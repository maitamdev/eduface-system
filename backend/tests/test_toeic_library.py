"""Study-bank integrity and review/exam selection, independent of Mongo."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import pytest
from core.toeic_content import content, select_questions, study_catalog, validate_content, PART_COUNTS, public_question


def assert_whole_groups(rows):
    bank = content()["questions"]
    original = Counter(q.get("group_id", q["id"]) for q in bank)
    assert len({q["id"] for q in rows}) == len(rows)
    for group, size in Counter(q.get("group_id", q["id"]) for q in rows).items():
        assert size == original[group]


@pytest.mark.parametrize("topic", [t["id"] for t in content()["topics"]])
def test_topic_practice_is_targeted_keeps_context_and_copies_bank(topic):
    bank = content()["questions"]
    target_groups = {q.get("group_id", q["id"]) for q in bank if topic in q["topic_ids"]}
    for seed in (11, 41):
        rows = select_questions("topic", topic_id=topic, seed=seed)
        assert 0 < len(rows) <= 15
        assert all(q.get("group_id", q["id"]) in target_groups for q in rows)
        assert_whole_groups(rows)
        rows[0]["options"][0] = "changed copy"
        assert all("changed copy" not in q["options"] for q in bank)


@pytest.mark.parametrize("exam", [e["id"] for e in content()["exams"]])
def test_fixed_exam_membership_order_and_duration_are_pinned(exam):
    data = content()
    forms = json.loads((Path(__file__).resolve().parents[1]/"data/toeic/exam-forms.json").read_text(encoding="utf-8"))
    assert data["exams"] == forms
    descriptor = next(e for e in forms if e["id"] == exam)
    rows = select_questions("exam", exam_id=exam, seed=123)
    assert rows == select_questions("exam", exam_id=exam, seed=999)
    assert [q["id"] for q in rows] == descriptor["question_ids"]
    assert_whole_groups(rows)
    if descriptor["type"] == "full":
        assert Counter(q["part"] for q in rows) == PART_COUNTS
    assert descriptor["minutes"] == {"full":120,"mini":35,"listening":45,"reading":75}[descriptor["type"]]


def test_full_forms_are_disjoint_but_section_forms_are_disclosed_subsets():
    exams = {e["id"]:set(e["question_ids"]) for e in content()["exams"]}
    assert not exams["dhv-full-01-v1"] & exams["dhv-full-02-v1"]
    assert exams["dhv-listening-01-v1"] | exams["dhv-reading-01-v1"] == exams["dhv-full-01-v1"]


def test_review_keeps_sibling_context_and_respects_part_filter():
    bank = content()["questions"]
    first = next(q for q in bank if q["part"] == 3)
    other = next(q for q in bank if q["part"] == 5)
    rows = select_questions("review", part=3, mistake_ids={first["id"],other["id"]})
    assert len(rows) == 3 and all(q["group_id"] == first["group_id"] for q in rows)
    assert_whole_groups(rows)
    assert select_questions("review", mistake_ids={"removed-id"}) == []
    rows = select_questions("review", mistake_ids={q["id"] for q in bank}, seed=99)
    assert len(rows) <= 30
    assert_whole_groups(rows)


def test_large_lesson_is_a_manageable_sample_without_splitting_context():
    for lesson in ("lab-p3", "lab-p5", "lab-p7"):
        rows = select_questions("lesson", lesson_id=lesson, seed=91)
        assert 0 < len(rows) <= 30 and all(q["lesson_id"] == lesson for q in rows)
        assert_whole_groups(rows)
    assert len(select_questions("lesson", lesson_id="f01")) == 10


def test_public_catalog_and_active_questions_do_not_reveal_scored_answers():
    public = study_catalog(content())
    assert len(public["topics"]) == 38 and len(public["exams"]) == 9
    assert all(t["question_count"] > 0 for t in public["topics"])
    assert all("question_ids" not in e for e in public["exams"])
    evidence = next(q for q in content()["questions"] if q.get("evidence"))
    assert not {"evidence","correct","explanation","transcript"} & public_question(evidence).keys()
    assert public_question(evidence, review=True)["evidence"] == evidence["evidence"]
    assert public["topics"][0]["example"]["explanation"]  # Worked examples are intentionally public.


@pytest.mark.parametrize("fault", ["unknown_topic","wrong_part","empty_topic","split_group","unknown_exam_question","repeated_exam_question","duplicate_exam","unmatched_evidence","mismatched_transcript","bad_graphic"])
def test_malformed_library_fails_validation(fault):
    data = deepcopy(content())
    if fault == "unknown_topic": data["questions"][0]["topic_ids"] = ["not-a-topic"]
    if fault == "wrong_part": data["topics"][0]["part"] = 7
    if fault == "empty_topic": data["topics"][0]["rules"] = []
    if fault == "split_group":
        qid = next(qid for qid in data["exams"][0]["question_ids"] if next(q for q in data["questions"] if q["id"] == qid)["part"] == 3)
        data["exams"][0]["question_ids"].remove(qid)
    if fault == "unknown_exam_question": data["exams"][0]["question_ids"][0] = "not-a-question"
    if fault == "repeated_exam_question": data["exams"][0]["question_ids"][1] = data["exams"][0]["question_ids"][0]
    if fault == "duplicate_exam": data["exams"][1]["id"] = data["exams"][0]["id"]
    if fault == "unmatched_evidence": next(q for q in data["questions"] if q.get("evidence"))["evidence"] = "unsupported claim"
    if fault == "mismatched_transcript": next(q for q in data["questions"] if q["part"] == 3)["transcript"] = "different audio"
    if fault == "bad_graphic": next(q for q in data["questions"] if q.get("graphic"))["graphic"]["rows"][0].append("extra cell")
    with pytest.raises(AssertionError): validate_content(data)
