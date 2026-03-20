"""
CareFlow AI — Intake Schema
Defines the structured intake field schema used by the Clinical Structuring Agent.
Each field maps to the evidence-grounded data model.
"""

from typing import Dict, List

# Intake areas ordered by conversational priority
INTAKE_AREAS: List[Dict] = [
    {
        "area": "presenting_concern",
        "display": "Presenting Concern",
        "fields": [
            "main_concern",
            "reason_for_seeking_help",
            "urgency_as_reported",
        ],
        "required": True,
    },
    {
        "area": "symptom_description",
        "display": "Symptom / Experience Description",
        "fields": [
            "symptom_description",
            "onset_date",
            "duration",
            "severity_as_reported",
            "frequency",
            "triggers",
        ],
        "required": True,
    },
    {
        "area": "functional_impact",
        "display": "Functional Impact",
        "fields": [
            "sleep_description",
            "sleep_hours_per_night",
            "appetite_description",
            "energy_level",
            "concentration_description",
            "social_functioning",
            "occupational_or_academic_functioning",
            "self_care",
        ],
        "required": True,
    },
    {
        "area": "safety",
        "display": "Safety",
        "fields": [
            "self_harm_history",
            "suicidal_ideation_history",
            "current_safety_concern_as_reported",
        ],
        "required": True,
    },
    {
        "area": "history",
        "display": "Relevant History",
        "fields": [
            "previous_mental_health_concerns",
            "previous_treatment",
            "hospitalizations",
            "family_mental_health_history",
        ],
        "required": False,
    },
    {
        "area": "treatment_and_medications",
        "display": "Treatment & Medications",
        "fields": [
            "current_treatment",
            "current_medications",
            "medication_concerns",
            "previous_medications",
        ],
        "required": False,
    },
    {
        "area": "substances",
        "display": "Substances",
        "fields": [
            "alcohol_use",
            "substance_use",
            "caffeine_or_other",
        ],
        "required": False,
    },
    {
        "area": "support_and_context",
        "display": "Support & Context",
        "fields": [
            "living_situation",
            "family_context",
            "social_support",
            "protective_factors",
            "stressors",
        ],
        "required": False,
    },
    {
        "area": "goals",
        "display": "Patient Goals",
        "fields": [
            "goals_for_support",
            "preferences_for_care",
            "concerns_about_treatment",
        ],
        "required": False,
    },
]

REQUIRED_AREAS = [a["area"] for a in INTAKE_AREAS if a["required"]]
ALL_AREAS = [a["area"] for a in INTAKE_AREAS]

AREA_DISPLAY = {a["area"]: a["display"] for a in INTAKE_AREAS}

ALL_FIELDS = []
for area_def in INTAKE_AREAS:
    for f in area_def["fields"]:
        ALL_FIELDS.append({"area": area_def["area"], "field": f})


def get_area_fields(area: str) -> List[str]:
    for a in INTAKE_AREAS:
        if a["area"] == area:
            return a["fields"]
    return []


def get_field_area(field_name: str) -> str:
    for a in INTAKE_AREAS:
        if field_name in a["fields"]:
            return a["area"]
    return "unknown"
