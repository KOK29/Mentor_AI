# MentorSLM Architecture

```text
Student
  │
  ▼
Sign up / Sign in
  │
  ├── Email Verification
  └── Two-Step Verification
  │
  ▼
Learner Profile
  │
  ▼
Topic Search
  │
  ▼
Knowledge Diagnostic
  │
  ▼
Student Model (starting level + strengths + weaknesses)
  │
  ▼
Teacher SLM
  │
  ├──────────────┬──────────────┬──────────────┐
  ▼              ▼              ▼              ▼
Teaching       Practice       Research       Assessment
Engine         Engine         Engine         Engine
  │              │              │              │
  │              ▼              │              │
  │        Mistake Analyzer     │              │
  │              │              │              │
  └──────────────┴──────────────┴──────────────┘
                         │
                         ▼
                    Mastery Engine
                         │
                         ▼
                  Learning Path Engine
                         │
                         ▼
                 Review / Advance / Next Topic
```

## Design principle

The SLM does not own high-stakes state. Authentication, answer scoring, progress recording, mastery calculations, and progression rules are deterministic. The SLM is used for language-rich tutoring: explanations, Socratic hints, examples, and misconception-oriented feedback.
