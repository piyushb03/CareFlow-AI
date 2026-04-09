"""
CareFlow AI — Verification Agent (Agent 4)
Catches errors before they reach the human reviewer.
Can reject or request revision of intermediate results.
"""

import json
import logging
from typing import Dict, Any, List, Optional

from backend.services.agents.base import AgentBase

logger = logging.getLogger(__name__)


class VerificationAgent(AgentBase):
    name = "verification_agent"
    prompt_file = "verification_agent.md"
    prompt_version = "v1.0"

    def run(
        self,
        case_id: str,
        conversation_history: List[Dict],
        structured_summary: Dict,
        safety_signals: Dict,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Verify the structured summary and safety signals against the original conversation.
        Returns verification result with list of issues.
        """
        system_prompt = self.load_prompt()
        history_text = self._format_history(conversation_history)
        summary_text = json.dumps(structured_summary, indent=2)
        signals_text = json.dumps(safety_signals, indent=2)

        messages = [
            {
                "role": "user",
                "content": f"""Verify the following structured intake summary against the original conversation.

ORIGINAL CONVERSATION:
{history_text}

STRUCTURED SUMMARY:
{summary_text}

SAFETY SIGNALS:
{signals_text}

Check for ALL of the following:
1. Unsupported claims — values stated as fact that have no evidence in the conversation
2. Hallucinated information — information not present in the conversation
3. Contradictions — internal contradictions within the summary
4. Missing important information — important information from conversation not captured
5. Evidence misattribution — evidence quotes that don't match the cited turn
6. Overconfident language — high confidence assigned to inferred or unclear information
7. Safety signal inconsistencies — signals that conflict with conversation content
8. Summary vs conversation mismatches — summary that misrepresents conversation

For each issue found, create:
{{
  "type": "unsupported_claim|contradiction|missing_information|evidence_mismatch|overconfidence|safety_inconsistency|other",
  "severity": "low|medium|high",
  "description": "specific description of the problem",
  "evidence": "relevant quote from conversation",
  "source_turns": [1, 3],
  "recommended_fix": "specific recommended correction"
}}

Respond with JSON:
{{
  "verification_passed": true,
  "issues": [],
  "high_severity_count": 0,
  "medium_severity_count": 0,
  "low_severity_count": 0,
  "overall_quality": "high|medium|low",
  "revision_required": false,
  "revision_instructions": "specific instructions for revision if needed",
  "verifier_notes": "general notes for reviewer"
}}

verification_passed = true only if there are NO high-severity issues.
revision_required = true if any medium or high severity issues found.""",
            }
        ]

        run = self._create_agent_run(case_id, "Verification of structured summary and safety signals")
        try:
            result = self.llm.complete_json(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=3000,
            )
            self._complete_agent_run(run, result, verification_result="passed" if result.get("verification_passed") else "failed")
            self._log_audit(
                case_id,
                "verification_passed" if result.get("verification_passed") else "verification_failed",
                f"Verification: {len(result.get('issues', []))} issues found",
                {
                    "issues_count": len(result.get("issues", [])),
                    "high_severity": result.get("high_severity_count", 0),
                    "revision_required": result.get("revision_required", False),
                },
            )
            return result
        except Exception as e:
            self._complete_agent_run(run, {}, error=str(e))
            logger.error("VerificationAgent.run failed: %s", e)
            return {
                "verification_passed": False,
                "issues": [{
                    "type": "other",
                    "severity": "high",
                    "description": f"Verification agent failed: {str(e)}",
                    "evidence": None,
                    "source_turns": [],
                    "recommended_fix": "Manual verification required",
                }],
                "high_severity_count": 1,
                "medium_severity_count": 0,
                "low_severity_count": 0,
                "overall_quality": "low",
                "revision_required": True,
                "revision_instructions": "Complete re-verification required",
                "verifier_notes": f"Agent error: {str(e)}",
            }

    def _format_history(self, history: List[Dict]) -> str:
        lines = []
        for turn in history:
            idx = turn.get("turn_index", "?")
            role = turn.get("role", "unknown").upper()
            content = turn.get("content", "")
            lines.append(f"[Turn {idx}] {role}: {content}")
        return "\n".join(lines) if lines else "(empty conversation)"
