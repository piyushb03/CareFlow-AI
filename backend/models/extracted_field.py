"""
CareFlow AI — ExtractedField Model
Every structured field extracted from conversation, with full evidence chain.
"""

import uuid
from backend.extensions import db


class ExtractedField(db.Model):
    __tablename__ = "extracted_fields"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = db.Column(db.String(36), db.ForeignKey("cases.id"), nullable=False)

    # Field identity
    category = db.Column(db.String(100), nullable=False)   # e.g. "sleep", "safety_signals"
    field_name = db.Column(db.String(200), nullable=False)  # e.g. "hours_per_night"

    # Value and evidence
    value = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="unknown")
    # explicit | inferred | unknown | contradictory

    evidence = db.Column(db.Text, nullable=True)            # direct quote from conversation
    source_turns_json = db.Column(db.Text, nullable=True)   # JSON array of turn indices

    confidence = db.Column(db.Float, nullable=True)
    uncertainty_note = db.Column(db.Text, nullable=True)    # explanation of uncertainty

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "case_id": self.case_id,
            "category": self.category,
            "field_name": self.field_name,
            "value": self.value,
            "status": self.status,
            "evidence": self.evidence,
            "source_turns": json.loads(self.source_turns_json) if self.source_turns_json else [],
            "confidence": self.confidence,
            "uncertainty_note": self.uncertainty_note,
        }
