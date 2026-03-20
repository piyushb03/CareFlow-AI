"""
CareFlow AI — Safety Signal Taxonomy
Defines the 10 safety-relevant signal categories used by the Safety Signal Agent.

IMPORTANT: These are signals for reviewer attention, NOT diagnoses.
The system never claims to diagnose a mental-health condition.
"""

from typing import Dict

SAFETY_SIGNALS: Dict[str, Dict] = {
    "self_harm_language": {
        "display": "Self-Harm Related Language",
        "description": "Language suggesting thoughts, urges, or behaviors related to harming oneself.",
        "examples": ["cutting", "hurting myself", "self-destructive"],
        "reviewer_guidance": "Requires immediate qualified clinical assessment. Do not interpret absence of explicit statement as absence of concern.",
        "requires_attention_if": "present",
    },
    "suicidal_ideation_language": {
        "display": "Suicidal Ideation Related Language",
        "description": "Language suggesting thoughts about death, dying, suicide, or not wanting to exist.",
        "examples": ["don't want to be here anymore", "better off dead", "thinking about ending it"],
        "reviewer_guidance": "Requires immediate qualified clinical assessment. Assess specificity, plan, means, intent.",
        "requires_attention_if": "present",
    },
    "harm_to_others_language": {
        "display": "Harm-to-Others Related Language",
        "description": "Language suggesting thoughts, urges, or intentions to harm others.",
        "examples": ["want to hurt someone", "violent thoughts", "can't control anger"],
        "reviewer_guidance": "Requires qualified clinical and risk assessment. Assess specificity and intent.",
        "requires_attention_if": "present",
    },
    "acute_distress": {
        "display": "Acute Distress",
        "description": "Language or descriptions suggesting significant, current psychological distress.",
        "examples": ["can't cope", "falling apart", "in crisis", "overwhelming panic"],
        "reviewer_guidance": "Assess acuity and functional impact. Prioritize for timely review.",
        "requires_attention_if": "present",
    },
    "severe_functional_impairment": {
        "display": "Severe Functional Impairment",
        "description": "Reported inability to maintain basic daily activities, work, relationships, or self-care.",
        "examples": ["can't get out of bed", "lost my job", "not eating or sleeping"],
        "reviewer_guidance": "Assess duration and trajectory. May indicate need for more intensive support.",
        "requires_attention_if": "present",
    },
    "substance_related_concern": {
        "display": "Substance-Related Concern",
        "description": "Reported or implied problematic use of alcohol, substances, or medications.",
        "examples": ["drinking every day", "using to cope", "increased use recently"],
        "reviewer_guidance": "Assess type, frequency, quantity, and function. Note impact on safety and functioning.",
        "requires_attention_if": "present",
    },
    "psychosis_like_language": {
        "display": "Psychosis-Like Language",
        "description": "Language suggesting perceptual disturbances, unusual beliefs, or disorganized thinking.",
        "examples": ["hearing voices", "people are following me", "thoughts don't make sense"],
        "reviewer_guidance": "Requires specialist assessment. Note specific content, distress, and functional impact.",
        "requires_attention_if": "present",
    },
    "abuse_or_immediate_danger": {
        "display": "Abuse or Immediate Danger",
        "description": "Reports or suggestions of current or recent abuse, domestic violence, or immediate danger.",
        "examples": ["partner hurts me", "not safe at home", "afraid of someone"],
        "reviewer_guidance": "Requires immediate qualified safety assessment. Follow organizational safeguarding protocols.",
        "requires_attention_if": "present",
    },
    "protective_factors": {
        "display": "Protective Factors",
        "description": "Factors that may reduce risk or support resilience, such as social support, reasons for living, engagement in care.",
        "examples": ["have good support", "children keep me going", "willing to seek help"],
        "reviewer_guidance": "Positive contextual factor. Note strength and reliability of protective factors.",
        "requires_attention_if": "absent",
    },
    "support_availability": {
        "display": "Support Availability",
        "description": "Presence or absence of identified social, family, or professional support.",
        "examples": ["has family nearby", "no one to talk to", "isolated"],
        "reviewer_guidance": "Important context for care planning. Absence of support increases risk context.",
        "requires_attention_if": "absent",
    },
}

ALL_SIGNAL_NAMES = list(SAFETY_SIGNALS.keys())

SIGNAL_DISPLAY_NAMES = {k: v["display"] for k, v in SAFETY_SIGNALS.items()}


def get_signal_info(signal_name: str) -> Dict:
    """Return full taxonomy info for a signal name."""
    return SAFETY_SIGNALS.get(signal_name, {})


def get_all_signal_names() -> list:
    return ALL_SIGNAL_NAMES
