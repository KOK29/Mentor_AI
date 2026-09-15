from __future__ import annotations
import datetime, hashlib, json, os, secrets, uuid
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .ai.local_slm_provider import LocalSLMProvider
from .db.models import DiagnosticResultModel, UserModel
from .db.session import get_db, init_db
from .engines.assessment.engine import AssessmentEngine
from .engines.knowledge_assessment import grade as grade_diagnostic, questions_for
from .engines.learning_path.engine import LearningPathEngine
from .engines.mastery.engine import MasteryEngine
from .engines.mistake_analyzer.engine import MistakeAnalyzer
from .engines.practice.engine import PracticeEngine
from .engines.research.engine import ResearchEngine
from .engines.teaching.engine import TeachingEngine
from .providers.sqlite.progress_repository import SQLiteProgressRepository
from .schemas.api import MistakeAnalysisRequest, PracticeRequest, TeachRequest
from .security.bcrypt_hasher import BcryptPasswordHasher
from .security.dependencies import get_current_user
from .security.jwt_token_service import JWTTokenService
from .security.middleware import RateLimitMiddleware

app = FastAPI(title="MentorSLM", version="1.0.0", description="Adaptive SLM-powered tutoring platform")
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["x-frame-options"] = "DENY"
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["referrer-policy"] = "strict-origin-when-cross-origin"
    return response

@app.on_event("startup")
async def startup() -> None:
    await init_db()

hasher = BcryptPasswordHasher()
tokens = JWTTokenService()
DEV_OTP = os.getenv("DEV_OTP_MODE", "1") == "1"
OTP_TTL = int(os.getenv("OTP_TTL_SECONDS", "300"))
_email_codes: dict[str, tuple[str, datetime.datetime]] = {}
_login_codes: dict[str, tuple[str, datetime.datetime]] = {}
_login_challenges: dict[str, str] = {}
_verified_challenges: set[str] = set()

TOPICS = [
    "Programming", "Python", "Computer Science", "Artificial Intelligence", "Data Science",
    "Cybersecurity", "Mathematics", "Statistics", "Physics", "Chemistry", "Biology",
    "English", "Business", "Finance", "Economics"
]

def otp_hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()

def make_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"

def store_otp(bucket: dict, key: str, code: str) -> None:
    bucket[key] = (otp_hash(code), datetime.datetime.utcnow() + datetime.timedelta(seconds=OTP_TTL))

def verify_otp(bucket: dict, key: str, code: str) -> bool:
    item = bucket.get(key)
    if not item:
        return False
    expected, expires = item
    if expires < datetime.datetime.utcnow() or not secrets.compare_digest(expected, otp_hash(code)):
        return False
    bucket.pop(key, None)
    return True

