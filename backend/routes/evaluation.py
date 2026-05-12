"""
CareFlow AI — Evaluation Routes
"""

import os
import json
import logging
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)
evaluation_bp = Blueprint("evaluation", __name__)


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@evaluation_bp.route("/evaluation/run", methods=["POST"])
def run_evaluation():
    """Trigger a full evaluation run on synthetic cases."""
    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "agent")  # "agent" | "baseline"

    try:
        if mode == "baseline":
            from evaluation.run_baseline import run_all_baseline_cases
            results = run_all_baseline_cases()
        else:
            from evaluation.run_agent import run_all_agent_cases
            results = run_all_agent_cases()

        return jsonify({"status": "completed", "results": results})
    except Exception as e:
        logger.error("Evaluation run failed: %s", e)
        return _error(f"Evaluation failed: {str(e)}", 500)


@evaluation_bp.route("/evaluation/results", methods=["GET"])
def get_evaluation_results():
    """Get latest evaluation results."""
    results_dir = os.environ.get("EVAL_RESULTS_DIR", "evaluation/results")
    results_file = os.path.join(results_dir, "latest_results.json")

    if not os.path.exists(results_file):
        return _error("No evaluation results found. Run evaluation first.", 404)

    with open(results_file, "r") as f:
        results = json.load(f)
    return jsonify(results)


@evaluation_bp.route("/evaluation/case/<eval_case_id>", methods=["GET"])
def get_evaluation_case(eval_case_id):
    """Get evaluation results for a specific case."""
    results_dir = os.environ.get("EVAL_RESULTS_DIR", "evaluation/results")
    case_file = os.path.join(results_dir, f"{eval_case_id}.json")

    if not os.path.exists(case_file):
        return _error(f"Evaluation case {eval_case_id} not found", 404)

    with open(case_file, "r") as f:
        result = json.load(f)
    return jsonify(result)


@evaluation_bp.route("/evaluation/cases", methods=["GET"])
def list_evaluation_cases():
    """List all synthetic evaluation cases."""
    cases_dir = os.environ.get("EVAL_CASES_DIR", "evaluation/cases")
    if not os.path.exists(cases_dir):
        return jsonify({"cases": [], "message": "No evaluation cases found"})

    cases = []
    for fname in sorted(os.listdir(cases_dir)):
        if fname.endswith(".json"):
            fpath = os.path.join(cases_dir, fname)
            with open(fpath, "r") as f:
                case_data = json.load(f)
            cases.append({
                "id": case_data.get("id"),
                "title": case_data.get("title"),
                "description": case_data.get("description"),
                "filename": fname,
            })
    return jsonify({"cases": cases})
