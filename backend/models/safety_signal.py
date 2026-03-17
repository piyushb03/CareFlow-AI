"""
CareFlow AI — SafetySignal Model
Stores structured safety-relevant signals with evidence chain.
These are signals for reviewer attention — NOT diagnoses.
"""

import uuid
from backend.extensions import db


class SafetySignal(db.Model):
    __tablename__ = "safety_signals"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = db.Column(db.String(36), db.ForeignKey("cases.id"), nullable=False)

    # Signal taxonomy (see schemas/safety_taxonomy.py for full definitions)
    signal = db.Column(db.String(100), nullable=False)
    # self_harm_language | suicidal_ideation_language | harm_to_others_language |
    # acute_distress | severe_functional_impairment | substance_related_concern |
    # psychosis_like_language | abuse_or_immediate_danger |
    # protective_factors | support_availability

    status = db.Column(db.String(50), nullable=False, default="not_assessed")
    # present | absent | unclear | not_assessed

    evidence = db.Column(db.Text, nullable=True)              # exact quote or "not established"
    source_turns_json = db.Column(db.Text, nullable=True)     # JSON array of turn indices

    confidence = db.Column(db.Float, nullable=True)
    uncertainty = db.Column(db.Text, nullable=True)

    requires_reviewer_attention = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "case_id": self.case_id,
            "signal": self.signal,
            "status": self.status,
            "evidence": self.evidence,
            "source_turns": json.loads(self.source_turns_json) if self.source_turns_json else [],
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "requires_reviewer_attention": self.requires_reviewer_attention,
        }
