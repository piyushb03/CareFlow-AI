"""
CareFlow AI — Health Check Route
"""

from flask import Blueprint, jsonify
import datetime

health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "CareFlow AI",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "disclaimer": "AI-assisted intake preparation only. Not a diagnostic system.",
    })


@health_bp.route("/")
def root():
    return jsonify({
        "service": "CareFlow AI API",
        "version": "1.0.0",
        "purpose": "Agentic Clinical Intake & Triage Orchestrator",
        "disclaimer": (
            "This system assists intake preparation only. "
            "All consequential decisions remain with qualified human reviewers."
        ),
    })
