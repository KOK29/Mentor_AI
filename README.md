# MentorSLM — Adaptive AI Tutor

MentorSLM is a tournament-ready education solution built around a **Small Language Model (SLM)**. It behaves like a teacher rather than a generic chatbot: it checks what a learner already knows, teaches at the right level, lets the learner attempt problems, analyzes mistakes, recommends trustworthy learning resources, and adapts the next learning step.

## Competition flow

**Sign up / Sign in → Email verification → Two-step verification → Learner profile → Topic search → Knowledge diagnostic → Student level → Teacher SLM → Teaching / Practice / Research / Assessment → Mistake analysis → Mastery → Next learning path**

## Core engines

- **Teacher SLM** — local Ollama-compatible SLM, default `qwen2.5:3b`, with deterministic demo fallback.
- **Teaching Engine** — level-aware explanation, examples, objectives, and next steps.
- **Practice Engine** — targeted exercises and hints.
- **Research Engine** — curated learning links and references for the selected topic.
- **Assessment Engine** — grading logic for quizzes/exams.
- **Mistake Analyzer** — identifies likely misconception and gives corrective steps instead of only revealing the answer.
- **Mastery Engine** — converts learning history into mastery signals.
- **Learning Path Engine** — recommends review, practice, or advancement.
- **Knowledge Assessment** — pre-learning diagnostic that places the learner at beginner/intermediate/advanced level.

## Why this is not a chatbot

The product is organized around a student model and learning state. The SLM is one component inside a controlled tutoring workflow. Deterministic code handles authentication, grading, progress, mastery, and progression; the SLM handles explanation, tutoring language, hints, and adaptive teaching.

## Repository structure

```text
MentorSLM/
├── backend/
│   ├── app/
│   │   ├── ai/                    # local SLM + fallback provider
│   │   ├── db/                    # users, diagnostics, progress
│   │   ├── engines/               # tutoring engines
│   │   ├── providers/sqlite/      # progress persistence
│   │   ├── schemas/               # API DTOs
│   │   ├── security/              # bcrypt, JWT, rate limiting
│   │   └── main.py                # FastAPI application
│   └── tests/
├── frontend/
│   └── src/                       # single coherent learner journey
├── docs/
├── .env.example
├── docker-compose.yml
└── README.md
```

## Local run

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy ..\.env.example ..\.env   # Windows
# cp ../.env.example ../.env    # macOS/Linux
uvicorn app.main:app --reload --port 8000
```

### 2. Optional local SLM

Install Ollama, then pull a small model:

```bash
ollama pull qwen2.5:3b
ollama serve
```

If Ollama is unavailable during judging, MentorSLM automatically uses its deterministic fallback so the product demo still works.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Demo OTP behavior

For a local tournament demo, `DEV_OTP_MODE=1` returns the 6-digit verification code in the API response and the UI displays it. This makes the authentication flow demonstrable without depending on an external email provider. **Set `DEV_OTP_MODE=0` before production deployment and connect an email/SMS delivery provider.**

## Security baseline

- bcrypt password hashing
- JWT access and refresh tokens
- email ownership verification flow
- two-step login challenge
- expiring one-time codes
- API rate limiting
- CORS configuration
- security headers
- no committed secrets

## Suggested 3-person ownership

- **AI / software:** SLM provider, teaching, practice, mistake analysis, orchestration.
- **Database / data science:** diagnostic scoring, student model, mastery, learning analytics.
- **Software / security:** authentication, verification, API security, deployment, exam integrity.

## Tournament demo script

1. Create an account and verify email.
2. Sign in with two-step verification.
3. Enter a learning goal in the learner profile.
4. Search **Python** and start the diagnostic.
5. Intentionally answer one or two questions incorrectly to show level placement.
6. Show the Teacher SLM lesson and research resources.
7. Intentionally choose a wrong practice answer to demonstrate the Mistake Analyzer.
8. Explain that quiz/exam results feed Mastery + Learning Path for the next lesson.

## Production extensions

Real email/SMS delivery, Redis-backed OTP challenges, vector database/RAG for uploaded ebooks, citation verification, larger diagnostic banks, exam mode, teacher/admin analytics, and model fine-tuning can be added without changing the core architecture.

## 2026 tournament merge upgrade

This clean edition combines the strongest ideas from the uploaded **MentorAI** and **Tutor AI / MentorSLM** projects into one architecture rather than shipping two competing applications.

### Added from MentorAI

- richer learner profile: education level, goal, and preferred learning style
- explicit Student Model endpoint that combines learner context, diagnostic level, strengths/weaknesses, mastery, streak, and recent history
- clearer learner-first progression from profile → topic → diagnostic → personalized learning

### Strengthened for judging

- fixed practice-set feedback so the Mistake Analyzer works with generated multi-lesson practice sets
- assessment results are now persisted automatically to the learner's progress history
- post-assessment mastery is recalculated and passed into the Learning Path Engine
- floating **Mentor AI** assistant guides learners toward concepts, roadmaps, practice, and next steps while using current topic/level/progress context
- clean distribution excludes `.env`, virtual environments, `node_modules`, compiled bundles, bytecode, and local databases
- retained deterministic AI fallback for reliable offline demos

### Why the assistant is not “just another chatbot”

The assistant is deliberately scoped to navigation and learning decisions. The actual product intelligence remains split across deterministic engines for diagnostic assessment, grading, progress, mastery, mistake analysis, and learning-path decisions, with the SLM used for teaching language and generated learning content.

## Judge-facing differentiation

A concise pitch for the system is:

> **MentorAI is an adaptive learning operating system: it diagnoses what a learner knows, builds a student model, teaches at the right level, analyzes mistakes, measures mastery, and continuously chooses the next best learning step.**

The strongest demo is not a long conversation with the AI. Show the closed learning loop:

**diagnose → personalize → teach → practice → detect misconception → assess → update mastery → recommend next step**.

That loop demonstrates a product architecture rather than a thin LLM wrapper.
