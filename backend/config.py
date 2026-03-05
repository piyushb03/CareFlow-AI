"""
CareFlow AI — Configuration
All runtime configuration from environment variables.
"""

import os


class Config:
    # Flask
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///careflow.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MB

    # LLM
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "groq")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_MODEL_FAST = os.environ.get("GROQ_MODEL_FAST", "llama-3.1-8b-instant")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")

    # Agent
    MAX_AGENT_RETRIES = int(os.environ.get("MAX_AGENT_RETRIES", "3"))
    AGENT_TIMEOUT_SECONDS = int(os.environ.get("AGENT_TIMEOUT_SECONDS", "60"))
    LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.1"))

    # Paths
    EVAL_CASES_DIR = os.environ.get("EVAL_CASES_DIR", "evaluation/cases")
    EVAL_GOLD_DIR = os.environ.get("EVAL_GOLD_DIR", "evaluation/gold")
    EVAL_RESULTS_DIR = os.environ.get("EVAL_RESULTS_DIR", "evaluation/results")
    REPORTS_DIR = os.environ.get("REPORTS_DIR", "reports")
    TRAJECTORIES_DIR = os.environ.get("TRAJECTORIES_DIR", "trajectories")
