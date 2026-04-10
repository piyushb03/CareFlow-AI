"""
CareFlow AI — Triage Orchestrator (Agent 5)
Coordinates the complete workflow, manages case state, enforces verification loop,
and produces the final reviewer-ready intake brief.

IMPORTANT: The orchestrator does NOT make clinical decisions.
It only structures and prioritizes information for human review.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from backend.extensions import db
from backend.services.agents.safety_agent import SafetySignalAgent
from backend.services.agents.structuring_agent import StructuringAgent
from backend.services.agents.verification_agent import VerificationAgent
from backend.services.llm.client import get_llm_client

logger = logging.getLogger(__name__)

MAX_RETRIES = int(os.environ.get("MAX_AGENT_RETRIES", "3"))


class TriageOrchestrator:
    """
    Coordinates all agents, enforces verification loop (max 3 retries),
    and produces the final reviewer-ready brief.
    """

    def __init__(self):
        self.safety_agent = SafetySignalAgent()
        self.structuring_agent = StructuringAgent()
        self.verification_agent = VerificationAgent()
        self.llm = get_llm_client()

    def process_case(self, case_id: str) -> Dict[str, Any]:
        """
        Full processing pipeline for a completed intake conversation.
        1. Load conversation from DB
        2. Run Safety Signal Agent
        3. Run Structuring Agent
        4. Run Verification Agent (with retry loop)
        5. Produce final reviewer brief
        6. Update case in DB
        """
        from backend.models.case import Case
        from backend.models.conversation import ConversationTurn
        from backend.models.safety_signal import SafetySignal
        from backend.models.extracted_field import ExtractedField
        from backend.models.verification import VerificationIssue
        from backend.models.audit import AuditEvent

        case = Case.query.get(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Mark processing started
        case.status = "processing"
        case.processing_started_at = datetime.utcnow()
        db.session.commit()

        self._audit(case_id, "processing_started", "Orchestrator started case processing")

        # Load conversation
        turns = (
            ConversationTurn.query
            .filter_by(case_id=case_id)
            .order_by(ConversationTurn.turn_index)
            .all()
        )
        conversation_history = [t.to_dict() for t in turns]

        if not conversation_history:
            self._audit(case_id, "processing_failed", "No conversation turns found")
            case.status = "error"
            case.verification_status = "requires_human_review"
            db.session.commit()
            return {"error": "No conversation turns found", "case_id": case_id}

        trajectory = {
            "case_id": case_id,
            "started_at": datetime.utcnow().isoformat(),
            "steps": [],
        }

        # ── STEP 1: Safety Signal Agent ──────────────────────────────────────
        self._audit(case_id, "agent_started", "Safety Signal Agent starting")
        logger.info("Orchestrator: Running SafetySignalAgent for case %s", case_id)

        safety_result = self.safety_agent.run(case_id=case_id, conversation_history=conversation_history)
        trajectory["steps"].append({
            "step": 1,
            "agent": "safety_signal_agent",
            "status": "completed",
            "high_priority_signals": safety_result.get("high_priority_signals", []),
        })

        # Persist safety signals
        for sig in safety_result.get("signals", []):
            signal_record = SafetySignal(
                case_id=case_id,
                signal=sig.get("signal"),
                status=sig.get("status", "not_assessed"),
                evidence=sig.get("evidence"),
                source_turns_json=json.dumps(sig.get("source_turns", [])),
                confidence=sig.get("confidence"),
                uncertainty=sig.get("uncertainty"),
                requires_reviewer_attention=sig.get("requires_reviewer_attention", False),
            )
            db.session.add(signal_record)
        db.session.commit()

        # ── STEP 2: Structuring Agent ─────────────────────────────────────────
        self._audit(case_id, "agent_started", "Structuring Agent starting")
        logger.info("Orchestrator: Running StructuringAgent for case %s", case_id)

        structured_result = self.structuring_agent.run(
            case_id=case_id, conversation_history=conversation_history
        )
        trajectory["steps"].append({
            "step": 2,
            "agent": "structuring_agent",
            "status": "completed",
            "missing_information": structured_result.get("missing_information", []),
            "contradictions_count": len(structured_result.get("contradictions", [])),
        })

        # Persist extracted fields
        structured_areas = structured_result.get("structured_areas", {})
        for area_name, fields in structured_areas.items():
            if isinstance(fields, dict):
                for field_name, field_data in fields.items():
                    if isinstance(field_data, dict):
                        ef = ExtractedField(
                            case_id=case_id,
                            category=area_name,
                            field_name=field_name,
                            value=str(field_data.get("value")) if field_data.get("value") is not None else None,
                            status=field_data.get("status", "unknown"),
                            evidence=field_data.get("evidence"),
                            source_turns_json=json.dumps(field_data.get("source_turns", [])),
                            confidence=field_data.get("confidence"),
                        )
                        db.session.add(ef)
        db.session.commit()

        # ── STEP 3: Verification Loop (max MAX_RETRIES) ───────────────────────
        verification_passed = False
        retry_count = 0
        current_structured = structured_result
        verification_result = None

        while retry_count < MAX_RETRIES:
            self._audit(
                case_id,
                "agent_started",
                f"Verification Agent starting (attempt {retry_count + 1}/{MAX_RETRIES})",
            )
            logger.info(
                "Orchestrator: Running VerificationAgent for case %s (attempt %d)",
                case_id, retry_count + 1,
            )

            verification_result = self.verification_agent.run(
                case_id=case_id,
                conversation_history=conversation_history,
                structured_summary=current_structured,
                safety_signals=safety_result,
            )

            trajectory["steps"].append({
                "step": 3 + retry_count,
                "agent": "verification_agent",
                "attempt": retry_count + 1,
                "verification_passed": verification_result.get("verification_passed"),
                "issues_count": len(verification_result.get("issues", [])),
                "revision_required": verification_result.get("revision_required", False),
            })

            # Persist issues
            for issue in verification_result.get("issues", []):
                vi = VerificationIssue(
                    case_id=case_id,
                    issue_type=issue.get("type", "other"),
                    severity=issue.get("severity", "medium"),
                    description=issue.get("description", ""),
                    evidence=issue.get("evidence"),
                    source_turns_json=json.dumps(issue.get("source_turns", [])),
                    recommended_fix=issue.get("recommended_fix"),
                )
                db.session.add(vi)
            db.session.commit()

            if verification_result.get("verification_passed"):
                verification_passed = True
                self._audit(case_id, "verification_passed", f"Verification passed on attempt {retry_count + 1}")
                break
            else:
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    # Attempt revision
                    self._audit(
                        case_id,
                        "verification_failed",
                        f"Verification failed on attempt {retry_count}. Requesting revision.",
                    )
                    revision_instructions = verification_result.get("revision_instructions", "")
                    current_structured = self._request_revision(
                        case_id, current_structured, verification_result, conversation_history, revision_instructions
                    )
                    trajectory["steps"].append({
                        "step": f"revision_{retry_count}",
                        "agent": "structuring_agent",
                        "action": "revision",
                        "attempt": retry_count,
                        "revision_instructions": revision_instructions[:200],
                    })

        # ── STEP 4: Produce Final Brief ───────────────────────────────────────
        final_brief = self._build_reviewer_brief(
            case_id=case_id,
            conversation_history=conversation_history,
            structured_result=current_structured,
            safety_result=safety_result,
            verification_result=verification_result,
            verification_passed=verification_passed,
            retry_count=retry_count,
        )

        # Determine final verification status
        if verification_passed:
            verification_status = "passed"
        elif retry_count >= MAX_RETRIES:
            verification_status = "requires_human_review"
            self._audit(
                case_id,
                "human_review_required",
                f"Verification failed after {MAX_RETRIES} attempts. Escalating to human review.",
            )
        else:
            verification_status = "failed"

        # Persist final outputs
        case.status = "ready_for_review"
        case.processing_completed_at = datetime.utcnow()
        case.verification_status = verification_status
        case.structured_summary_json = json.dumps(current_structured)
        case.safety_signals_json = json.dumps(safety_result)
        case.reviewer_brief_json = json.dumps(final_brief)
        db.session.commit()

        # Save trajectory
        trajectory["completed_at"] = datetime.utcnow().isoformat()
        trajectory["verification_status"] = verification_status
        trajectory["retry_count"] = retry_count
        self._save_trajectory(case_id, trajectory)

        self._audit(case_id, "processing_completed", f"Case processing complete. Status: {verification_status}")
        logger.info("Orchestrator: Case %s complete. Status: %s", case_id, verification_status)

        return {
            "case_id": case_id,
            "status": "ready_for_review",
            "verification_status": verification_status,
            "reviewer_brief": final_brief,
        }

    def _request_revision(
        self,
        case_id: str,
        current_structured: Dict,
        verification_result: Dict,
        conversation_history: List[Dict],
        revision_instructions: str,
    ) -> Dict:
        """
        Ask the structuring agent to revise its output based on verification feedback.
        """
        system_prompt = self.structuring_agent.load_prompt()
        history_text = self.structuring_agent._format_history(conversation_history)
        issues_text = json.dumps(verification_result.get("issues", []), indent=2)

        messages = [
            {
                "role": "user",
                "content": f"""The verification agent found the following issues with your previous structured summary.
