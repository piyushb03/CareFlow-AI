"""
CareFlow AI — ReviewerDecision Model
Records every reviewer action for audit trail.
"""

import uuid
from datetime import datetime
from backend.extensions import db


class ReviewerDecision(db.Model):
    __tablename__ = "reviewer_decisions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = db.Column(db.String(36), db.ForeignKey("cases.id"), nullable=False)

    action = db.Column(db.String(50), nullable=False)
    # approved | rejected | edited | added_note | marked_reviewed

    reviewer_id = db.Column(db.String(100), nullable=True)   # anonymous reviewer label
    notes = db.Column(db.Text, nullable=True)
    edited_fields_json = db.Column(db.Text, nullable=True)   # JSON of changes made
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "case_id": self.case_id,
            "action": self.action,
            "reviewer_id": self.reviewer_id,
            "notes": self.notes,
            "edited_fields": json.loads(self.edited_fields_json) if self.edited_fields_json else None,
            "created_at": self.created_at.isoformat(),
        }
