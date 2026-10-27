"""Versioned learning material with original and attributed MIT content. Public projections never expose answer keys."""
import copy
import json
import random
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "toeic" / "course.json"
PART_COUNTS = {1: 6, 2: 25, 3: 39, 4: 30, 5: 30, 6: 16, 7: 54}


def validate_curriculum(data):
    syllabus = data["curriculum"]
    lessons = {row["id"] for row in data["lessons"]}
    sources = {row["id"] for row in data["sources"]}
    levels = {row["id"] for row in syllabus["levels"]}
    sessions = syllabus["sessions"]
    assert len({row["id"] for row in sessions}) == len(sessions), "Duplicate curriculum session"
    assert len(levels) == len(syllabus["levels"]), "Duplicate curriculum level"
    for level in syllabus["levels"]:
        rows = [row for row in sessions if row["level_id"] == level["id"]]
        assert [row["number"] for row in rows] == list(range(1, level["session_count"] + 1)), "Invalid session sequence"
        assert set(level["checkpoints"]) <= {row["number"] for row in rows}, "Unknown checkpoint"
    for row in sessions:
        assert row["level_id"] in levels
        assert row["objectives"] and row["knowledge"] and row["examples"]
        assert row["practice"] and row["homework"] and row["vocabulary_focus"]
        assert row["lesson_ids"] and set(row["lesson_ids"]) <= lessons, "Unknown supporting lesson"
        assert row["source_ids"] and set(row["source_ids"]) <= sources, "Unknown curriculum source"
        assert sum(step["minutes"] for step in row["agenda"]) == row["minutes"], "Agenda duration mismatch"
        assert all(step["minutes"] > 0 and step["task"] for step in row["agenda"])
        assert len(row["checks"]) >= 2
        for check in row["checks"]:
            assert check["prompt"] and check["explanation"]
            assert len(set(check["options"])) == len(check["options"]) >= 3
            assert type(check["correct"]) is int and 0 <= check["correct"] < len(check["options"])
    return syllabus


def validate_content(data):
    validate_curriculum(data)
    lessons = {x["id"] for x in data["lessons"]}
    ids = set()
    for q in data["questions"]:
        assert q["id"] not in ids, f"Duplicate question: {q['id']}"
        ids.add(q["id"])
        assert q["lesson_id"] in lessons and q["part"] in PART_COUNTS
        assert 0 <= q["correct"] < len(q["options"]) and len(q["options"]) in (3, 4)
        assert len(set(q["options"])) == len(q["options"])
        assert q["explanation"] and q["prompt"]
        if q["part"] <= 4:
            assert q.get("audio_id") and q.get("transcript")
        if q["part"] == 1:
            assert q.get("image")
    assert len(lessons) == len(data["lessons"])
    cards = data["vocabulary"]
    assert len({c["id"] for c in cards}) == len(cards)
    assert all(c["lesson_id"] in lessons and c["meaning"] and c["example"] for c in cards)
    for part, minimum in PART_COUNTS.items():
        assert sum(q["part"] == part for q in data["questions"]) >= minimum
    for lesson in data["lessons"]:
        assert lesson["sections"] and any(q["lesson_id"] == lesson["id"] for q in data["questions"])
    validate_study_library(data)
    return data


def validate_study_library(data):
    bank = {q["id"]: q for q in data["questions"]}
    topics = {t["id"]: t for t in data["topics"]}
    assert len(topics) == len(data["topics"]), "Duplicate topic"
    sources = {s["id"] for s in data["sources"]}
    groups = defaultdict(list)
    for q in bank.values():
        assert q.get("topic_ids") and len(q["topic_ids"]) == len(set(q["topic_ids"])), "Missing or repeated study label"
        assert all(t in topics and topics[t]["part"] == q["part"] for t in q["topic_ids"]), "Unknown or mismatched topic"
        if q.get("group_id"):
            groups[q["group_id"]].append(q)
        if q.get("graphic"):
            g = q["graphic"]
            assert g["title"] and g["columns"] and g["rows"]
            assert all(len(row) == len(g["columns"]) and all(isinstance(cell, str) and cell for cell in row) for row in g["rows"]), "Malformed listening graphic"
        if q.get("evidence"):
            assert q["evidence"] in q.get("passage", ""), "Evidence absent from passage"
        if q["id"].startswith("oc-"):
            p = q["provenance"]
            assert p["license"] == "MIT" and p["upstream_id"] and len(p["revision"]) == 40
            assert p["revision"] in p["url"] and q["explanation"], "Incomplete source attribution"
    for rows in groups.values():
        for field in ("part", "lesson_id", "passage", "audio_id", "transcript", "graphic"):
            assert all(q.get(field) == rows[0].get(field) for q in rows), f"Incoherent group {rows[0]['group_id']}: {field}"
        if rows[0]["part"] in (3,4): assert len(rows) == 3, "Listening groups must have three questions"
        if rows[0]["part"] == 6: assert len(rows) == 4, "Part 6 groups must have four questions"
    for tid, t in topics.items():
        assert t["part"] in PART_COUNTS and t["title"] and t["recognition"]
        assert len(t["rules"]) >= 3 and len(t["steps"]) >= 3 and len(t["traps"]) >= 2
        assert t["example"]["text"] and t["example"]["explanation"]
        assert t["source_ids"] and set(t["source_ids"]) <= sources, "Unknown guide source"
        assert any(tid in q["topic_ids"] for q in bank.values()), "Guide has no practice"
    exams = data["exams"]
    assert len({e["id"] for e in exams}) == len(exams), "Duplicate exam code"
    full_ids = set()
    for exam in exams:
        ids = exam["question_ids"]
        assert len(set(ids)) == len(ids) and set(ids) <= bank.keys(), "Invalid exam membership"
        assert 0 < len(ids) <= 200 and 0 < exam["minutes"] <= 120
        counts = Counter(bank[qid]["part"] for qid in ids)
        assert counts == {p["part"]:p["count"] for p in exam["parts"]}, "Exam counts mismatch"
        assert [bank[qid]["part"] for qid in ids] == sorted(bank[qid]["part"] for qid in ids), "Exam parts out of order"
        for qid in ids:
            if gid := bank[qid].get("group_id"):
                assert {q["id"] for q in groups[gid]} <= set(ids), "Exam splits a group"
        if exam["type"] == "full":
            assert counts == PART_COUNTS and exam["minutes"] == 120
            assert not full_ids.intersection(ids), "Full exam forms overlap"
            full_ids.update(ids)
        elif exam["type"] in ("listening", "reading"):
            expected = {p:c for p,c in PART_COUNTS.items() if (p <= 4) == (exam["type"] == "listening")}
            assert counts == expected and exam["minutes"] == (45 if exam["type"] == "listening" else 75)
        else:
            assert exam["type"] == "mini" and len(ids) == 50 and len(counts) == 7 and exam["minutes"] == 35
    return data


