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
