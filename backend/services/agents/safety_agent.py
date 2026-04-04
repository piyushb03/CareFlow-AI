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
            }
        ]

        run = self._create_agent_run(case_id, f"Safety analysis: {len(conversation_history)} turns")
        try:
            result = self.llm.complete_json(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=3000,
            )
            self._complete_agent_run(run, result)
            self._log_audit(
                case_id,
                "agent_completed",
                f"Safety Signal Agent completed. High priority: {result.get('high_priority_signals', [])}",
                {"high_priority_signals": result.get("high_priority_signals", [])},
            )
            return result
        except Exception as e:
            self._complete_agent_run(run, {}, error=str(e))
            logger.error("SafetySignalAgent.run failed: %s", e)
            # Return a safe fallback — all signals marked not_assessed
            return self._fallback_response(str(e))

    def _fallback_response(self, error_msg: str) -> Dict:
        signals = []
        for signal_name in ALL_SIGNAL_NAMES:
            signals.append({
                "signal": signal_name,
                "status": "not_assessed",
                "evidence": "not established — agent error",
                "source_turns": [],
                "confidence": 0.0,
                "uncertainty": f"Agent failed to complete analysis: {error_msg}",
                "requires_reviewer_attention": True,
            })
        return {
            "signals": signals,
            "overall_safety_summary": "Safety analysis incomplete due to system error. Requires full human review.",
            "high_priority_signals": [],
            "assessment_limitations": f"System error: {error_msg}",
        }

    def _format_history(self, history: List[Dict]) -> str:
        lines = []
        for turn in history:
            idx = turn.get("turn_index", "?")
            role = turn.get("role", "unknown").upper()
            content = turn.get("content", "")
            lines.append(f"[Turn {idx}] {role}: {content}")
        return "\n".join(lines) if lines else "(empty conversation)"
