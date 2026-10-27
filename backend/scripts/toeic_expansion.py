"""Curate licensed questions, attach reviewed Vietnamese teaching notes, and build
fixed exam forms. All inputs are local and pinned; the app never scrapes at runtime.
"""
import copy
import hashlib
import json
import random
import re
import sys
from pathlib import Path

from toeic_ocean_vi import REVIEWS, EXCLUDED
from toeic_topics import TOPICS
from toeic_extra_questions import EXTRA

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from core.toeic_content import choose_groups, PART_COUNTS


def arrange_options(q):
    correct = q["options"][q["correct"]]
    random.Random(hashlib.sha256(q["id"].encode()).hexdigest()).shuffle(q["options"])
    q["correct"] = q["options"].index(correct)
    if q["part"] <= 2:
        q["transcript"] += "\n" + "\n".join(f"{chr(65+i)}. {answer}" for i, answer in enumerate(q["options"]))
    return q


def tag_original_questions(bank):
    """Add study labels without changing legacy IDs, wording, keys or audio."""
    grammar = {
        "f02": ["agreement","word-form","word-form","word-form","infinitive","quantity","quantity","pronouns","agreement","word-form","infinitive","quantity"],
        "b03": ["agreement","tense","preposition","passive","tense","tense","agreement","preposition","tense","tense","agreement","vocabulary"],
        "i03": ["passive","relative","conjunction","conjunction","relative","passive","conjunction","relative","conjunction","relative"],
        "u03": ["vocabulary","vocabulary","conjunction","conjunction","advanced","preposition","word-form","conjunction","preposition","advanced"],
    }
    for q in bank:
        part, prompt = q["part"], q["prompt"].lower()
        if part == 1:
            tag = "scene" if q["id"] in {f"b01-q{i:02}" for i in (4,5,6,7)} else "actions"
        elif part == 2:
            opening = q["transcript"].split("A.")[0].lower()
            tag = "choice" if re.search(r"\bor\b", opening) else "request" if re.search(r"\b(could you|would you|can you|let's|shall we)\b", opening) else "wh" if re.search(r"\b(what|where|when|why|who|which|how)\b", opening) else "yesno" if re.search(r"\b(is|are|do|does|did|have|has|will|would|can|could)\b", opening) else "indirect"
        elif part in (3,4):
            if part == 3 and any(x in prompt for x in ("imply", "mean by")):
                tag = "intent"
            elif any(x in prompt for x in ("do next", "do after", "asked to", "should the", "suggest", "will the man do", "will the woman do")):
                tag = "next" if part == 3 else "action"
            elif any(x in prompt for x in ("mainly", "purpose", "most likely take place", "who is the speaker", "who most likely", "where does")):
                tag = "overview" if part == 3 else "purpose"
            else:
                tag = "detail"
        elif part == 5:
            tag = grammar[q["lesson_id"]][int(q["id"].split("-q")[-1])-1] if q["lesson_id"] in grammar else "vocabulary"
        elif part == 6:
            tag = "insertion" if all(len(o.split()) >= 6 for o in q["options"]) else "linking" if q["options"][q["correct"]].lower().strip("., ") in {"however","therefore","otherwise","in addition","furthermore","nevertheless","meanwhile","consequently"} else "grammar"
        else:
            tag = "vocabulary" if "closest" in prompt or "word" in prompt and "mean" in prompt else "inference" if any(x in prompt for x in ("infer", "implied", "conclude", "suggest", "most likely")) else "purpose" if "purpose" in prompt or "mainly" in prompt else "detail"
        q["topic_ids"] = [f"p{part}-{tag}"]


