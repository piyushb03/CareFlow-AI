"""
CareFlow AI — Safety Signal Extractor (Agent 2)
Identifies predefined safety-relevant signals in conversation.
IMPORTANT: Produces signals for reviewer attention — NOT diagnoses.
"""

import json
import logging
from typing import Dict, Any, List

from backend.services.agents.base import AgentBase
from backend.schemas.safety_taxonomy import ALL_SIGNAL_NAMES, SAFETY_SIGNALS

logger = logging.getLogger(__name__)


class SafetySignalAgent(AgentBase):
    name = "safety_signal_agent"
    prompt_file = "safety_agent.md"
    prompt_version = "v1.0"

    def run(self, case_id: str, conversation_history: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Analyze conversation for safety-relevant signals.
        Returns structured JSON with signal status, evidence, and confidence.
        """
        system_prompt = self.load_prompt()
        history_text = self._format_history(conversation_history)
        taxonomy_text = json.dumps(
            {k: v["description"] for k, v in SAFETY_SIGNALS.items()}, indent=2
        )

        messages = [
            {
                "role": "user",
                "content": f"""Analyze the following intake conversation for safety-relevant signals.

CONVERSATION:
{history_text}

SIGNAL TAXONOMY:
{taxonomy_text}

For EACH of the following signals, provide a structured assessment:
{json.dumps(ALL_SIGNAL_NAMES)}

CRITICAL RULES:
- Never infer absence from silence. If not mentioned, status = "not_assessed"
- Use exact quotes from the conversation as evidence
- Never claim a signal is absent unless explicitly stated
- Never use clinical diagnostic language
- If evidence is indirect, lower confidence and note uncertainty

Respond with JSON:
{{
  "signals": [
    {{
      "signal": "signal_name",
      "status": "present|absent|unclear|not_assessed",
      "evidence": "exact quote from conversation OR 'not established'",
      "source_turns": [1, 4],
      "confidence": 0.0,
      "uncertainty": "description of what is unclear",
      "requires_reviewer_attention": true
    }}
  ],
  "overall_safety_summary": "brief factual summary for reviewer — no diagnostic language",
  "high_priority_signals": ["signal_name1"],
  "assessment_limitations": "what was not established"
}}""",
