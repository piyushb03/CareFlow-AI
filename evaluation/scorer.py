"""
CareFlow AI — Evaluation Scorer
Computes the Reviewer-Ready Score (0-100) and secondary metrics.
All scores based on actual system outputs vs gold-standard annotations.
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


SCORE_WEIGHTS = {
    "evidence_extraction": 0.20,    # Did it extract the right fields with evidence?
    "safety_signal_detection": 0.25, # Did it correctly identify safety signals?
    "evidence_attribution": 0.15,   # Did it cite correct turn numbers?
    "contradiction_detection": 0.15, # Did it find contradictions?
    "missing_info_detection": 0.15,  # Did it identify missing information?
    "unsupported_claim_avoidance": 0.10, # Did it avoid making things up?
}


def compute_reviewer_ready_score(
    system_output: Dict,
    gold: Dict,
    conversation_history: List[Dict],
) -> Dict[str, Any]:
    """
    Compute the Reviewer-Ready Score.
    Returns component scores and overall score (0-100).
    """
    scores = {}

    # ── Evidence Extraction (0-1) ────────────────────────────────────────────
    scores["evidence_extraction"] = _score_evidence_extraction(
        system_output.get("structured_areas", {}),
        gold.get("expected_fields", {}),
    )

    # ── Safety Signal Detection (0-1) ────────────────────────────────────────
    scores["safety_signal_detection"] = _score_safety_signals(
        system_output.get("signals", []) or _extract_signals(system_output),
        gold.get("expected_safety_signals", {}),
    )

    # ── Evidence Attribution (0-1) ───────────────────────────────────────────
    scores["evidence_attribution"] = _score_evidence_attribution(
        system_output,
        conversation_history,
        gold,
    )

    # ── Contradiction Detection (0-1) ─────────────────────────────────────────
    scores["contradiction_detection"] = _score_contradiction_detection(
        system_output.get("contradictions", []),
        gold.get("expected_contradictions", []),
    )

    # ── Missing Info Detection (0-1) ─────────────────────────────────────────
    scores["missing_info_detection"] = _score_missing_info(
        system_output.get("missing_information", []),
        gold.get("expected_missing_information", []),
    )

    # ── Unsupported Claim Avoidance (0-1) ────────────────────────────────────
    scores["unsupported_claim_avoidance"] = _score_unsupported_claims(
        system_output,
        conversation_history,
    )

    # ── Weighted Overall Score ───────────────────────────────────────────────
    weighted_total = sum(
        scores[component] * weight
        for component, weight in SCORE_WEIGHTS.items()
        if component in scores
    )
    overall_score = round(weighted_total * 100, 1)

