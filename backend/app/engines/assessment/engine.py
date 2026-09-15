from __future__ import annotations
from typing import Any, Optional


class AssessmentEngine:
    def __init__(self, feedback_repo: Optional[Any] = None) -> None:
        self._feedback = feedback_repo

    async def grade(self, answers: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(answers)
        if total == 0:
            return {
                "score": 0.0,
                "passed": False,
                "report": "No answers provided",
                "correct": 0,
                "total": 0,
                "next_step": "Start with a quick concept review and a simpler practice set",
            }

        correct = sum(1 for answer in answers if bool(answer.get("correct")))
        percentage = correct / total
        passed = percentage >= 0.7

        if self._feedback is not None:
            try:
                topic = str((answers[0] or {}).get("topic") or "General study")
                correction = await self._feedback.get_best_correction("assessment", topic, "general")
                if correction:
                    if "threshold" in correction:
                        passed = percentage >= float(correction["threshold"])
                    if "next_step" in correction:
                        next_step = str(correction["next_step"])
                    else:
                        next_step = (
                            "Move to advanced cases and explain your reasoning clearly"
                            if passed else "Review the key concept and retry a simpler version before moving forward"
                        )
                else:
                    next_step = (
                        "Move to advanced cases and explain your reasoning clearly"
                        if passed else "Review the key concept and retry a simpler version before moving forward"
                    )
            except Exception:
                next_step = (
                    "Move to advanced cases and explain your reasoning clearly"
                    if passed else "Review the key concept and retry a simpler version before moving forward"
                )
        else:
            next_step = (
                "Move to advanced cases and explain your reasoning clearly"
                if passed else "Review the key concept and retry a simpler version before moving forward"
            )

        return {
            "score": round(percentage, 3),
            "correct": correct,
            "total": total,
            "passed": passed,
            "report": "Strong understanding" if passed else "Needs review",
            "next_step": next_step,
        }

