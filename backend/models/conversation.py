"""
CareFlow AI — ConversationTurn Model
Records each turn of the intake conversation with turn ID for evidence tracing.
"""

import uuid
from datetime import datetime
from backend.extensions import db


class ConversationTurn(db.Model):
    __tablename__ = "conversation_turns"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = db.Column(db.String(36), db.ForeignKey("cases.id"), nullable=False)

    # turn_index is the stable numeric ID referenced in evidence (e.g. "source_turns: [3, 7]")
    turn_index = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # "agent" | "patient"
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Optional metadata
    intake_area = db.Column(db.String(100), nullable=True)   # e.g. "sleep", "safety"
    question_rationale = db.Column(db.Text, nullable=True)   # why the agent asked this

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "turn_index": self.turn_index,
            "role": self.role,
            "content": self.content,
            "intake_area": self.intake_area,
            "question_rationale": self.question_rationale,
            "created_at": self.created_at.isoformat(),
        }
