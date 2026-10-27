from collections import Counter
from pathlib import Path
import json
import pytest
from pydantic import ValidationError
from core.toeic_content import content, select_questions, public_question, grade, PART_COUNTS, validate_curriculum
from routers.toeic import Answers, Review, Start, validated_answers, SessionCompletion
from fastapi import HTTPException
from uuid import uuid4


def test_complete_course_and_public_preview_have_no_answer_keys():
    data = content()
    assert (len(data["lessons"]), len(data["questions"]), len(data["vocabulary"])) == (27,727,200)
    preview = json.loads((Path(__file__).resolve().parents[2]/"frontend/src/features/toeic/previewCatalog.json").read_text(encoding="utf-8"))
    assert "questions" not in preview
    assert len(preview["lessons"]) == 27
    for q in data["questions"]:
        public = public_question(q)
        assert not {"correct", "explanation", "transcript", "evidence"} & public.keys()
        assert public_question(q, review=True)["correct"] == q["correct"]


@pytest.mark.parametrize("kind,part", [("mock",None),("diagnostic",None)]+[("part",p) for p in range(1,8)])
def test_generated_attempts_preserve_whole_passage_groups(kind, part):
    bank = content()["questions"]
    group_sizes = Counter(q.get("group_id",q["id"]) for q in bank)
    for seed in range(10):
        rows = select_questions(kind,part=part,seed=seed)
        assert len({q["id"] for q in rows}) == len(rows)
        for group,size in Counter(q.get("group_id",q["id"]) for q in rows).items():
            assert size == group_sizes[group]
        if kind == "mock": assert Counter(q["part"] for q in rows) == PART_COUNTS
        if kind == "diagnostic": assert len(rows) == 25


def test_server_grades_unanswered_and_per_part_without_scaled_score():
    rows = select_questions("diagnostic", seed=42)
    answers = {q["id"]:q["correct"] for q in rows[:10]}
    result = grade(rows,answers)
    assert (result["correct"],result["total"],result["percent"]) == (10,25,40)
    assert sum(p["correct"] for p in result["parts"]) == 10
    assert "score" not in result and result["suggested_stage"] == 2


@pytest.mark.parametrize("answers", [{"f01-q01":True},{"f01-q01":"1"},{"f01-q01":-1},{"f01-q01":4}])
def test_answer_schema_rejects_coerced_and_invalid_choices(answers):
    with pytest.raises(ValidationError): Answers(answers=answers)


def test_answer_validation_checks_membership_and_option_count():
    rows=select_questions("lesson","f01")
    with pytest.raises(HTTPException): validated_answers({"questions":rows},{"unknown":0})
    with pytest.raises(HTTPException): validated_answers({"questions":rows},{rows[0]["id"]:3})
    assert validated_answers({"questions":rows},{rows[0]["id"]:None}) == {rows[0]["id"]:None}


def test_review_rejects_bool_and_out_of_range_rating():
    for rating in (True,0,5,"3"):
        with pytest.raises(ValidationError): Review(rating=rating,expected_version=0,event_id=uuid4())


def test_listening_option_letters_match_authored_audio_transcripts():
    for q in content()["questions"]:
        if q["part"] <= 2:
            for i, option in enumerate(q["options"]): assert f"{chr(65+i)}. {option}" in q["transcript"]


def test_curriculum_covers_requested_levels_and_has_reusable_learning_resources():
    data = content()
    syllabus = validate_curriculum(data)
    assert [l["session_count"] for l in syllabus["levels"]] == [24, 12, 12, 8]
    assert len(syllabus["sessions"]) == 56
    assert sum(len(s["checks"]) for s in syllabus["sessions"]) == 112
    assert sum(s["minutes"] for s in syllabus["sessions"]) == 5130
    assert sum(s["minutes"] == 120 for s in syllabus["sessions"]) == 3
    assert {s["id"] for s in syllabus["sessions"] if s["level_id"] == "level-1"} == {f"l1-s{n:02}" for n in range(1,25)}
    assert "Final test" in next(s["title"] for s in syllabus["sessions"] if s["id"] == "l1-s24")
    assert "Announcement" in next(s["title"] for s in syllabus["sessions"] if s["id"] == "l2-s12")
    # The self-check keys are intentionally visible study material, independent of
    # the scored bank; adding a syllabus must not expose bank question answers.
    assert not ({q["id"] for q in data["questions"]} & {s["id"] for s in syllabus["sessions"]})


@pytest.mark.parametrize("field,value", [
    ("source_ids", ["not-a-source"]), ("lesson_ids", ["not-a-lesson"]),
    ("minutes", 999), ("number", 99), ("knowledge", []),
])
def test_curriculum_validation_rejects_broken_learning_paths(field, value):
    from copy import deepcopy
    data = deepcopy(content())
    data["curriculum"]["sessions"][0][field] = value
    with pytest.raises(AssertionError):
        validate_curriculum(data)


@pytest.mark.parametrize("value", ["true", 1, None])
def test_session_completion_requires_an_explicit_boolean(value):
    with pytest.raises(ValidationError):
        SessionCompletion(completed=value)
