"""
CareFlow AI — LLM Provider Abstraction
Supports: Groq (primary, ultra-fast) | Google Gemini (alternate)
Set LLM_PROVIDER=groq or LLM_PROVIDER=gemini in .env
"""

import os
import json
import time
import logging
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    duration_seconds: Optional[float] = None
    raw_response: Optional[Any] = None


class LLMClient:
    """
    Unified LLM client.
    Primary:  Groq  (openai/gpt-oss-20b) — fast inference with higher rate limits
    Alternate: Google Gemini (gemini-1.5-flash or gemini-1.5-pro)
    """

    def __init__(self):
        self.provider = os.environ.get("LLM_PROVIDER", "groq").lower()
        self.temperature = float(os.environ.get("LLM_TEMPERATURE", "0.1"))
        self._groq_client = None

    # ── Groq ──────────────────────────────────────────────────────────────────
    def _get_groq_client(self):
        if self._groq_client is None:
            try:
                from groq import Groq
            except ImportError:
                raise ImportError("groq package not installed. Run: pip install groq")
            api_key = os.environ.get("GROQ_API_KEY", "")
            if not api_key:
                raise ValueError(
                    "GROQ_API_KEY is not set. Add it to your .env file."
                )
            self._groq_client = Groq(api_key=api_key)
        return self._groq_client

    # ── Unified complete ───────────────────────────────────────────────────────
    def complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: Optional[float] = None,
        timeout: int = 90,
    ) -> LLMResponse:
        t_start = time.time()
        temp = temperature if temperature is not None else self.temperature

        if self.provider == "groq":
            response = self._groq_complete(
                messages, system_prompt, model, max_tokens, temp, timeout
            )
        elif self.provider in ("gemini", "google"):
            response = self._gemini_complete(
                messages, system_prompt, model, max_tokens, temp
            )
        else:
            raise ValueError(
                f"Unknown LLM_PROVIDER: '{self.provider}'. "
                "Valid options: groq | gemini"
            )

        response.duration_seconds = time.time() - t_start
        logger.info(
            "llm_call | provider=%s | model=%s | in=%s | out=%s | dur=%.2fs",
            response.provider,
            response.model,
            response.input_tokens,
            response.output_tokens,
            response.duration_seconds,
        )
        return response

    # ── Groq completion ────────────────────────────────────────────────────────
    def _groq_complete(
        self, messages, system_prompt, model, max_tokens, temperature, timeout
    ):
        client = self._get_groq_client()
        model_name = model or os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")

        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        resp = client.chat.completions.create(
            model=model_name,
            messages=all_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
        )
        return LLMResponse(
            content=resp.choices[0].message.content,
            model=model_name,
            provider="groq",
            input_tokens=getattr(resp.usage, "prompt_tokens", None),
            output_tokens=getattr(resp.usage, "completion_tokens", None),
            raw_response=resp,
        )

    # ── Gemini completion ──────────────────────────────────────────────────────
    def _gemini_complete(
        self, messages, system_prompt, model, max_tokens, temperature
    ):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Run: pip install google-generativeai"
            )

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )

        model_name = model or os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        genai.configure(api_key=api_key)

        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        # Combine into a single prompt (Gemini doesn't use chat turns for this use-case)
        prompt_parts = []
        if system_prompt:
            prompt_parts.append(f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n")
        for msg in messages:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            prompt_parts.append(f"{role}:\n{content}\n")
        full_prompt = "".join(prompt_parts)

        gemini_model = genai.GenerativeModel(
            model_name,
            generation_config=generation_config,
        )
        resp = gemini_model.generate_content(full_prompt)
        text = resp.text

        # Extract token counts if available
        input_tokens, output_tokens = None, None
        try:
            if hasattr(resp, "usage_metadata"):
                input_tokens = resp.usage_metadata.prompt_token_count
                output_tokens = resp.usage_metadata.candidates_token_count
        except Exception:
            pass

        return LLMResponse(
            content=text,
            model=model_name,
            provider="gemini",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            raw_response=resp,
        )

    # ── JSON wrapper ───────────────────────────────────────────────────────────
    def complete_json(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: Optional[float] = None,
        timeout: int = 90,
    ) -> Dict[str, Any]:
        """
        Calls complete() and robustly extracts a JSON dict from the response.
        Raises ValueError if valid JSON cannot be extracted after all recovery attempts.
        """
        response = self.complete(
            messages=messages,
            system_prompt=system_prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
        )
        return self._parse_json(response.content)

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """
        Three-stage JSON extraction:
        1. Direct parse (fastest path)
        2. From markdown ```json ... ``` fenced block
        3. First balanced { ... } block found anywhere
        """
        # 1. Direct
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        # 2. Fenced code block
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # 3. First { ... } block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        raise ValueError(
            f"Could not extract valid JSON from LLM response. "
            f"Provider={self.provider}. First 300 chars: {text[:300]}"
        )


# ── Module-level singleton ─────────────────────────────────────────────────────
_client_instance: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = LLMClient()
    return _client_instance
