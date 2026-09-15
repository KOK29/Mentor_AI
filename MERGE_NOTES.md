# Merge Notes

## Source decision

The FastAPI + React MentorSLM project was selected as the production foundation because it already had clear engine boundaries, JWT/bcrypt security, tests, Docker/CI files, and a modern frontend. The Flask MentorAI project's strongest learner-model concepts were integrated into that foundation.

## Important fixes and additions

1. Fixed the generated-practice object mismatch that could prevent practice answers from reaching the Mistake Analyzer.
2. Added `education_level` and `preferred_style` to the persisted learner profile.
3. Added `GET /api/v1/student-model` to expose a judge-friendly adaptive learner state.
4. Added `POST /api/v1/mentor/assist` for an in-product learning/navigation assistant.
5. Assessment grades now create persistent progress records.
6. The frontend recalculates mastery after assessment and requests a new adaptive learning path.
7. Added a bottom-right Mentor AI assistant UI.
8. Fixed TypeScript API-header typing and practice data types.
9. Removed generated/dependency/private artifacts from the deliverable.

## Validation performed

- Python source compilation: passed.
- Knowledge-assessment tests: 3 passed.
- React/TypeScript static type check: passed.
- Full backend dependency test suite was not executed in this environment because the system Python does not have the project's bcrypt dependency installed. Install `backend/requirements.txt` before running the complete suite.
- A complete Vite bundle was not produced in this Linux sandbox because the uploaded `node_modules` directory was created for Windows and lacked Rollup's Linux optional native package. A fresh `npm install`/`npm ci` on the target machine resolves that platform-specific dependency; TypeScript validation passed independently.
