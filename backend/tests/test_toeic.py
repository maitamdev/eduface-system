from collections import Counter
from pathlib import Path
import json
import pytest
from pydantic import ValidationError
from core.toeic_content import content, select_questions, public_question, grade, PART_COUNTS
from routers.toeic import Answers, Review, Start, validated_answers
from fastapi import HTTPException
from uuid import uuid4


def test_complete_course_and_public_preview_have_no_answer_keys():
    data = content()
    assert (len(data["lessons"]), len(data["questions"]), len(data["vocabulary"])) == (20,268,200)
    preview = json.loads((Path(__file__).resolve().parents[2]/"frontend/src/features/toeic/previewCatalog.json").read_text(encoding="utf-8"))
    assert "questions" not in preview
    assert len(preview["lessons"]) == 20
    for q in data["questions"]:
        public = public_question(q)
        assert not {"correct", "explanation", "transcript"} & public.keys()
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