@lru_cache(maxsize=1)
def content():
    return validate_content(json.loads(DATA_PATH.read_text(encoding="utf-8")))


def public_question(q, review=False):
    hidden = set() if review else {"correct", "explanation", "transcript", "evidence"}
    return {k: copy.deepcopy(v) for k, v in q.items() if k not in hidden}


def choose_groups(questions, count, rng):
    """Subset sum keeps every passage/dialogue intact while meeting section counts."""
    groups = defaultdict(list)
    for q in questions:
        groups[q.get("group_id", q["id"])].append(q)
    values = list(groups.values())
    rng.shuffle(values)
    combinations = {0: []}
    for group in values:
        for size, selected in list(combinations.items())[::-1]:
            target = size + len(group)
            if target <= count and target not in combinations:
                combinations[target] = selected + group
    if count not in combinations:
        raise ValueError(f"Cannot build a coherent section with {count} questions")
    return combinations[count]


def grouped_practice(bank, question_ids, rng, limit=15):
    """Include the complete context for a matched question, never split a set."""
    matches = {q.get("group_id", q["id"]) for q in bank if q["id"] in question_ids}
    groups = defaultdict(list)
    for q in bank:
        key = q.get("group_id", q["id"])
        if key in matches:
            groups[key].append(q)
    values = list(groups.values())
    rng.shuffle(values)
    selected = []
    for rows in values:
        if len(selected) + len(rows) <= limit:
            selected.extend(rows)
    return copy.deepcopy(selected)


def select_questions(kind, lesson_id=None, part=None, seed=None, *, topic_id=None, exam_id=None, mistake_ids=None):
    data = content()
    rng = random.Random(seed)
    bank = data["questions"]
    if kind == "exam":
        exam = next(e for e in data["exams"] if e["id"] == exam_id)
        lookup = {q["id"]: q for q in bank}
        return copy.deepcopy([lookup[qid] for qid in exam["question_ids"]])
    if kind == "topic":
        ids = {q["id"] for q in bank if topic_id in q.get("topic_ids", [])}
        return grouped_practice(bank, ids, rng)
    if kind == "review":
        ids = {q["id"] for q in bank if q["id"] in (mistake_ids or set()) and (part is None or q["part"] == part)}
        return grouped_practice(bank, ids, rng, limit=30)
    if kind == "lesson":
        pool = [q for q in bank if q["lesson_id"] == lesson_id]
        return grouped_practice(bank, {q["id"] for q in pool}, rng, limit=30) if len(pool) > 30 else copy.deepcopy(pool)
    if kind == "part":
        pool = [q for q in bank if q["part"] == part]
        count = {1: 6, 2: 10, 3: 9, 4: 9, 5: 10, 6: 8, 7: 10}[part]
        return copy.deepcopy(choose_groups(pool, count, rng))
    counts = PART_COUNTS if kind == "mock" else {1: 2, 2: 4, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5}
    selected = []
    for p, count in counts.items():
        selected.extend(choose_groups([q for q in bank if q["part"] == p], count, rng))
    return copy.deepcopy(selected)


def study_catalog(data):
    """Descriptions and counts are public; scored question membership stays server-side."""
    topics = [copy.deepcopy(t) | {"question_count": sum(t["id"] in q.get("topic_ids", []) for q in data["questions"])} for t in data.get("topics", [])]
    exams = [{k: copy.deepcopy(v) for k, v in e.items() if k != "question_ids"} |
             {"question_count": len(e["question_ids"])} for e in data.get("exams", [])]
    return {"topics": topics, "exams": exams}


def grade(questions, answers):
    correct = sum(answers.get(q["id"]) == q["correct"] for q in questions)
    parts = []
    for part in sorted({q["part"] for q in questions}):
        subset = [q for q in questions if q["part"] == part]
        score = sum(answers.get(q["id"]) == q["correct"] for q in subset)
        parts.append({"part": part, "correct": score, "total": len(subset), "percent": round(100 * score / len(subset))})
    percent = round(100 * correct / len(questions))
    return {"correct": correct, "total": len(questions), "percent": percent,
            "parts": parts, "suggested_stage": min(4, percent // 20),
            "score_notice": "Kết quả luyện tập nội bộ, không quy đổi thành điểm TOEIC chính thức."}
