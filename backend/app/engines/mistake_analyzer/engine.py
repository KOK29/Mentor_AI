from __future__ import annotations
from typing import Any, Optional
from ...ai.provider import AIProvider


class MistakeAnalyzer:
    def __init__(self, ai: AIProvider, feedback_repo: Optional[Any] = None) -> None:
        self.ai = ai
        self._feedback = feedback_repo

    async def analyze(self, student_answer: str, correct_answer: str, context: str | None = None) -> dict[str, Any]:
        prompt = (
            f"Analyze the mistake. Student: {student_answer}. Correct: {correct_answer}. "
            f"Context: {context or 'general study'}. Explain the root cause, concise correction, and next steps."
        )
        resp = await self.ai.generate(prompt, model="mistake-mock")
        payload = resp["output"]["content"] if "output" in resp and isinstance(resp["output"], dict) else {}
        payload.setdefault("summary", f"The answer was close but missed the exact principle needed for {context or 'this task'}.")
        payload.setdefault("root_cause", "The learner likely focused on the wrong pattern or skipped the key requirement.")
        payload.setdefault("improvement_steps", [
            "Review the definition again",
            "Compare the reasoning with the correct rule",
            "Practice a similar problem using the corrected method",
            "Explain the answer aloud before choosing the final option",
        ])

        if self._feedback is not None:
            try:
                topic = (context or "General study").split("(")[0].strip()
                level = "beginner"
                if "(" in (context or "") and ")" in (context or ""):
                    level_piece = (context or "").split("(")[-1].split(")")[0]
                    if "," in level_piece:
                        level = level_piece.split(",")[-1].strip().lower()
                correction = await self._feedback.get_best_correction("mistake", topic, level)
                if correction:
                    payload = {**payload, **correction}
            except Exception:
                pass

        resp["output"] = {**resp.get("output", {}), "content": payload}
        return resp
