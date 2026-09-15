"""Ollama-compatible Small Language Model provider with deterministic fallback."""
from __future__ import annotations
import json, os, re
import httpx
from .mock_provider import MockAIProvider

class LocalSLMProvider:
    def __init__(self) -> None:
        self.base_url = os.getenv("SLM_BASE_URL", "http://localhost:11434").rstrip("/")
        self.model = os.getenv("SLM_MODEL", "qwen2.5:3b")
        self.timeout = float(os.getenv("SLM_TIMEOUT_SECONDS", "20"))
        self.fallback = MockAIProvider()

    async def generate(self, prompt: str, *, model: str | None = None):
        system = (
            "You are MentorSLM, a Socratic teacher. Do not simply reveal answers when a learner can retry. "
            "Diagnose misconceptions, explain at the learner's level, and return ONLY a valid JSON object "
            "containing the fields requested by the prompt."
        )
        payload = {"model": self.model, "prompt": f"{system}\n\n{prompt}", "stream": False, "format": "json"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(f"{self.base_url}/api/generate", json=payload)
                r.raise_for_status()
                text = str(r.json().get("response") or "").strip()
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                raise ValueError("SLM response must be a JSON object")
            return {"model": self.model, "output": {"content": parsed}}
        except Exception:
            # Tournament-safe fallback: the demo remains functional if the local SLM service is unavailable.
            return await self.fallback.generate(prompt, model=model)
