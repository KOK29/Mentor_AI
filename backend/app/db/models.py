"""Core database models for MentorSLM."""
from __future__ import annotations
import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False, default="Learner")
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    two_factor_enabled = Column(Boolean, nullable=False, default=True)
    locale = Column(String, nullable=False, default="en")
    learning_goal = Column(String, nullable=False, default="")
    education_level = Column(String, nullable=False, default="")
    preferred_style = Column(String, nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class ProgressEntryModel(Base):
    __tablename__ = "progress_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    topic = Column(String, nullable=False, default="General study")
    level = Column(String, nullable=False, default="beginner")
    difficulty = Column(String, nullable=False, default="easy")
    score = Column(Float, nullable=False, default=0.0)
    correct = Column(Boolean, nullable=False, default=False)
    completed_at = Column(String, nullable=False)

class DiagnosticResultModel(Base):
    __tablename__ = "diagnostic_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    topic = Column(String, nullable=False, index=True)
    score = Column(Float, nullable=False)
    level = Column(String, nullable=False)
    strengths_json = Column(Text, nullable=False, default="[]")
    weaknesses_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
