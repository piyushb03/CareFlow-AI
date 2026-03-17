"""
CareFlow AI — Case Model
Central case record linking all downstream artifacts.
"""

import uuid
from datetime import datetime
from backend.extensions import db


class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Status lifecycle: intake → processing → ready_for_review → reviewed
    status = db.Column(db.String(50), default="intake", nullable=False)

    # Metadata (synthetic / de-identified only — no real patient PII)
    case_ref = db.Column(db.String(100), nullable=True)   # e.g. "CASE-2026-001"
    eval_case_id = db.Column(db.String(50), nullable=True)  # links to synthetic eval dataset

    # Processing
    processing_started_at = db.Column(db.DateTime, nullable=True)
    processing_completed_at = db.Column(db.DateTime, nullable=True)
    verification_status = db.Column(db.String(50), default="pending", nullable=False)
    # pending | passed | failed | requires_human_review

    # Final outputs stored as JSON text
    structured_summary_json = db.Column(db.Text, nullable=True)
    safety_signals_json = db.Column(db.Text, nullable=True)
    reviewer_brief_json = db.Column(db.Text, nullable=True)

    # Reviewer
    reviewer_status = db.Column(db.String(50), default="awaiting_review", nullable=False)
    # awaiting_review | approved | rejected | edited
    reviewer_notes = db.Column(db.Text, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewer_id = db.Column(db.String(100), nullable=True)  # anonymous reviewer label

    # Relationships
    conversation_turns = db.relationship("ConversationTurn", backref="case", lazy="dynamic", cascade="all, delete-orphan")
    agent_runs = db.relationship("AgentRun", backref="case", lazy="dynamic", cascade="all, delete-orphan")
    extracted_fields = db.relationship("ExtractedField", backref="case", lazy="dynamic", cascade="all, delete-orphan")
    safety_signals = db.relationship("SafetySignal", backref="case", lazy="dynamic", cascade="all, delete-orphan")
    verification_issues = db.relationship("VerificationIssue", backref="case", lazy="dynamic", cascade="all, delete-orphan")
    reviewer_decisions = db.relationship("ReviewerDecision", backref="case", lazy="dynamic", cascade="all, delete-orphan")
    audit_events = db.relationship("AuditEvent", backref="case", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self, include_relations=False):
        d = {
            "id": self.id,
            "case_ref": self.case_ref,
            "status": self.status,
            "verification_status": self.verification_status,
            "reviewer_status": self.reviewer_status,
            "reviewer_notes": self.reviewer_notes,
            "reviewer_id": self.reviewer_id,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "processing_started_at": self.processing_started_at.isoformat() if self.processing_started_at else None,
            "processing_completed_at": self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            "eval_case_id": self.eval_case_id,
        }
        if include_relations:
            import json
            d["structured_summary"] = json.loads(self.structured_summary_json) if self.structured_summary_json else None
            d["safety_signals_summary"] = json.loads(self.safety_signals_json) if self.safety_signals_json else None
            d["reviewer_brief"] = json.loads(self.reviewer_brief_json) if self.reviewer_brief_json else None
        return d
