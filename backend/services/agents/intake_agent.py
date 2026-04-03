"""
CareFlow AI — Intake Interviewer Agent (Agent 1)
Conducts the real-time intake conversation.
Dynamically chooses the next best question based on missing information.
"""

import json
import logging
from typing import Dict, Any, List, Optional

from backend.services.agents.base import AgentBase
from backend.schemas.intake_schema import INTAKE_AREAS, REQUIRED_AREAS, ALL_AREAS

logger = logging.getLogger(__name__)


class IntakeAgent(AgentBase):
    name = "intake_agent"
    prompt_file = "intake_agent.md"
    prompt_version = "v1.0"

    def get_next_question(
        self,
        case_id: str,
        conversation_history: List[Dict],
        collected_fields: Dict,
        missing_areas: List[str],
    ) -> Dict[str, Any]:
        """
        Given conversation history and collected fields so far,
        determine the single best next question to ask.
        Returns: {"question": str, "area": str, "rationale": str, "is_complete": bool}
        """
        system_prompt = self.load_prompt()

        # Build context summary
        collected_summary = json.dumps(collected_fields, indent=2) if collected_fields else "{}"
        history_text = self._format_history(conversation_history)
        missing_text = ", ".join(missing_areas) if missing_areas else "none"

        messages = [
            {
                "role": "user",
                "content": f"""Current conversation:
{history_text}

Collected information so far:
{collected_summary}

Missing required areas: {missing_text}

Determine the single best next question to ask, or indicate the interview is complete.

Respond with JSON:
{{
  "question": "the exact question to ask the patient",
  "area": "intake_area_name",
  "rationale": "why this question now",
  "is_complete": false,
  "missing_areas_remaining": ["area1", "area2"]
}}

If enough information has been collected across all required areas, set is_complete to true and question to null.""",
            }
        ]

        run = self._create_agent_run(case_id, f"Next question for areas: {missing_text}")
        try:
            result = self.llm.complete_json(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=1024,
            )
            self._complete_agent_run(run, result)
            return result
        except Exception as e:
            self._complete_agent_run(run, {}, error=str(e))
            logger.error("IntakeAgent.get_next_question failed: %s", e)
            return {
                "question": "Could you tell me more about what brought you here today?",
                "area": "presenting_concern",
                "rationale": "fallback question after agent error",
                "is_complete": False,
                "missing_areas_remaining": missing_areas,
            }

    def assess_completeness(
        self,
        conversation_history: List[Dict],
        collected_fields: Dict,
    ) -> Dict[str, Any]:
        """
        Assess which intake areas have been sufficiently covered and which are missing.
        Returns structured coverage report.
        """
        system_prompt = self.load_prompt()
        history_text = self._format_history(conversation_history)

        messages = [
            {
                "role": "user",
                "content": f"""Review the intake conversation and identify coverage.

Conversation:
{history_text}

For each intake area below, assess whether sufficient information was collected:
{json.dumps(ALL_AREAS)}

Respond with JSON:
{{
  "covered_areas": ["area1", "area2"],
  "missing_required_areas": ["area3"],
  "missing_optional_areas": ["area4"],
  "partial_areas": ["area5"],
  "collected_fields": {{
    "field_name": {{
      "value": "...",
      "turn_index": 3,
      "confidence": 0.9
    }}
  }},
  "ready_for_processing": true
}}""",
            }
        ]

        run = self._create_agent_run(case_id="assessment", input_summary="completeness assessment")
        try:
            result = self.llm.complete_json(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=2048,
            )
            self._complete_agent_run(run, result)
            return result
        except Exception as e:
            self._complete_agent_run(run, {}, error=str(e))
            logger.error("IntakeAgent.assess_completeness failed: %s", e)
            return {"covered_areas": [], "missing_required_areas": REQUIRED_AREAS, "ready_for_processing": False}

    def run(self, case_id: str, conversation_history: List[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Full run mode: assess completeness of an existing conversation."""
        conv = conversation_history or []
        collected = kwargs.get("collected_fields", {})
        return self.assess_completeness(conv, collected)

    def _format_history(self, history: List[Dict]) -> str:
        lines = []
        for turn in history:
            idx = turn.get("turn_index", "?")
            role = turn.get("role", "unknown").upper()
            content = turn.get("content", "")
            lines.append(f"[Turn {idx}] {role}: {content}")
        return "\n".join(lines) if lines else "(no conversation yet)"
