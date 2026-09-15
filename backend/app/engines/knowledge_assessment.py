"""Entry diagnostic used before the Teacher SLM starts tutoring."""
from __future__ import annotations

QUESTION_BANK = {
    "programming": [
        {"id":"p1","skill":"fundamentals","question":"What is a variable primarily used for?","options":["Store a value","Repeat code forever","Encrypt a file","Draw a network"],"answer":"Store a value"},
        {"id":"p2","skill":"control-flow","question":"Which construct is used to choose between conditions?","options":["if/else","import","class only","comment"],"answer":"if/else"},
        {"id":"p3","skill":"loops","question":"What does a loop help you do?","options":["Repeat a block of work","Delete the compiler","Create hardware","Avoid all conditions"],"answer":"Repeat a block of work"},
        {"id":"p4","skill":"functions","question":"Why are functions useful?","options":["Reuse organized logic","Only store images","Replace databases","Disable errors"],"answer":"Reuse organized logic"},
        {"id":"p5","skill":"debugging","question":"What is debugging?","options":["Finding and fixing defects","Designing a logo","Compressing a PDF","Buying a server"],"answer":"Finding and fixing defects"},
    ],
    "mathematics": [
        {"id":"m1","skill":"arithmetic","question":"What is 12 × 4?","options":["48","36","42","52"],"answer":"48"},
        {"id":"m2","skill":"algebra","question":"If x + 7 = 12, what is x?","options":["5","19","7","12"],"answer":"5"},
        {"id":"m3","skill":"fractions","question":"Which is equal to 1/2?","options":["0.5","0.2","1.5","2.0"],"answer":"0.5"},
        {"id":"m4","skill":"geometry","question":"How many degrees are in a right angle?","options":["90","45","180","360"],"answer":"90"},
        {"id":"m5","skill":"reasoning","question":"If all A are B and x is A, what must be true?","options":["x is B","x is not B","B is empty","Nothing follows"],"answer":"x is B"},
    ],
}

GENERIC = [
    {"id":"g1","skill":"concepts","question":"Which response best shows understanding of a topic?","options":["Explain it in your own words","Memorize only the title","Skip every example","Avoid practice"],"answer":"Explain it in your own words"},
    {"id":"g2","skill":"application","question":"What is the strongest evidence that you can apply a concept?","options":["Solve a new problem with it","Recognize its name","See it once","Copy a definition"],"answer":"Solve a new problem with it"},
    {"id":"g3","skill":"analysis","question":"When two sources disagree, what should you do first?","options":["Compare evidence and credibility","Pick the shorter one","Ignore both","Choose randomly"],"answer":"Compare evidence and credibility"},
    {"id":"g4","skill":"practice","question":"What should happen after a repeated mistake?","options":["Review the misconception and retry","Hide the result","Increase speed only","Skip the topic forever"],"answer":"Review the misconception and retry"},
    {"id":"g5","skill":"reflection","question":"Which action best supports long-term mastery?","options":["Review weak areas over time","Study once only","Avoid testing","Never revisit mistakes"],"answer":"Review weak areas over time"},
]

def questions_for(topic: str) -> list[dict]:
    key = topic.strip().lower()
    if "program" in key or "python" in key or "code" in key:
        return QUESTION_BANK["programming"]
    if "math" in key or "algebra" in key or "calculus" in key:
        return QUESTION_BANK["mathematics"]
    return GENERIC

def grade(topic: str, answers: list[dict]) -> dict:
    questions = questions_for(topic)
    keyed = {q["id"]: q for q in questions}
    correct = 0
    strengths, weaknesses = [], []
    for item in answers:
        q = keyed.get(str(item.get("question_id")))
        if not q:
            continue
        ok = str(item.get("answer")) == q["answer"]
        correct += int(ok)
        (strengths if ok else weaknesses).append(q["skill"])
    score = round((correct / max(len(questions), 1)) * 100, 1)
    level = "advanced" if score >= 80 else "intermediate" if score >= 50 else "beginner"
    return {"score": score, "level": level, "strengths": sorted(set(strengths)), "weaknesses": sorted(set(weaknesses))}
