"""
CareFlow AI — Baseline Agent
Single-prompt, no specialized agents, no verification, no evidence attribution.
This is the fair comparison baseline for the evaluation.
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

BASELINE_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "baseline_prompt.md")


def load_baseline_prompt() -> str:
    with open(BASELINE_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def run_baseline(conversation_history: List[Dict]) -> Dict[str, Any]:
    """
    Single-prompt baseline: one LLM call, no agents, no verification.
    Returns structured summary.
    """
    from backend.services.llm.client import get_llm_client

    llm = get_llm_client()
    system_prompt = load_baseline_prompt()

    # Format conversation
    history_text = ""
    for turn in conversation_history:
        idx = turn.get("turn_index", "?")
        role = turn.get("role", "unknown").upper()
        content = turn.get("content", "")
        history_text += f"[Turn {idx}] {role}: {content}\n"

    messages = [
        {
            "role": "user",
            "content": f"""Please summarize the following intake conversation:

CONVERSATION:
{history_text}

Provide a structured summary for clinical reviewer.""",
        }
    ]

    t_start = time.time()
    try:
        response = llm.complete(
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=2000,
        )
        duration = time.time() - t_start

        return {
            "method": "baseline",
            "prompt_version": "v1.0",
            "model": response.model,
            "summary_text": response.content,
            "duration_seconds": duration,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "generated_at": datetime.utcnow().isoformat(),
            # Baseline has none of these:
            "has_evidence_attribution": False,
            "has_verification": False,
            "has_contradiction_detection": False,
            "has_safety_taxonomy": False,
            "has_structured_fields": False,
        }
    except Exception as e:
        logger.error("Baseline agent failed: %s", e)
        return {
            "method": "baseline",
            "error": str(e),
            "duration_seconds": time.time() - t_start,
        }
