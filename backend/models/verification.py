"""
CareFlow AI — VerificationIssue Model
Records each issue found by the Verification Agent.
"""

import uuid
from datetime import datetime
from backend.extensions import db


class VerificationIssue(db.Model):
    __tablename__ = "verification_issues"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = db.Column(db.String(36), db.ForeignKey("cases.id"), nullable=False)
    agent_run_id = db.Column(db.String(36), db.ForeignKey("agent_runs.id"), nullable=True)

    issue_type = db.Column(db.String(100), nullable=False)
    # unsupported_claim | contradiction | missing_information |
    # evidence_mismatch | overconfidence | other

    severity = db.Column(db.String(20), nullable=False, default="medium")
    # low | medium | high

    description = db.Column(db.Text, nullable=False)
    evidence = db.Column(db.Text, nullable=True)
    source_turns_json = db.Column(db.Text, nullable=True)
    recommended_fix = db.Column(db.Text, nullable=True)

    resolved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "case_id": self.case_id,
            "agent_run_id": self.agent_run_id,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "description": self.description,
            "evidence": self.evidence,
            "source_turns": json.loads(self.source_turns_json) if self.source_turns_json else [],
            "recommended_fix": self.recommended_fix,
            "resolved": self.resolved,
            "created_at": self.created_at.isoformat(),
        }