Please revise the summary to fix these issues.

ORIGINAL CONVERSATION:
{history_text}

VERIFICATION ISSUES:
{issues_text}

REVISION INSTRUCTIONS:
{revision_instructions}

PREVIOUS STRUCTURED SUMMARY (to be corrected):
{json.dumps(current_structured, indent=2)}

Provide a corrected structured summary in the same JSON format.
Fix all identified issues. Do not introduce new unsupported claims.""",
            }
        ]

        try:
            result = self.llm.complete_json(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=4096,
            )
            return result
        except Exception as e:
            logger.error("Orchestrator revision request failed: %s", e)
            return current_structured  # Return unchanged if revision fails

    def _build_reviewer_brief(
        self,
        case_id: str,
        conversation_history: List[Dict],
        structured_result: Dict,
        safety_result: Dict,
        verification_result: Optional[Dict],
        verification_passed: bool,
        retry_count: int,
    ) -> Dict:
        """
        Produce the final structured reviewer brief.
        This is the primary deliverable — reviewer-ready, evidence-grounded.
        """
        # Compute reviewer priority
        high_priority_signals = safety_result.get("high_priority_signals", [])
        contradictions = structured_result.get("contradictions", [])
        missing_fields = structured_result.get("missing_information", [])
        issues = verification_result.get("issues", []) if verification_result else []
        high_sev_issues = [i for i in issues if i.get("severity") == "high"]

