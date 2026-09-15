"""SQLite-backed progress repository.

Stores per-user learning history in the ``progress_entries`` table and
recomputes summary statistics on read (same logic as the former in-memory
helper functions in main.py).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import ProgressEntryModel


class SQLiteProgressRepository:
    """Persistent progress repository backed by SQLite."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def record(self, payload: dict) -> dict:
        user_id = str(payload.get("user_id") or "default-user")
        entry_model = ProgressEntryModel(
            user_id=user_id,
            topic=payload.get("topic", "General study"),
            level=payload.get("level", "beginner"),
            difficulty=payload.get("difficulty", "easy"),
            score=float(payload.get("score", 0)),
            correct=bool(payload.get("correct", False)),
            completed_at=datetime.now(timezone.utc).isoformat(),
        )
        self._session.add(entry_model)
        await self._session.flush()

        entry_dict = _model_to_dict(entry_model)
        summary = await self.get_summary(user_id)
        return {"message": "Progress recorded", "entry": entry_dict, "summary": summary}

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get_summary(self, user_id: Optional[str] = None) -> dict:
        if user_id:
            stmt = select(ProgressEntryModel).where(ProgressEntryModel.user_id == user_id)
        else:
            stmt = select(ProgressEntryModel)

        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return _build_summary(rows)

    async def get_profile(self, user_id: str) -> dict[str, Any]:
        result = await self._session.execute(
            select(ProgressEntryModel).where(ProgressEntryModel.user_id == user_id)
        )
        rows = result.scalars().all()

        # Build per-subject aggregates
        subjects: dict[str, dict] = {}
        for row in rows:
            topic = row.topic or "General study"
            subjects.setdefault(topic, {"sessions": 0, "score": 0.0, "correct": 0})
            subjects[topic]["sessions"] += 1
            subjects[topic]["score"] += row.score
            subjects[topic]["correct"] += 1 if row.correct else 0

        subjects_out = {
            key: {
                "sessions": val["sessions"],
                "average_score": round(val["score"] / val["sessions"], 2),
                "accuracy": round((val["correct"] / val["sessions"]) * 100, 2),
            }
            for key, val in subjects.items()
        }

        summary = _build_summary(rows)
        return {
            "user_id": user_id,
            "subjects": subjects_out,
            "total_sessions": summary["totalSessions"],
            "average_score": summary["averageScore"],
            "mastery": summary["mastery"],
            "streak": summary["streak"],
            "recent_history": summary["recentHistory"],
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _model_to_dict(model: ProgressEntryModel) -> dict:
    return {
        "user_id": model.user_id,
        "topic": model.topic,
        "level": model.level,
        "difficulty": model.difficulty,
        "score": model.score,
        "correct": model.correct,
        "completed_at": model.completed_at,
    }


def _build_summary(rows: list[ProgressEntryModel]) -> dict:
    if not rows:
        return {
            "totalSessions": 0,
            "averageScore": 0.0,
            "mastery": 0.0,
            "streak": 0,
            "recentHistory": [],
        }

    history = [_model_to_dict(r) for r in rows]
    total_sessions = len(history)
    average_score = sum(item["score"] for item in history) / total_sessions
    mastery = round(min(1.0, (average_score / 100) * 0.8 + 0.2), 3)

    recent_history = sorted(history, key=lambda item: item["completed_at"], reverse=True)[:5]

    streak = 0
    for item in sorted(history, key=lambda item: item["completed_at"], reverse=True):
        if item["correct"]:
            streak += 1
        else:
            break

    return {
        "totalSessions": total_sessions,
        "averageScore": round(average_score, 2),
        "mastery": mastery,
        "streak": streak,
        "recentHistory": recent_history,
    }
