from __future__ import annotations
from typing import Any, Optional


class LearningPathEngine:
    def __init__(self, feedback_repo: Optional[Any] = None) -> None:
        self._feedback = feedback_repo

    async def recommend(
        self,
        goal: str,
        current_level: str = "beginner",
        mastery: float | None = None,
        recent_history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        level_rank = {"beginner": 1, "intermediate": 2, "advanced": 3}
        level = level_rank.get((current_level or "beginner").lower(), 1)

        recent_topic_entries = []
        if recent_history:
            recent_topic_entries = [
                item for item in recent_history if isinstance(item, dict) and item.get("topic", "").lower() == goal.lower()
            ]

        mastery_score = float(mastery) if mastery is not None else 0.5
        mastery_score = max(0.0, min(1.0, mastery_score))

        if mastery_score >= 0.75:
            focus = "consolidate strategic depth and speed"
            next_best_action = f"Push deeper into advanced {goal} problem solving and compare elegant solutions"
            daily_plan = [
                f"Solve a challenging {goal} case study",
                f"Review one advanced explanation and summarize the key insight",
                f"Reinforce weak points with a timed mini-quiz",
            ]
            weekly_plan = [
                f"Complete 2 deeper {goal} practice sets",
                f"Document the strongest patterns and trade-offs in {goal}",
                f"Test yourself on edge cases and business-impact scenarios",
            ]
        elif mastery_score >= 0.45:
            focus = "close the remaining gap with targeted review"
            next_best_action = f"Apply the core {goal} ideas to realistic tasks and fix the recurring mistakes"
            daily_plan = [
                f"Review the most important {goal} concept from your recent lessons",
                f"Solve a timed {goal} practice set with feedback",
                f"Revisit the last mistake and rework the correct method",
            ]
            weekly_plan = [
                f"Practice 3 moderate {goal} exercises with reflection",
                f"Compare multiple ways of solving the same {goal} problem",
                f"Finish a concise recap of your growth areas in {goal}",
            ]
        else:
            focus = "build confidence with fundamentals and repetition"
            next_best_action = f"Build the fundamentals of {goal} with short lessons, examples, and guided practice"
            daily_plan = [
                f"Read the overview of {goal}",
                f"Practice 5 foundational {goal} questions",
                f"Review one mistake from your last session and write the correct rule",
            ]
            weekly_plan = [
                f"Master the core concepts of {goal}",
                f"Complete 2 mini assessments in {goal}",
                f"Review vocabulary, steps, examples, and the most common mistakes",
            ]

        if level == 1:
            next_best_action = f"Build the fundamentals of {goal} with short lessons and guided examples"
            daily_plan = [
                f"Read the overview of {goal}",
                f"Practice 5 foundational {goal} questions",
                f"Apply one {goal} concept in a real example and explain the reasoning",
            ]
            weekly_plan = [
                f"Master the core concepts of {goal}",
                f"Complete 2 mini assessments in {goal}",
                f"Review vocabulary, steps, and examples",
            ]
        elif level == 2:
            next_best_action = f"Apply the core ideas of {goal} to realistic problems and compare solutions"
            daily_plan = [
                f"Study an intermediate {goal} concept with examples",
                f"Solve a timed practice set in {goal}",
                f"Review the mistakes and strengthen weak points",
            ]
            weekly_plan = [
                f"Solve practical {goal} challenges",
                f"Compare different approaches in {goal}",
                f"Prepare a short recap and revision summary",
            ]
            if recent_topic_entries:
                wrong_recent = sum(1 for item in recent_topic_entries if not item.get("correct", False))
                if wrong_recent > 0:
                    daily_plan[2] = f"Reconnect the last {wrong_recent} mistake(s) in {goal} and fix the pattern"
        else:
            next_best_action = f"Tackle deep challenges in {goal} by optimizing, refining, and defending your reasoning"
            daily_plan = [
                f"Work on an advanced {goal} case study",
                f"Compare alternatives and justify the best method",
                f"Review feedback and improve your final answer",
            ]
            weekly_plan = [
                f"Handle a complex {goal} problem set",
                f"Design and explain an expert-level solution",
                f"Assess performance and identify the next advanced skill gap",
            ]

        milestone_prefix = "Build" if level == 1 else "Apply" if level == 2 else "Master"
        milestones = [
            f"{milestone_prefix} the core {goal} pattern with confidence",
            f"Complete a short {goal} assessment without major errors",
            f"Explain the correct reasoning behind one {goal} challenge",
        ]

        if self._feedback is not None:
            try:
                correction = await self._feedback.get_best_correction("learning_path", goal, current_level)
                if correction:
                    next_best_action = str(correction.get("next_best_action") or next_best_action)
                    if isinstance(correction.get("daily_plan"), list):
                        daily_plan = correction["daily_plan"]
                    if isinstance(correction.get("weekly_plan"), list):
                        weekly_plan = correction["weekly_plan"]
                    if isinstance(correction.get("milestones"), list):
                        milestones = correction["milestones"]
                    if "weekly_focus" in correction:
                        focus = str(correction["weekly_focus"])
            except Exception:
                pass

        return {
            "goal": goal,
            "current_level": current_level,
            "next_best_action": next_best_action,
            "daily_plan": daily_plan,
            "weekly_plan": weekly_plan,
            "weekly_focus": focus,
            "milestones": milestones,
            "recommendation": f"Focus on the next {current_level} stage of {goal} and keep practicing with real tasks based on your recent performance.",
            "mastery_score": round(mastery_score, 3),
            "progress_stage": "foundation" if mastery_score < 0.4 else "growth" if mastery_score < 0.75 else "expert",
        }