def expand_course(data):
    tag_original_questions(data["questions"])
    snapshot = json.loads((ROOT / "backend/data/toeic/vendor/ocean-snapshot.json").read_text(encoding="utf-8"))
    raw = []
    for filename, pack in snapshot["files"].items():
        source = pack["data"]
        if "questions" in source:
            # The old upstream Part 6 has separate one-blank excerpts under the
            # same group ID. Use the newer coherent four-question passages instead.
            raw.extend((filename, row) for row in source["questions"] if row["part"] != "6")
        for key, part in (("part6Groups", 6), ("readingGroups", 7)):
            for group in source.get(key, []):
                for row in group["questions"]:
                    raw.append((filename, row | {"part": str(part), "passage": group["passage"], "groupId": group["groupId"]}))
        raw.extend((filename, row | {"part": "1"}) for row in source.get("items", []))
    imported = []
    for filename, row in raw:
        if row["id"] in EXCLUDED:
            continue
        note = REVIEWS[row["id"]]  # Fail the build if any item has no reviewed translation.
        part = int(row["part"])
        qid = "oc-" + row["id"].lower()
        q = {"id": qid, "lesson_id": f"lab-p{part}", "part": part,
            "prompt": row.get("prompt", "Choose the statement that best describes the picture."),
            "options": list(row["choices"]), "correct": row["answer"],
            "explanation": note["explanation"], "topic_ids": [note["topic"]],
            "provenance": {"provider": "TOEIC Question Ocean / DHV", "kind": "adapted", "license": "MIT",
                "upstream_id": row["id"], "revision": snapshot["revision"],
                "url": f"{snapshot['repository']}/blob/{snapshot['revision']}/{filename}"}}
        if row["id"] == "P3-012":
            q["options"][row["answer"]] = "Update a room reservation and contact a team"
        if row["id"] == "P1-016":
            q["options"][row["answer"]] = "Two people are looking at a transit map."
        if row.get("groupId"):
            q["group_id"] = "oc-" + row["groupId"].lower()
        if row.get("passage"):
            q["passage"] = row["passage"]
        if row.get("evidence"):
            assert row["evidence"] in row["passage"]
            q["evidence"] = row["evidence"]
        if part <= 4:
            q["audio_id"] = q.get("group_id", qid)
            q["transcript"] = re.sub(r"\b([WM]):\s*", lambda m: "\n" + ("Woman: " if m[1] == "W" else "Man: "), row.get("audioText", "")).strip()
        if part == 1:
            q["transcript"] = "Look at the picture."
            q["image"] = "/toeic/images/ocean-" + Path(row["image"]).name
            q["image_credit"] = "Ảnh mô phỏng tạo bằng AI · TOEIC Question Ocean · MIT"
        # Closely related skills can share an item while retaining whole contexts.
        if note["topic"] == "p5-relative" and row["id"] in {"P5-074", "P5-083", "P5-115"}:
            q["topic_ids"].append("p5-passive")
        if row["id"] in {"P2-032", "P2-037", "P2-052", "P2-068"}:
            q["topic_ids"].append("p2-indirect")
        imported.append(arrange_options(q))
    data["questions"].extend(imported)
    data["questions"].extend(arrange_options(copy.deepcopy(q)) for q in EXTRA)
    data["topics"] = copy.deepcopy(TOPICS)
    for part, title in enumerate(["Hình và hành động", "Phản hồi trong giao tiếp", "Hiểu hội thoại công việc", "Nghe thông báo và hướng dẫn", "Ngữ pháp và từ vựng trong câu", "Mạch văn bản và câu nối", "Đọc bằng chứng và đối chiếu nguồn"], 1):
        guides = [t for t in TOPICS if t["part"] == part]
        data["lessons"].append({"id": f"lab-p{part}", "stage": 1 if part <= 2 else 2 if part <= 5 else 3,
            "title": f"Chuyên đề Part {part} · {title}", "part": part, "minutes": 45,
            "objectives": ["Nhận diện các dạng câu hỏi và chọn cách xử lý phù hợp.", "Giải thích đáp án bằng ngữ pháp hoặc bằng chứng cụ thể.", "Dùng mục Ôn theo dạng để luyện từng kỹ năng rồi mở đề tổng hợp."],
            "sections": [{"title": t["title"], "body": "\n\n".join([t["recognition"], *t["rules"], "Cách làm: " + " → ".join(t["steps"]), "Tránh lỗi: " + " ".join(t["traps"]), t["example"]["text"], t["example"]["explanation"]])} for t in guides],
            "practice_rule": "Ôn một dạng trong mục Ôn theo dạng, làm bài tối đa 15 câu kèm ngữ cảnh rồi xem lời giải. Nếu luyện cả chuyên đề, mỗi lượt lấy tối đa 30 câu từ ngân hàng và giữ trọn nhóm. Đồng hồ đặt theo số câu; các lượt có thể lặp câu đã học."})
    data["sources"].append({"id": "ocean-mit", "title": "TOEIC Question Ocean · nguồn MIT được chọn lọc", "url": snapshot["repository"], "provider": "Chun-Hsiung Luo / DHV", "access": "MIT · có bản ghi nguồn và điều chỉnh", "stage": "Ôn dạng bài / đề luyện", "usage": "Đã nhập phần nội dung tự biên soạn được cấp phép MIT, bổ sung lời giải tiếng Việt và loại câu có vấn đề. Ảnh mới là cảnh tạo bằng AI từ nguồn; audio được tạo lại từ transcript. Xem thông báo MIT và ghi nguồn ở chân mục ôn tập."})
    data["expansion"] = {"version": "2026.10-v3", "adapted_questions": len(imported), "original_questions": len(EXTRA),
        "upstream_revision": snapshot["revision"], "excluded": EXCLUDED,
        "excluded_legacy_part6": 44, "adaptations": {"P3-012": "Clarified update of an existing room reservation.", "P1-016": "Describe the visible shared map without inferring commuting or comparison with the wall map."}}
    data["notice"] = "Học liệu DHV tự biên soạn và nội dung MIT từ TOEIC Question Ocean được chọn lọc, bổ sung lời giải tiếng Việt. Không phải đề ETS. Mục tiêu 900 là định hướng, không bảo đảm kết quả. Audio tổng hợp; hình Part 1 là minh họa hoặc cảnh mô phỏng tạo bằng AI. Điểm hiển thị là số câu đúng, không quy đổi điểm TOEIC chính thức."
    # Checked-in membership freezes existing exam codes as the bank grows.
    forms_path = Path(__file__).resolve().parents[1] / "data/toeic/exam-forms.json"
    data["exams"] = json.loads(forms_path.read_text(encoding="utf-8")) if forms_path.exists() else build_exams(data["questions"])
    return data


