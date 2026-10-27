"""Versioned, original learning material. Public projections never expose answer keys."""
import copy
import json
import random
from collections import defaultdict
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
    return data


@lru_cache(maxsize=1)
def content():
    return validate_content(json.loads(DATA_PATH.read_text(encoding="utf-8")))


def public_question(q, review=False):
    hidden = set() if review else {"correct", "explanation", "transcript"}
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


def select_questions(kind, lesson_id=None, part=None, seed=None):
    data = content()
    rng = random.Random(seed)
    bank = data["questions"]
    if kind == "lesson":
        return copy.deepcopy([q for q in bank if q["lesson_id"] == lesson_id])
    if kind == "part":
        pool = [q for q in bank if q["part"] == part]
        count = {1: 6, 2: 10, 3: 9, 4: 9, 5: 10, 6: 8, 7: 10}[part]
        return copy.deepcopy(choose_groups(pool, count, rng))
    counts = PART_COUNTS if kind == "mock" else {1: 2, 2: 4, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5}
    selected = []
    for p, count in counts.items():
        selected.extend(choose_groups([q for q in bank if q["part"] == p], count, rng))
    return copy.deepcopy(selected)


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
