"""
CareFlow AI — Agent Base Class
All agents inherit from this. Handles prompt loading, LLM calls,
AgentRun persistence, and retry logic.
"""

import os
import json
import time
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from backend.services.llm.client import get_llm_client, LLMResponse
from backend.extensions import db

logger = logging.getLogger(__name__)

# base.py lives at: backend/services/agents/base.py
# project root is 3 dirs up: backend/services/agents -> backend/services -> backend -> root
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "prompts")


class AgentBase(ABC):
    name: str = "base_agent"
    prompt_file: str = ""
    prompt_version: str = "v1.0"

    def __init__(self):
        self.llm = get_llm_client()
        self._system_prompt: Optional[str] = None

    def load_prompt(self) -> str:
        """Load agent prompt from versioned markdown file."""
        if self._system_prompt is not None:
            return self._system_prompt
        prompt_path = os.path.normpath(os.path.join(PROMPTS_DIR, self.prompt_file))
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self._system_prompt = f.read()
        return self._system_prompt

    def _create_agent_run(self, case_id: str, input_summary: str) -> Any:
        """Persist an AgentRun record at the start of execution."""
        from backend.models.agent_run import AgentRun
        run = AgentRun(
            case_id=case_id,
            agent_name=self.name,
            prompt_version=self.prompt_version,
            model=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
            status="running",
            input_summary=input_summary[:2000] if input_summary else None,
        )
        db.session.add(run)
        db.session.commit()
        return run

    def _complete_agent_run(self, run: Any, output: Dict, llm_response: Optional[LLMResponse] = None, error: Optional[str] = None, **kwargs):
        """Update AgentRun on completion."""
        run.completed_at = datetime.utcnow()
        run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
        run.status = "failed" if error else "completed"
        run.output_json = json.dumps(output) if output else None
        run.error_message = error
        if llm_response:
            run.estimated_input_tokens = llm_response.input_tokens
            run.estimated_output_tokens = llm_response.output_tokens
            run.model = llm_response.model
        db.session.commit()

    def _log_audit(self, case_id: str, event_type: str, description: str, metadata: Optional[Dict] = None):
        """Write an audit event."""
        from backend.models.audit import AuditEvent
        event = AuditEvent(
            case_id=case_id,
            event_type=event_type,
            actor=f"agent:{self.name}",
            description=description,
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        db.session.add(event)
        db.session.commit()

    @abstractmethod
    def run(self, case_id: str, **kwargs) -> Dict[str, Any]:
        """Execute the agent and return structured output."""
        pass