class RegisterIn(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class VerifyIn(BaseModel):
    email: EmailStr
    code: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TwoFactorIn(BaseModel):
    challenge_id: str
    code: str

class ProfileIn(BaseModel):
    full_name: Optional[str] = None
    learning_goal: Optional[str] = None
    education_level: Optional[str] = None
    preferred_style: Optional[str] = None
    locale: Optional[str] = None

class MentorAssistIn(BaseModel):
    message: str
    topic: Optional[str] = None
    level: Optional[str] = None

@app.get("/health")
async def health():
    return {"status": "ok", "service": "MentorSLM"}

@app.post("/api/v1/auth/register")
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db)):
    if len(payload.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    email = payload.email.lower().strip()
    existing = (await db.execute(select(UserModel).where(UserModel.email == email))).scalar_one_or_none()
    if existing:
        raise HTTPException(409, "Email already registered")
    user = UserModel(
        id=str(uuid.uuid4()), username=email, full_name=payload.full_name.strip() or "Learner",
        email=email, hashed_password=hasher.hash_password(payload.password), email_verified=False,
        two_factor_enabled=True,
    )
    db.add(user); await db.commit()
    code = make_otp(); store_otp(_email_codes, email, code)
    result = {"email": email, "verification_required": True}
    if DEV_OTP: result["dev_code"] = code
    return result

@app.post("/api/v1/auth/verify-email")
async def verify_email(payload: VerifyIn, db: AsyncSession = Depends(get_db)):
    email = payload.email.lower().strip()
    if not verify_otp(_email_codes, email, payload.code):
        raise HTTPException(400, "Invalid or expired verification code")
    user = (await db.execute(select(UserModel).where(UserModel.email == email))).scalar_one_or_none()
    if not user: raise HTTPException(404, "Account not found")
    user.email_verified = True; await db.commit()
    return {"verified": True}

@app.post("/api/v1/auth/login")
async def login(payload: LoginIn, db: AsyncSession = Depends(get_db)):
    email = payload.email.lower().strip()
    user = (await db.execute(select(UserModel).where(UserModel.email == email))).scalar_one_or_none()
    if not user or not hasher.verify_password(payload.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    if not user.email_verified:
        raise HTTPException(403, "Verify your email before signing in")
    challenge = secrets.token_urlsafe(24); code = make_otp(); store_otp(_login_codes, challenge, code)
    _login_challenges[challenge] = email
    result = {"two_factor_required": True, "challenge_id": challenge}
    if DEV_OTP: result["dev_code"] = code
    return result

@app.post("/api/v1/auth/verify-2fa")
async def verify_2fa(payload: TwoFactorIn, db: AsyncSession = Depends(get_db)):
    if not verify_otp(_login_codes, payload.challenge_id, payload.code):
        raise HTTPException(400, "Invalid or expired two-step code")
    if payload.challenge_id not in _login_challenges:
        raise HTTPException(400, "Unknown sign-in challenge")
    _verified_challenges.add(payload.challenge_id)
    return {"verified": True, "challenge_id": payload.challenge_id}

class CompleteLoginIn(BaseModel):
    challenge_id: str

@app.post("/api/v1/auth/complete-login")
async def complete_login(payload: CompleteLoginIn, db: AsyncSession = Depends(get_db)):
    if payload.challenge_id not in _verified_challenges:
        raise HTTPException(401, "Two-step verification required")
    email = _login_challenges.pop(payload.challenge_id, None)
    _verified_challenges.discard(payload.challenge_id)
    if not email:
        raise HTTPException(401, "Invalid sign-in challenge")
    user = (await db.execute(select(UserModel).where(UserModel.email == email))).scalar_one_or_none()
    if not user or not user.email_verified:
        raise HTTPException(401, "Unable to complete sign in")
    return {"access_token": tokens.create_access_token(email), "refresh_token": tokens.create_refresh_token(email), "token_type": "bearer"}

async def current_db_user(current_user: str, db: AsyncSession) -> UserModel:
    user = (await db.execute(select(UserModel).where(UserModel.email == current_user))).scalar_one_or_none()
    if not user: raise HTTPException(404, "User not found")
    return user

@app.get("/api/v1/profile")
async def profile(current_user: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await current_db_user(current_user, db)
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "learning_goal": user.learning_goal, "education_level": user.education_level, "preferred_style": user.preferred_style, "locale": user.locale}

@app.patch("/api/v1/profile")
async def update_profile(payload: ProfileIn, current_user: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await current_db_user(current_user, db)
    if payload.full_name is not None: user.full_name = payload.full_name.strip()[:120]
    if payload.learning_goal is not None: user.learning_goal = payload.learning_goal.strip()[:300]
    if payload.education_level is not None: user.education_level = payload.education_level.strip()[:80]
    if payload.preferred_style is not None: user.preferred_style = payload.preferred_style.strip()[:120]
    if payload.locale is not None: user.locale = payload.locale.strip()[:20]
    await db.commit()
    return {"saved": True, "full_name": user.full_name, "learning_goal": user.learning_goal, "education_level": user.education_level, "preferred_style": user.preferred_style, "locale": user.locale}


@app.get("/api/v1/student-model")
async def student_model(current_user: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await current_db_user(current_user, db)
    progress = await SQLiteProgressRepository(db).get_profile(current_user)
    latest = (await db.execute(
        select(DiagnosticResultModel).where(DiagnosticResultModel.user_id == user.id).order_by(DiagnosticResultModel.created_at.desc())
    )).scalars().first()
    return {
        "learner": {
            "full_name": user.full_name,
            "education_level": user.education_level,
            "learning_goal": user.learning_goal,
            "preferred_style": user.preferred_style,
        },
        "diagnostic": None if not latest else {
            "topic": latest.topic, "score": latest.score, "level": latest.level,
            "strengths": json.loads(latest.strengths_json or "[]"),
            "weaknesses": json.loads(latest.weaknesses_json or "[]"),
        },
        "progress": progress,
        "readiness": "building" if progress["total_sessions"] < 3 else ("strong" if progress["mastery"] >= 0.75 else "developing"),
    }

@app.post("/api/v1/mentor/assist")
async def mentor_assist(payload: MentorAssistIn, current_user: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await current_db_user(current_user, db)
    progress = await SQLiteProgressRepository(db).get_profile(current_user)
    topic = (payload.topic or "the current topic").strip()
    level = (payload.level or "beginner").strip()
    message = payload.message.strip()[:600]
    lower = message.lower()
    if any(word in lower for word in ("career", "roadmap", "become", "path")):
        answer = f"For your goal '{user.learning_goal or 'build strong skills'}', focus on foundations first, then projects, then assessment. For {topic}, I recommend: learn the core concepts, complete guided practice, build one small project, and use your assessment result to choose the next topic."
        actions = ["Open the Teaching tab", "Complete one Practice set", "Take the Assessment", "Review the next learning path"]
    elif any(word in lower for word in ("stuck", "don't understand", "dont understand", "help", "confused")):
        answer = f"You are working at {level} level in {topic}. Start with one concept at a time: restate the rule in your own words, inspect the worked example, then try a similar problem without looking. If you miss it, use the Mistake Analyzer before moving on."
        actions = ["Review the current lesson", "Try one problem", "Use mistake feedback"]
    else:
        mastery = round(float(progress.get("mastery", 0)) * 100)
        answer = f"I can guide you through {topic}. Your recorded mastery is {mastery}%. Ask me for a concept explanation, study roadmap, practice strategy, or what to do next."
        actions = ["Explain a concept", "Build a roadmap", "Suggest next step"]
    return {"answer": answer, "suggested_actions": actions, "context": {"topic": topic, "level": level, "mastery": progress.get("mastery", 0)}}

@app.get("/api/v1/topics/search")
async def search_topics(q: str = "", _: str = Depends(get_current_user)):
    needle = q.strip().lower()
    matches = [t for t in TOPICS if not needle or needle in t.lower()]
    return {"query": q, "topics": matches[:12]}

@app.get("/api/v1/diagnostic/questions")
async def diagnostic_questions(topic: str, _: str = Depends(get_current_user)):
    public = [{k:v for k,v in q.items() if k != "answer"} for q in questions_for(topic)]
    return {"topic": topic, "questions": public}

@app.post("/api/v1/diagnostic/grade")
async def diagnostic_grade(payload: dict, current_user: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    topic = str(payload.get("topic") or "General")
    result = grade_diagnostic(topic, payload.get("answers") or [])
    user = await current_db_user(current_user, db)
    db.add(DiagnosticResultModel(user_id=user.id, topic=topic, score=result["score"], level=result["level"], strengths_json=json.dumps(result["strengths"]), weaknesses_json=json.dumps(result["weaknesses"])))
    await db.commit()
    return result

def ai_provider():
    return LocalSLMProvider()

@app.post("/api/v1/teach")
async def teach(req: TeachRequest, _: str = Depends(get_current_user)):
    return await TeachingEngine(ai_provider()).teach(req.topic, level=req.level, language=req.language)

@app.post("/api/v1/practice")
async def practice(req: PracticeRequest, _: str = Depends(get_current_user)):
    return await PracticeEngine(ai_provider()).generate_exercise(req.topic, difficulty=req.difficulty, kind=req.kind)

@app.post("/api/v1/mistakes/analyze")
async def mistake(req: MistakeAnalysisRequest, _: str = Depends(get_current_user)):
    return await MistakeAnalyzer(ai_provider()).analyze(req.student_answer, req.correct_answer, context=req.context)

@app.get("/api/v1/research")
async def research(q: str, limit: int = 5, _: str = Depends(get_current_user)):
    return await ResearchEngine(ai_provider()).search(q, limit=limit)

@app.post("/api/v1/assessment/grade")
async def assessment(answers: list[dict], current_user: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await AssessmentEngine().grade(answers)
    if answers:
        topic = str(answers[0].get("topic") or "General study")
        score_pct = round(float(result.get("score", 0)) * 100, 2)
        await SQLiteProgressRepository(db).record({
            "user_id": current_user, "topic": topic, "level": "assessment",
            "difficulty": "adaptive", "score": score_pct, "correct": score_pct >= 70,
        })
    return result

@app.post("/api/v1/mastery/calculate")
async def mastery(attempts: list[dict], _: str = Depends(get_current_user)):
    return await MasteryEngine().calculate(attempts)

@app.post("/api/v1/learning-path/recommend")
async def learning_path(payload: Optional[dict] = None, _: str = Depends(get_current_user)):
    data = payload or {}
    return await LearningPathEngine().recommend(str(data.get("goal") or "general learning"), str(data.get("current_level") or "beginner"), mastery=float(data["mastery"]) if data.get("mastery") is not None else None, recent_history=data.get("recent_history") or [])

@app.post("/api/v1/progress/record")
async def record_progress(payload: dict, current_user: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    payload = {**payload, "user_id": current_user}
    return await SQLiteProgressRepository(db).record(payload)

@app.get("/api/v1/progress")
async def get_progress(current_user: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await SQLiteProgressRepository(db).get_summary(current_user)
