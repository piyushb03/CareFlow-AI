"""
CareFlow AI — AgentRun Model
Full audit trail for every agent execution including prompt version, timing, and retry info.
"""

import uuid
from datetime import datetime
from backend.extensions import db


class AgentRun(db.Model):
    __tablename__ = "agent_runs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = db.Column(db.String(36), db.ForeignKey("cases.id"), nullable=False)

    agent_name = db.Column(db.String(100), nullable=False)
    prompt_version = db.Column(db.String(20), nullable=False, default="v1.0")
    model = db.Column(db.String(100), nullable=False)

    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Float, nullable=True)

    status = db.Column(db.String(50), nullable=False, default="running")
    # running | completed | failed | retrying

    retry_number = db.Column(db.Integer, default=0, nullable=False)

    # Stored as JSON text — input/output summaries for trajectory
    input_summary = db.Column(db.Text, nullable=True)
    output_json = db.Column(db.Text, nullable=True)

    verification_result = db.Column(db.String(50), nullable=True)
    # passed | failed | skipped

    # Token tracking (best-effort)
    estimated_input_tokens = db.Column(db.Integer, nullable=True)
    estimated_output_tokens = db.Column(db.Integer, nullable=True)

    error_message = db.Column(db.Text, nullable=True)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "case_id": self.case_id,
            "agent_name": self.agent_name,
            "prompt_version": self.prompt_version,
            "model": self.model,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "retry_number": self.retry_number,
            "input_summary": self.input_summary,
            "output": json.loads(self.output_json) if self.output_json else None,
            "verification_result": self.verification_result,
            "estimated_input_tokens": self.estimated_input_tokens,
            "estimated_output_tokens": self.estimated_output_tokens,
            "error_message": self.error_message,
        }
