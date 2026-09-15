from app.engines.knowledge_assessment import grade, questions_for

def test_programming_diagnostic_has_five_questions():
    assert len(questions_for("Python")) == 5

def test_diagnostic_assigns_advanced_for_full_score():
    qs = questions_for("Python")
    answers = [{"question_id": q["id"], "answer": q["answer"]} for q in qs]
    result = grade("Python", answers)
    assert result["score"] == 100.0
    assert result["level"] == "advanced"

def test_diagnostic_assigns_beginner_for_zero_score():
    qs = questions_for("Mathematics")
    answers = [{"question_id": q["id"], "answer": "not-the-answer"} for q in qs]
    result = grade("Mathematics", answers)
    assert result["level"] == "beginner"
