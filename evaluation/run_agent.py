"""
CareFlow AI — Run Agent Evaluation
Runs the full multi-agent pipeline on all synthetic evaluation cases.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

CASES_DIR = os.environ.get("EVAL_CASES_DIR", "evaluation/cases")
GOLD_DIR = os.environ.get("EVAL_GOLD_DIR", "evaluation/gold")
RESULTS_DIR = os.environ.get("EVAL_RESULTS_DIR", "evaluation/results")


def run_all_agent_cases() -> dict:
    """Run full multi-agent pipeline on all evaluation cases."""
    from evaluation.scorer import compute_reviewer_ready_score, compute_secondary_metrics
    from backend.services.agents.safety_agent import SafetySignalAgent
    from backend.services.agents.structuring_agent import StructuringAgent
    from backend.services.agents.verification_agent import VerificationAgent
    from backend.app import create_app

    app = create_app()
    app.app_context().push()

    os.makedirs(RESULTS_DIR, exist_ok=True)

    case_files = sorted([f for f in os.listdir(CASES_DIR) if f.endswith(".json")])

    results = []
    all_scores = []
    timing_data = []

    safety_agent = SafetySignalAgent()
    structuring_agent = StructuringAgent()
    verification_agent = VerificationAgent()

    for case_file in case_files:
        case_path = os.path.join(CASES_DIR, case_file)
        with open(case_path, "r") as f:
            case = json.load(f)

        case_id = case["id"]
        gold_file = os.path.join(GOLD_DIR, f"{case_id}_gold.json")
        gold = {}
        if os.path.exists(gold_file):
            with open(gold_file, "r") as f:
                gold = json.load(f)

        logger.info("Agent: Running case %s — %s", case_id, case.get("title", ""))
        t_start = time.time()

        # Run agents directly (without DB for eval mode)
        conv = case["conversation"]

        # Agent 2: Safety
        safety_result = safety_agent.run(case_id=case_id, conversation_history=conv)

        # Agent 3: Structuring
        structured_result = structuring_agent.run(case_id=case_id, conversation_history=conv)

        # Agent 4: Verification
        verification_result = verification_agent.run(
            case_id=case_id,
            conversation_history=conv,
            structured_summary=structured_result,
            safety_signals=safety_result,
        )

        # Build combined output for scoring
        combined_output = {
            **structured_result,
            "signals": safety_result.get("signals", []),
            "safety_signals": safety_result,
            "verification": verification_result,
        }

        duration = time.time() - t_start

        score_result = compute_reviewer_ready_score(
            system_output=combined_output,
            gold=gold,
            conversation_history=conv,
        )

        case_result = {
            "case_id": case_id,
            "title": case.get("title"),
            "difficulty": case.get("difficulty"),
            "method": "agent",
            "duration_seconds": duration,
            "overall_score": score_result["overall_score"],
            "component_scores": score_result["component_scores"],
            "verification_passed": verification_result.get("verification_passed"),
            "issues_count": len(verification_result.get("issues", [])),
            "structured_result": structured_result,
            "safety_result": safety_result,
            "verification_result": verification_result,
        }

        results.append(case_result)
        all_scores.append(score_result["overall_score"])
        timing_data.append({"duration_seconds": duration})

        result_file = os.path.join(RESULTS_DIR, f"{case_id}_agent.json")
        with open(result_file, "w") as f:
            json.dump(case_result, f, indent=2)

        logger.info("Agent %s: score=%.1f in %.1fs | verification=%s",
                    case_id, score_result["overall_score"], duration,
                    "passed" if verification_result.get("verification_passed") else "failed")

    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0

    summary = {
        "method": "agent",
        "run_at": datetime.utcnow().isoformat(),
        "cases_evaluated": len(results),
        "average_reviewer_ready_score": round(avg_score, 1),
        "individual_scores": {r["case_id"]: r["overall_score"] for r in results},
        "note": "Multi-agent pipeline with Safety, Structuring, Verification agents.",
    }

    with open(os.path.join(RESULTS_DIR, "agent_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("Agent evaluation complete. Average score: %.1f", avg_score)
    return summary


if __name__ == "__main__":
    results = run_all_agent_cases()
    print(json.dumps(results, indent=2))
