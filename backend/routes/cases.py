"""
CareFlow AI — Cases Routes
Core API for case management, intake, processing, and reviewer workflow.
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from backend.extensions import db

logger = logging.getLogger(__name__)

cases_bp = Blueprint("cases", __name__)


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


# ─────────────────────────────────────────────────────────────────────────────
# Case CRUD
# ─────────────────────────────────────────────────────────────────────────────

@cases_bp.route("/cases", methods=["POST"])
def create_case():
    """Create a new intake case."""
    from backend.models.case import Case
    from backend.models.audit import AuditEvent

    data = request.get_json(silent=True) or {}
    case_ref = data.get("case_ref") or f"CASE-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    eval_case_id = data.get("eval_case_id")

    case = Case(case_ref=case_ref, eval_case_id=eval_case_id)
    db.session.add(case)
    db.session.flush()  # assigns case.id before using it in AuditEvent

    audit = AuditEvent(
        case_id=case.id,
        event_type="case_created",
        actor="system",
        description=f"Case created: {case_ref}",
    )
    db.session.add(audit)
    db.session.commit()

    logger.info("Case created: %s", case.id)
    return jsonify(case.to_dict()), 201


@cases_bp.route("/cases", methods=["GET"])
def list_cases():
    """List all cases."""
    from backend.models.case import Case
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status_filter = request.args.get("status")

    query = Case.query.order_by(Case.created_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "cases": [c.to_dict() for c in paginated.items],
        "total": paginated.total,
        "page": page,
        "per_page": per_page,
        "pages": paginated.pages,
    })


@cases_bp.route("/cases/<case_id>", methods=["GET"])
def get_case(case_id):
    """Get full case details."""
    from backend.models.case import Case
    case = Case.query.get(case_id)
    if not case:
        return _error("Case not found", 404)
    return jsonify(case.to_dict(include_relations=True))


# ─────────────────────────────────────────────────────────────────────────────
# Conversation / Intake
# ─────────────────────────────────────────────────────────────────────────────

@cases_bp.route("/cases/<case_id>/messages", methods=["POST"])
def add_message(case_id):
    """
    Add a message to the intake conversation and get the next agent question.
    Supports real-time interview mode.
    """
    from backend.models.case import Case
    from backend.models.conversation import ConversationTurn
    from backend.services.agents.intake_agent import IntakeAgent

    case = Case.query.get(case_id)
    if not case:
        return _error("Case not found", 404)
    if case.status not in ("intake", "ready_for_review"):
        return _error(f"Case is not in intake state (current: {case.status})", 400)

    data = request.get_json(silent=True) or {}
    patient_content = data.get("content", "").strip()
    if not patient_content:
        return _error("Message content is required")

    # Get next turn index
    from sqlalchemy import func
    max_idx = db.session.query(func.max(ConversationTurn.turn_index)).filter_by(case_id=case_id).scalar()
    next_idx = (max_idx or 0) + 1

    # Save patient turn
    patient_turn = ConversationTurn(
        case_id=case_id,
        turn_index=next_idx,
        role="patient",
        content=patient_content,
    )
    db.session.add(patient_turn)
    db.session.commit()

    # Load conversation history
    turns = (
        ConversationTurn.query
        .filter_by(case_id=case_id)
        .order_by(ConversationTurn.turn_index)
        .all()
    )
    conversation_history = [t.to_dict() for t in turns]

    # Determine missing areas
    covered_areas = data.get("covered_areas", [])
    from backend.schemas.intake_schema import REQUIRED_AREAS
    missing_areas = [a for a in REQUIRED_AREAS if a not in covered_areas]

    # Get next question from Intake Agent
    agent = IntakeAgent()
    next_q = agent.get_next_question(
        case_id=case_id,
        conversation_history=conversation_history,
        collected_fields=data.get("collected_fields", {}),
        missing_areas=missing_areas,
    )

    if next_q.get("is_complete"):
        # Mark case ready for processing
        case.status = "intake"  # will be changed to processing when /process is called
        db.session.commit()
        return jsonify({
            "patient_turn": patient_turn.to_dict(),
            "is_complete": True,
            "next_question": None,
            "covered_areas": next_q.get("missing_areas_remaining", []),
            "message": "Intake conversation complete. Ready for processing.",
        })

    # Save agent turn
    agent_turn_idx = next_idx + 1
    agent_turn = ConversationTurn(
        case_id=case_id,
        turn_index=agent_turn_idx,
        role="agent",
        content=next_q.get("question", ""),
        intake_area=next_q.get("area"),
        question_rationale=next_q.get("rationale"),
    )
    db.session.add(agent_turn)
    db.session.commit()

    return jsonify({
        "patient_turn": patient_turn.to_dict(),
        "agent_turn": agent_turn.to_dict(),
        "is_complete": False,
        "missing_areas_remaining": next_q.get("missing_areas_remaining", []),
        "area": next_q.get("area"),
        "rationale": next_q.get("rationale"),
    })


@cases_bp.route("/cases/<case_id>/start-interview", methods=["POST"])
def start_interview(case_id):
    """Start a new interview — returns the opening question."""
    from backend.models.case import Case
    from backend.models.conversation import ConversationTurn
    from backend.services.agents.intake_agent import IntakeAgent
    from backend.schemas.intake_schema import REQUIRED_AREAS

    case = Case.query.get(case_id)
    if not case:
        return _error("Case not found", 404)

    agent = IntakeAgent()
    opening = agent.get_next_question(
        case_id=case_id,
        conversation_history=[],
        collected_fields={},
        missing_areas=REQUIRED_AREAS,
    )

    # Save first agent turn
    first_turn = ConversationTurn(
        case_id=case_id,
        turn_index=1,
        role="agent",
        content=opening.get("question", "Could you start by telling me what brings you here today?"),
        intake_area=opening.get("area", "presenting_concern"),
        question_rationale=opening.get("rationale", "Opening question"),
    )
    db.session.add(first_turn)
    db.session.flush()  # get first_turn.id

    from backend.models.audit import AuditEvent
    audit = AuditEvent(
        case_id=case_id,
        event_type="intake_started",
        actor="system",
        description="Intake interview started",
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "agent_turn": first_turn.to_dict(),
        "missing_areas": REQUIRED_AREAS,
        "message": "Interview started. This is an AI-assisted intake tool — not a clinical assessment.",
    })


# ─────────────────────────────────────────────────────────────────────────────
# Processing
# ─────────────────────────────────────────────────────────────────────────────

@cases_bp.route("/cases/<case_id>/process", methods=["POST"])
def process_case(case_id):
    """
    Trigger the full multi-agent processing pipeline.
    Runs Safety → Structuring → Verification → Reviewer Brief.
    """
    from backend.models.case import Case
    from backend.services.orchestration.orchestrator import TriageOrchestrator

    case = Case.query.get(case_id)
    if not case:
        return _error("Case not found", 404)

    # Allow re-processing if needed
    if case.status not in ("intake", "ready_for_review", "error"):
        return _error(f"Case cannot be processed in current state: {case.status}", 400)

    try:
        orchestrator = TriageOrchestrator()
        result = orchestrator.process_case(case_id)
        return jsonify(result)
    except Exception as e:
        logger.error("Processing failed for case %s: %s", case_id, e)
        return _error(f"Processing failed: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────────────────────
# Reviewer Workflow
# ─────────────────────────────────────────────────────────────────────────────

@cases_bp.route("/cases/<case_id>/trajectory", methods=["GET"])
def get_trajectory(case_id):
    """Get agent trajectory for judge inspection."""
    import os
    trajectories_dir = os.environ.get("TRAJECTORIES_DIR", "trajectories")
    path = os.path.join(trajectories_dir, f"{case_id}.json")
    if not os.path.exists(path):
        return _error("Trajectory not found — case may not have been processed", 404)
    with open(path, "r") as f:
        trajectory = json.load(f)
    return jsonify(trajectory)


@cases_bp.route("/cases/<case_id>/evidence", methods=["GET"])
def get_evidence(case_id):
    """Get all extracted fields with full evidence chain for Evidence Explorer."""
    from backend.models.extracted_field import ExtractedField
    from backend.models.safety_signal import SafetySignal

    fields = ExtractedField.query.filter_by(case_id=case_id).all()
    signals = SafetySignal.query.filter_by(case_id=case_id).all()

    return jsonify({
        "case_id": case_id,
        "extracted_fields": [f.to_dict() for f in fields],
        "safety_signals": [s.to_dict() for s in signals],
    })


@cases_bp.route("/cases/<case_id>/verification", methods=["GET"])
def get_verification(case_id):
    """Get all verification issues for a case."""
    from backend.models.verification import VerificationIssue
    issues = VerificationIssue.query.filter_by(case_id=case_id).all()
    return jsonify({
        "case_id": case_id,
        "issues": [i.to_dict() for i in issues],
    })


@cases_bp.route("/cases/<case_id>/conversation", methods=["GET"])
def get_conversation(case_id):
    """Get all conversation turns."""
    from backend.models.conversation import ConversationTurn
    turns = (
        ConversationTurn.query
        .filter_by(case_id=case_id)
        .order_by(ConversationTurn.turn_index)
        .all()
    )
    return jsonify({
        "case_id": case_id,
        "turns": [t.to_dict() for t in turns],
    })


@cases_bp.route("/cases/<case_id>/review", methods=["POST"])
def review_case(case_id):
    """Add reviewer notes."""
    from backend.models.case import Case
    from backend.models.review import ReviewerDecision
    from backend.models.audit import AuditEvent

    case = Case.query.get(case_id)
    if not case:
        return _error("Case not found", 404)

    data = request.get_json(silent=True) or {}
    notes = data.get("notes", "")
    reviewer_id = data.get("reviewer_id", "anonymous")

    decision = ReviewerDecision(
        case_id=case_id,
        action="added_note",
        reviewer_id=reviewer_id,
        notes=notes,
    )
    case.reviewer_notes = notes
    case.reviewer_id = reviewer_id
    db.session.add(decision)

    audit = AuditEvent(
        case_id=case_id,
        event_type="reviewer_note_added",
        actor=reviewer_id,
        description="Reviewer added notes",
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"status": "ok", "message": "Notes added"})


@cases_bp.route("/cases/<case_id>/approve", methods=["POST"])
def approve_case(case_id):
    """Reviewer approves the intake summary."""
    from backend.models.case import Case
    from backend.models.review import ReviewerDecision
    from backend.models.audit import AuditEvent

    case = Case.query.get(case_id)
    if not case:
        return _error("Case not found", 404)

    data = request.get_json(silent=True) or {}
    reviewer_id = data.get("reviewer_id", "anonymous")
    notes = data.get("notes", "")

    case.reviewer_status = "approved"
    case.reviewed_at = datetime.utcnow()
    case.reviewer_id = reviewer_id
    case.status = "reviewed"
    if notes:
        case.reviewer_notes = notes

    decision = ReviewerDecision(
        case_id=case_id, action="approved", reviewer_id=reviewer_id, notes=notes
    )
    db.session.add(decision)

    audit = AuditEvent(
        case_id=case_id, event_type="reviewer_approved", actor=reviewer_id,
        description="Reviewer approved intake summary"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"status": "ok", "message": "Case approved"})


@cases_bp.route("/cases/<case_id>/reject", methods=["POST"])
def reject_case(case_id):
    """Reviewer rejects the intake summary."""
    from backend.models.case import Case
    from backend.models.review import ReviewerDecision
    from backend.models.audit import AuditEvent

    case = Case.query.get(case_id)
    if not case:
        return _error("Case not found", 404)

    data = request.get_json(silent=True) or {}
    reviewer_id = data.get("reviewer_id", "anonymous")
    notes = data.get("notes", "")
    reason = data.get("reason", "Reviewer rejected")

    case.reviewer_status = "rejected"
    case.reviewed_at = datetime.utcnow()
    case.reviewer_id = reviewer_id
    case.reviewer_notes = f"REJECTED: {reason}. {notes}"

    decision = ReviewerDecision(
        case_id=case_id, action="rejected", reviewer_id=reviewer_id,
        notes=f"Reason: {reason}. {notes}"
    )
    db.session.add(decision)

    audit = AuditEvent(
        case_id=case_id, event_type="reviewer_rejected", actor=reviewer_id,
        description=f"Reviewer rejected: {reason}"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"status": "ok", "message": "Case rejected"})


@cases_bp.route("/cases/<case_id>/audit", methods=["GET"])
def get_audit(case_id):
    """Get full audit trail for a case."""
    from backend.models.audit import AuditEvent
    events = (
        AuditEvent.query
        .filter_by(case_id=case_id)
        .order_by(AuditEvent.created_at)
        .all()
    )
    return jsonify({
        "case_id": case_id,
        "events": [e.to_dict() for e in events],
    })


@cases_bp.route("/cases/<case_id>/agent-runs", methods=["GET"])
def get_agent_runs(case_id):
    """Get all agent runs for a case."""
    from backend.models.agent_run import AgentRun
    runs = (
        AgentRun.query
        .filter_by(case_id=case_id)
        .order_by(AgentRun.started_at)
        .all()
    )
    return jsonify({
        "case_id": case_id,
        "agent_runs": [r.to_dict() for r in runs],
    })