def build_exams(bank):
    exams, used = [], set()
    def add(eid, title, kind, minutes, rows, description):
        exams.append({"id": eid, "title": title, "type": kind, "minutes": minutes, "description": description,
            "question_ids": [q["id"] for q in rows], "parts": [{"part": p, "count": sum(q["part"] == p for q in rows)} for p in range(1,8) if any(q["part"] == p for q in rows)],
            "notice": "Luyện có đồng hồ tổng; audio điều khiển thủ công, nghe lại được. Các bài mini và bài riêng kỹ năng dùng chung ngân hàng với đề toàn phần. Không dự đoán điểm TOEIC."})
    for number in (1, 2):
        rng = random.Random(f"dhv-full-{number}-2026.10-v3")
        rows = []
        for part, count in PART_COUNTS.items():
            rows.extend(choose_groups([q for q in bank if q["part"] == part and q["id"] not in used], count, rng))
        used.update(q["id"] for q in rows)
        add(f"dhv-full-{number:02}-v1", f"DHV {number:02} · Đề toàn phần", "full", 120, rows,
            "200 câu: 100 nghe + 100 đọc, đúng số lượng Parts 1–7. Hai mã đề toàn phần không trùng ID câu hỏi trong phiên bản này; không phải đề chính thức.")
        if number == 1:
            add("dhv-listening-01-v1", "Listening 01 · Sức bền nghe", "listening", 45, [q for q in rows if q["part"] <= 4], "100 câu Parts 1–4, 45 phút. Trích phần nghe của DHV 01.")
            add("dhv-reading-01-v1", "Reading 01 · Quản lý 75 phút", "reading", 75, [q for q in rows if q["part"] >= 5], "100 câu Parts 5–7, 75 phút. Trích phần đọc của DHV 01.")
    for number in range(1, 5):
        rng = random.Random(f"dhv-mini-{number}-2026.10-v3")
        rows = []
        for part, count in {1:2, 2:6, 3:9, 4:9, 5:10, 6:4, 7:10}.items():
            rows.extend(choose_groups([q for q in bank if q["part"] == part], count, rng))
        add(f"dhv-mini-{number:02}-v1", f"Mini test {number:02} · 7 Part", "mini", 35, rows, "50 câu để luyện một lượt ngắn, giữ nguyên nhóm hội thoại và văn bản. Không phải đề rút gọn do ETS ban hành.")
    return exams


def topic_handbook():
    lines = ["# Sổ tay ôn theo dạng · TOEIC cùng DHV", "", "Học liệu luyện tập, không phải đề ETS. Học một dạng → luyện không xem đáp án → giải thích bằng chứng → ôn lỗi.", ""]
    for t in TOPICS:
        lines += [f"## Part {t['part']} · {t['title']}", "", t["recognition"], "", "### Kiến thức", ""]
        lines += [f"- {x}" for x in t["rules"]]
        lines += ["", "### Cách làm", ""] + [f"{i}. {x}" for i, x in enumerate(t["steps"], 1)]
        lines += ["", "### Bẫy cần tránh", ""] + [f"- {x}" for x in t["traps"]]
        lines += ["", "### Ví dụ có phân tích", "", t["example"]["text"], "", t["example"]["explanation"], ""]
    lines += ["Nguồn đối chiếu: [IIBC](https://www.iibc-global.org/english/toeic/test/lr/about/format.html), [ETS](https://www.ets.org/toeic/test-takers/prepare.html), [British Council](https://learnenglish.britishcouncil.org/free-resources/grammar/english-grammar-reference). Hướng dẫn và ví dụ trên được DHV biên soạn; ngân hàng bài luyện trong ứng dụng có thêm câu MIT được ghi nguồn riêng.", ""]
    return "\n".join(lines)
