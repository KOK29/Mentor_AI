from __future__ import annotations
from typing import Any, Optional


class MasteryEngine:
    def __init__(self, feedback_repo: Optional[Any] = None) -> None:
        self._feedback = feedback_repo

    async def calculate(self, attempts: list[dict[str, Any]]) -> dict[str, Any]:
        if not attempts:
            return {
                "mastery": 0.0,
                "confidence": 0.0,
                "accuracy": 0.0,
                "attempts": 0,
                "recommended_review": "now",
                "next_focus": "Start with the basics and build one concept at a time",
            }

        correct = sum(1 for attempt in attempts if bool(attempt.get("correct")))
        accuracy = correct / len(attempts)
        recency = min(1.0, max(0.2, len(attempts) / 10))
        difficulty_weight = sum(float(attempt.get("difficulty_score", 0.5)) for attempt in attempts) / len(attempts)
        score = min(1.0, round((accuracy * 0.55) + (recency * 0.25) + (difficulty_weight * 0.2), 3))

        level = "beginner" if score < 0.4 else "intermediate" if score < 0.75 else "advanced"
        next_focus = (
            "Revisit the fundamentals and simplify the explanation"
            if level == "beginner"
            else "Practice a wider range of applications and edge cases"
            if level == "intermediate"
            else "Prepare for deeper synthesis and expert-level problem solving"
        )

        if self._feedback is not None:
            try:
                topic = str((attempts[0] or {}).get("topic") or "General study")
                correction = await self._feedback.get_best_correction("mastery", topic, "general")
                if correction:
                    if "next_focus" in correction:
                        next_focus = str(correction["next_focus"])
                    if "level" in correction:
                        level = str(correction["level"])
                    if "mastery" in correction:
                        score = float(correction["mastery"])
            except Exception:
                pass

        return {
            "mastery": score,
            "confidence": round(min(1.0, score + 0.1), 3),
            "accuracy": round(accuracy, 3),
            "attempts": len(attempts),
            "recommended_review": "in 2 days" if score >= 0.7 else "today",
            "level": level,
            "next_focus": next_focus,
        }

