"""
CareFlow AI — AuditEvent Model
Immutable log of all system events.
"""

import uuid
from datetime import datetime
from backend.extensions import db


class AuditEvent(db.Model):
    __tablename__ = "audit_events"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = db.Column(db.String(36), db.ForeignKey("cases.id"), nullable=False)

    event_type = db.Column(db.String(100), nullable=False)
    # case_created | intake_started | agent_started | agent_completed |
    # verification_passed | verification_failed | human_review_required |
    # reviewer_approved | reviewer_rejected | case_closed

    actor = db.Column(db.String(100), nullable=True)   # "system" | "reviewer_X"
    description = db.Column(db.Text, nullable=True)
    metadata_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "case_id": self.case_id,
            "event_type": self.event_type,
            "actor": self.actor,
            "description": self.description,
            "metadata": json.loads(self.metadata_json) if self.metadata_json else None,
            "created_at": self.created_at.isoformat(),
        }
