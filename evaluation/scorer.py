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

    return {
        "overall_score": overall_score,
        "component_scores": {k: round(v * 100, 1) for k, v in scores.items()},
        "weights": SCORE_WEIGHTS,
        "max_score": 100,
        "interpretation": _interpret_score(overall_score),
    }


def _extract_signals(system_output: Dict) -> List[Dict]:
    """Extract signals from various output formats."""
    # Try different locations in output structure
    if "safety_signals" in system_output:
        s = system_output["safety_signals"]
        if isinstance(s, dict) and "signals" in s:
            return s["signals"]
        if isinstance(s, list):
            return s
    return []


def _score_evidence_extraction(structured_areas: Dict, expected_fields: Dict) -> float:
    """
    Check how many expected fields were extracted with correct values and status.
    """
    if not expected_fields:
        return 1.0  # No fields to check — perfect by default

    correct = 0
    total = len(expected_fields)

    for field_path, expected in expected_fields.items():
        parts = field_path.split(".")
        if len(parts) != 2:
            continue
        area, field = parts

        area_data = structured_areas.get(area, {})
        field_data = area_data.get(field, {})

        if not field_data or field_data.get("value") is None:
            # Field missing — partial credit if at least acknowledged
            continue

        # Value present: check status matches
        expected_status = expected.get("status", "explicit")
        actual_status = field_data.get("status", "unknown")

        if actual_status != "unknown" and actual_status != "contradictory":
            correct += 0.5  # Field found

        # Bonus for correct status attribution
        if actual_status == expected_status:
            correct += 0.3

        # Bonus for having evidence
        if field_data.get("evidence"):
            correct += 0.2

    return min(1.0, correct / total) if total > 0 else 1.0


def _score_safety_signals(signals: List[Dict], expected_signals: Dict) -> float:
    """
    Check safety signal detection accuracy.
    High recall for critical signals is most important.
    """
    if not expected_signals:
        return 1.0

    signal_map = {s["signal"]: s for s in signals}
    correct = 0
    total = len(expected_signals)

    for signal_name, expected_status in expected_signals.items():
        actual = signal_map.get(signal_name)
        if not actual:
            # Signal not assessed at all
            continue

        actual_status = actual.get("status", "not_assessed")

        if actual_status == expected_status:
            correct += 1.0
        elif actual_status == "unclear" and expected_status in ("present", "absent"):
            # Unclear is better than wrong
            correct += 0.5
        elif actual_status == "not_assessed" and expected_status != "not_assessed":
            # Failed to assess something important
            correct += 0.2

    # Critical signals penalty — must not miss present signals
    critical_signals = [s for s, status in expected_signals.items() if status == "present"]
    for cs in critical_signals:
        actual = signal_map.get(cs)
        if actual:
            if actual.get("status") == "absent":
                correct -= 0.5  # Calling present signal absent is a serious error

    return max(0.0, min(1.0, correct / total)) if total > 0 else 1.0


def _score_evidence_attribution(system_output: Dict, conversation: List[Dict], gold: Dict) -> float:
    """
    Check that cited turn numbers are valid and evidence quotes exist in conversation.
    """
    # Build turn content map
    turn_content = {t["turn_index"]: t["content"] for t in conversation}
    total_checks = 0
    valid_citations = 0

    def check_citations(obj):
        nonlocal total_checks, valid_citations
        if isinstance(obj, dict):
            source_turns = obj.get("source_turns", [])
            evidence = obj.get("evidence")
            if source_turns:
                total_checks += 1
                all_valid = all(t in turn_content for t in source_turns)
                if all_valid:
                    valid_citations += 1
            for v in obj.values():
                check_citations(v)
        elif isinstance(obj, list):
            for item in obj:
                check_citations(item)

    check_citations(system_output)

    if total_checks == 0:
        # No citations at all — penalize
        return 0.3

    return valid_citations / total_checks


def _score_contradiction_detection(detected: List, expected: List) -> float:
    """Check if known contradictions were detected."""
    if not expected:
        # No contradictions expected — penalize false positives
        if detected:
            return max(0.5, 1.0 - 0.1 * len(detected))
        return 1.0

    # Partial credit for finding any contradictions
    if not detected and expected:
        return 0.0

    # Credit for proportion found (approximately)
    detection_rate = min(1.0, len(detected) / max(1, len(expected)))
    return detection_rate


def _score_missing_info(detected_missing: List, expected_missing: List) -> float:
    """Check if known missing information was identified."""
    if not expected_missing:
        return 1.0

    if not detected_missing:
        return 0.0

    # Check overlap (flexible string matching)
    detected_lower = [str(d).lower() for d in detected_missing]
    found = 0
    for exp in expected_missing:
        exp_lower = exp.lower()
        # Check if any detected item mentions relevant keywords
        keywords = exp_lower.split(".")[-1].split("_")
        for detected in detected_lower:
            if any(kw in detected for kw in keywords if len(kw) > 3):
                found += 1
                break

    return min(1.0, found / len(expected_missing))


def _score_unsupported_claims(system_output: Dict, conversation: List[Dict]) -> float:
    """
    Penalize claims that appear fabricated (not traceable to conversation).
    Simple heuristic: check that inferred fields have evidence text.
    """
    total_inferred = 0
    inferred_with_evidence = 0

    def check_fields(obj):
        nonlocal total_inferred, inferred_with_evidence
        if isinstance(obj, dict):
            status = obj.get("status")
            if status == "inferred":
                total_inferred += 1
                if obj.get("evidence") and len(obj.get("evidence", "")) > 5:
                    inferred_with_evidence += 1
            for v in obj.values():
                check_fields(v)
        elif isinstance(obj, list):
            for item in obj:
                check_fields(item)

    check_fields(system_output)

    if total_inferred == 0:
        return 1.0  # No inferred claims — safe

    # Penalize inferred claims without evidence
    evidence_rate = inferred_with_evidence / total_inferred
    return 0.5 + (0.5 * evidence_rate)


def _interpret_score(score: float) -> str:
    if score >= 85:
        return "High quality — reviewer-ready with minor gaps"
    elif score >= 70:
        return "Good quality — some areas need reviewer attention"
    elif score >= 55:
        return "Moderate quality — multiple areas require careful review"
    else:
        return "Low quality — significant issues detected, full reviewer rework needed"


def compute_secondary_metrics(
    system_outputs: List[Dict],
    gold_cases: List[Dict],
    timing_data: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Compute secondary evaluation metrics across all cases."""
    if not system_outputs:
        return {}

    # Critical signal recall
    critical_recalls = []
    for output, gold in zip(system_outputs, gold_cases):
        critical = [s for s, status in gold.get("expected_safety_signals", {}).items() if status == "present"]
        if not critical:
            continue
        signals = _extract_signals(output)
        signal_map = {s["signal"]: s for s in signals}
        recalled = sum(1 for cs in critical if signal_map.get(cs, {}).get("status") == "present")
        if critical:
            critical_recalls.append(recalled / len(critical))

    metrics = {
        "critical_signal_recall": round(sum(critical_recalls) / len(critical_recalls) * 100, 1) if critical_recalls else None,
        "cases_evaluated": len(system_outputs),
    }

    if timing_data:
        durations = [t.get("duration_seconds") for t in timing_data if t.get("duration_seconds")]
        if durations:
            metrics["avg_processing_time_seconds"] = round(sum(durations) / len(durations), 1)
            metrics["max_processing_time_seconds"] = max(durations)

    return metrics
