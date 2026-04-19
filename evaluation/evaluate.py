"""
CareFlow AI — Evaluation Comparison
Compares baseline vs agent performance and produces the comparison table.
"""

import os
import sys
import json
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

RESULTS_DIR = os.environ.get("EVAL_RESULTS_DIR", "evaluation/results")


def evaluate():
    """Compare baseline vs agent and produce final evaluation report."""
    baseline_file = os.path.join(RESULTS_DIR, "baseline_summary.json")
    agent_file = os.path.join(RESULTS_DIR, "agent_summary.json")

    if not os.path.exists(baseline_file):
        logger.error("Baseline results not found. Run: python -m evaluation.run_baseline first")
        return None

    if not os.path.exists(agent_file):
        logger.error("Agent results not found. Run: python -m evaluation.run_agent first")
        return None

    with open(baseline_file) as f:
        baseline = json.load(f)
    with open(agent_file) as f:
        agent = json.load(f)

    baseline_avg = baseline.get("average_reviewer_ready_score", 0)
    agent_avg = agent.get("average_reviewer_ready_score", 0)
    improvement = agent_avg - baseline_avg

    # Per-case comparison
    per_case = []
    for case_id in agent.get("individual_scores", {}):
        b_score = baseline.get("individual_scores", {}).get(case_id, 0)
        a_score = agent.get("individual_scores", {}).get(case_id, 0)
        per_case.append({
            "case_id": case_id,
            "baseline_score": b_score,
            "agent_score": a_score,
            "delta": round(a_score - b_score, 1),
        })

    comparison = {
        "evaluation_date": datetime.utcnow().isoformat(),
        "summary": {
            "baseline_avg_score": baseline_avg,
            "agent_avg_score": agent_avg,
            "improvement": round(improvement, 1),
            "improvement_pct": round((improvement / max(baseline_avg, 1)) * 100, 1),
        },
        "per_case_comparison": per_case,
        "metric_table": [
            {
                "metric": "Reviewer-Ready Score (avg)",
