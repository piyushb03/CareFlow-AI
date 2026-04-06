"""
CareFlow AI — Clinical Structuring Agent (Agent 3)
Converts unstructured conversation into structured intake representation.
Every field distinguishes: explicit | inferred | unknown | contradictory.
Never fabricates values.
"""

import json
import logging
from typing import Dict, Any, List

from backend.services.agents.base import AgentBase
from backend.schemas.intake_schema import INTAKE_AREAS

logger = logging.getLogger(__name__)

FIELD_SCHEMA_EXAMPLE = {
    "value": "reported value or null",
    "status": "explicit|inferred|unknown|contradictory",
    "evidence": "exact quote from conversation or null",
    "source_turns": [1, 3],
    "confidence": 0.9,
}


class StructuringAgent(AgentBase):
    name = "structuring_agent"
    prompt_file = "structuring_agent.md"
    prompt_version = "v1.0"

    def run(self, case_id: str, conversation_history: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Convert conversation into fully structured intake representation.
        All fields annotated with status and evidence.
        """
        system_prompt = self.load_prompt()
        history_text = self._format_history(conversation_history)
        schema_text = json.dumps(
            {a["area"]: a["fields"] for a in INTAKE_AREAS}, indent=2
        )

        messages = [
            {
                "role": "user",
                "content": f"""Convert the following intake conversation into a structured representation.

CONVERSATION:
{history_text}

INTAKE SCHEMA (areas and fields to extract):
{schema_text}

CRITICAL RULES:
1. Never fabricate a value. If not stated, status = "unknown", value = null
2. Use exact quotes as evidence
3. Distinguish explicitly stated (status="explicit") from your inference (status="inferred")
4. Mark contradictory information as status="contradictory" with both values in evidence
5. Never diagnose or make clinical conclusions
6. Lower confidence for inferred values

For each intake area, structure the output as:
{{
  "area_name": {{
    "field_name": {{
      "value": "...",
      "status": "explicit|inferred|unknown|contradictory",
      "evidence": "exact quote or null",
      "source_turns": [1, 3],
      "confidence": 0.9
    }}
  }}
}}

Also include:
{{
