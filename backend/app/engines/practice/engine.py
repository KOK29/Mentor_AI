from __future__ import annotations
from typing import Any, Optional
from ...ai.provider import AIProvider


class PracticeEngine:
    def __init__(self, ai: AIProvider, feedback_repo: Optional[Any] = None) -> None:
        self.ai = ai
        self._feedback = feedback_repo

    def _normalize_difficulty(self, difficulty: str) -> str:
        value = (difficulty or "medium").lower().strip()
        return value if value in {"easy", "medium", "hard"} else "medium"

    def _domain_focus(self, topic: str) -> str:
        lowered = topic.lower()
        if any(token in lowered for token in ["business", "marketing", "finance", "management", "strategy"]):
            return "business_decision_making"
        if any(token in lowered for token in ["it", "support", "network", "security", "system"]):
            return "it_support_and_operations"
        if any(token in lowered for token in ["programming", "software", "python", "javascript", "code", "development"]):
            return "software_problem_solving"
        if any(token in lowered for token in ["computer science", "cs", "algorithm", "architecture", "database", "systems"]):
            return "cs_reasoning_and_design"
        return "core_understanding"

    async def generate_exercise(self, topic: str, difficulty: str = "medium", kind: str = "mcq") -> dict[str, Any]:
        resolved = self._normalize_difficulty(difficulty)
        prompt = (
            f"Generate a {resolved} {kind} exercise for topic: {topic}. "
            "Include question, choices, correct_answer, explanation, hint, difficulty, and a short skill tag."
        )
        resp = await self.ai.generate(prompt, model="practice-mock")
        payload = resp["output"]["content"] if "output" in resp and isinstance(resp["output"], dict) else {}
        payload.setdefault("difficulty", resolved)
        payload.setdefault("hint", f"Think about the core rule of {topic} and how it applies in a realistic scenario.")
        payload.setdefault("skill_tag", "application")
        payload.setdefault("domain_focus", self._domain_focus(topic))

        if self._feedback is not None:
            try:
                correction = await self._feedback.get_best_correction("practice", topic, resolved)
                if correction:
                    payload = {**payload, **correction}
            except Exception:
                pass

        resp["output"] = {**resp.get("output", {}), "content": payload}
        return resp
