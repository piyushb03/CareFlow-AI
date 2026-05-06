"""
CareFlow AI — Run Baseline Evaluation
Runs the single-prompt baseline on all synthetic evaluation cases.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from baseline.baseline_agent import run_baseline
from evaluation.scorer import compute_reviewer_ready_score, compute_secondary_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

CASES_DIR = os.environ.get("EVAL_CASES_DIR", "evaluation/cases")
GOLD_DIR = os.environ.get("EVAL_GOLD_DIR", "evaluation/gold")
RESULTS_DIR = os.environ.get("EVAL_RESULTS_DIR", "evaluation/results")


def load_case(case_file: str) -> dict:
    with open(case_file, "r") as f:
        return json.load(f)


def load_gold(case_id: str) -> dict:
    gold_file = os.path.join(GOLD_DIR, f"{case_id}_gold.json")
    if os.path.exists(gold_file):
        with open(gold_file, "r") as f:
            return json.load(f)
    return {}


def run_all_baseline_cases() -> dict:
    """Run baseline on all evaluation cases and compute scores."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

    case_files = sorted([
        f for f in os.listdir(CASES_DIR)
        if f.endswith(".json")
    ])

    results = []
    all_scores = []
    timing_data = []

    for case_file in case_files:
        case_path = os.path.join(CASES_DIR, case_file)
        case = load_case(case_path)
        case_id = case["id"]
        gold = load_gold(case_id)

        logger.info("Baseline: Running case %s — %s", case_id, case.get("title", ""))

        t_start = time.time()
        baseline_output = run_baseline(case["conversation"])
        duration = time.time() - t_start

        # For baseline: parse the text output into minimal structure for scoring
        # Baseline produces free text, not structured JSON — this is the key limitation
        structured_for_scoring = {
            "structured_areas": {},  # Baseline has no structured extraction
            "contradictions": [],    # Baseline has no contradiction detection
            "missing_information": [], # Baseline has no missing info detection
            "signals": [],           # Baseline has no safety taxonomy
            "_raw_text": baseline_output.get("summary_text", ""),
        }

        score_result = compute_reviewer_ready_score(
            system_output=structured_for_scoring,
            gold=gold,
            conversation_history=case["conversation"],
        )

        case_result = {
            "case_id": case_id,
            "title": case.get("title"),
            "difficulty": case.get("difficulty"),
            "method": "baseline",
            "duration_seconds": duration,
            "overall_score": score_result["overall_score"],
            "component_scores": score_result["component_scores"],
            "baseline_output": baseline_output,
        }

        results.append(case_result)
        all_scores.append(score_result["overall_score"])
        timing_data.append({"duration_seconds": duration})

        # Save per-case result
        result_file = os.path.join(RESULTS_DIR, f"{case_id}_baseline.json")
        with open(result_file, "w") as f:
            json.dump(case_result, f, indent=2)

        logger.info("Baseline %s: score=%.1f in %.1fs", case_id, score_result["overall_score"], duration)

    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    secondary = compute_secondary_metrics(
        [r["baseline_output"] for r in results],
        [load_gold(r["case_id"]) for r in results],
        timing_data,
    )

    summary = {
        "method": "baseline",
        "run_at": datetime.utcnow().isoformat(),
        "cases_evaluated": len(results),
        "average_reviewer_ready_score": round(avg_score, 1),
        "individual_scores": {r["case_id"]: r["overall_score"] for r in results},
        "secondary_metrics": secondary,
        "note": "Baseline uses single-prompt with no structured agents, verification, or evidence attribution.",
    }

    # Save summary
    summary_file = os.path.join(RESULTS_DIR, "baseline_summary.json")
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("Baseline evaluation complete. Average score: %.1f", avg_score)
    return summary


if __name__ == "__main__":
    results = run_all_baseline_cases()
    print(json.dumps(results, indent=2))
