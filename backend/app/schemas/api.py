from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class TeachRequest(BaseModel):
    topic: str
    level: Optional[str] = "beginner"
    language: Optional[str] = "en"


class PracticeRequest(BaseModel):
    topic: str
    difficulty: Optional[str] = "medium"
    kind: Optional[str] = "mcq"


class MistakeAnalysisRequest(BaseModel):
    student_answer: str
    correct_answer: str
    context: Optional[str] = None


class ResearchRequest(BaseModel):
    q: str
    limit: Optional[int] = 5
