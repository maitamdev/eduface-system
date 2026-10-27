"""Offline adaptation of the remaining reviewed MIT question data.

The full upstream snapshot is retained for audit, but only reviewed questions
enter scored practice. Existing question and exam IDs remain unchanged.
"""
import copy
import hashlib
import json
import random
import re
from collections import defaultdict
from pathlib import Path

from toeic_expansion import ROOT, arrange_options
from toeic_ocean_vi import EXCLUDED as PREVIOUS_EXCLUSIONS
from toeic_ocean_more_vi import REVIEWS, EDITS, GROUP_EDITS, EXCLUDED
from core.toeic_content import choose_groups, PART_COUNTS

LEGACY_PART6 = {f"P6-{n:03}" for n in range(1, 29)} | {
    f"P6-G{g}-Q{n}" for g in range(16, 20) for n in range(1, 5)
}


def edit_row(source):
    row = copy.deepcopy(source)
    group = GROUP_EDITS.get(row.get("groupId"), {})
    if "replace_audio" in group:
        before, after = group["replace_audio"]
        assert before in row["audioText"], row["id"]
        row["audioText"] = row["audioText"].replace(before, after)
    for before, after in group.get("replace_text", []):
        assert before in row["passage"], row["id"]
        for key in ("passage", "prompt", "evidence"):
            if row.get(key):
                row[key] = row[key].replace(before, after)
    changes = EDITS.get(row["id"], {})
    if "prompt" in changes:
        row["prompt"] = changes["prompt"]
    for index, value in changes.get("options", {}).items():
        row["choices"][index] = value
    if "answer_text" in changes:
        row["choices"][row["answer"]] = changes["answer_text"]
    return row


def context_key(q):
    """Avoid reusing a whole listening/reading context in the third full form."""
    text = q.get("passage") or q.get("transcript") or q.get("image") or q["id"]
    return q["part"], hashlib.sha256(re.sub(r"\s+", " ", text).strip().casefold().encode()).hexdigest()


def add_third_form(data):
    if any(e["id"] == "dhv-full-03-v1" for e in data["exams"]):
        return
    bank = {q["id"]: q for q in data["questions"]}
    used = {qid for e in data["exams"] if e["type"] == "full" for qid in e["question_ids"]}
    used_contexts = {context_key(bank[qid]) for qid in used}
    groups = defaultdict(list)
    for q in data["questions"]:
        groups[q.get("group_id", q["id"])].append(q)
    pool = []
    for rows in groups.values():
        key = context_key(rows[0])
        if not any(q["id"] in used for q in rows) and key not in used_contexts:
            pool.extend(rows)
            used_contexts.add(key)
    rng = random.Random("dhv-full-3-2026.10-v4")
    rows = []
    for part, count in PART_COUNTS.items():
        rows.extend(choose_groups([q for q in pool if q["part"] == part], count, rng))
    data["exams"].append({
        "id": "dhv-full-03-v1", "title": "DHV 03 · Đề toàn phần", "type": "full", "minutes": 120,
        "description": "200 câu: 100 nghe + 100 đọc. Mã đề thứ ba không trùng ID câu hỏi với DHV 01 và DHV 02; giữ trọn hội thoại và văn bản.",
        "question_ids": [q["id"] for q in rows],
        "parts": [{"part": p, "count": n} for p, n in PART_COUNTS.items()],
        "notice": "Đồng hồ tổng 120 phút; audio tổng hợp, điều khiển thủ công và nghe lại được. Đây là đề luyện có hỗ trợ, không phải đề ETS hay dự đoán điểm TOEIC.",
    })


def expand_sources(data):
    snapshot = json.loads((ROOT / "backend/data/toeic/vendor/ocean-complete-snapshot.json").read_text(encoding="utf-8"))
    existing = {q.get("provenance", {}).get("upstream_id") for q in data["questions"]}
    existing.discard(None)
    excluded = dict(PREVIOUS_EXCLUSIONS) | {
        qid: "Legacy Part 6 context consists of unrelated one-blank excerpts; not a coherent four-question passage."
        for qid in sorted(LEGACY_PART6)
    } | EXCLUDED
    images = {x["file"]: x for x in snapshot["images"]}
    imported = []
    for source in snapshot["questions"]:
        if source["id"] in existing or source["id"] in excluded:
            continue
        row = edit_row(source)
        note = REVIEWS[row["id"]]  # Missing review is a build failure, never a fallback translation.
        part = int(row["part"])
        qid = "oc-" + row["id"].lower()
        q = {
            "id": qid, "lesson_id": f"lab-p{part}", "part": part,
            "prompt": row.get("prompt") or "Choose the statement that best describes the picture.",
            "options": list(row["choices"]), "correct": row["answer"],
            "explanation": note["explanation"], "topic_ids": [note["topic"]],
            "provenance": {"provider": "TOEIC Question Ocean / DHV", "kind": "adapted", "license": "MIT",
                "upstream_id": row["id"], "revision": snapshot["revision"],
                "url": f"{snapshot['repository']}/blob/{snapshot['revision']}/{row['source_file']}"},
        }
        if row.get("groupId"):
            q["group_id"] = "oc-" + row["groupId"].lower()
        for field in ("passage", "evidence", "graphic"):
            if row.get(field):
                q[field] = row[field]
        if q.get("evidence"):
            assert q["evidence"] in q["passage"], qid
        if part <= 4:
            q["audio_id"] = q.get("group_id", qid)
            transcript = re.sub(r"\b([WM]):\s*", lambda m: "\n" + ("Woman: " if m[1] == "W" else "Man: "), row.get("audioText", "")).strip()
            q["transcript"] = re.sub(r"^Speaker:\s*", "", transcript)
        if part == 1:
            q["transcript"] = "Look at the picture."
            filename = "ocean-" + Path(row["image"]).name
            photo = images[filename]
            q["image"] = "/toeic/images/" + filename
            q["image_credit"] = ("Ảnh mô phỏng tạo bằng AI · TOEIC Question Ocean · MIT" if photo["generated"]
                                 else f"Ảnh: {photo['creator']} / Pexels · Pexels License")
            q["provenance"]["image_source"] = photo["url"]
            q["provenance"]["image_license"] = photo["license"]
        imported.append(arrange_options(q))
    imported_ids = {q["provenance"]["upstream_id"] for q in imported}
    assert imported_ids == REVIEWS.keys() - EXCLUDED.keys(), "Review/source inventory drift"
    assert len(snapshot["questions"]) == len(existing) + len(imported) + len(excluded)
    data["questions"].extend(imported)
    data["version"] = "dhv-toeic-2026.10-v4"
    data["lexicon_count"] = json.loads((ROOT / "backend/data/toeic/lexicon.json").read_text(encoding="utf-8"))["word_count"]
    data["expansion"].update({
        "version": "2026.10-v4", "adapted_questions": len(existing) + len(imported),
        "new_questions": len(imported), "upstream_total": len(snapshot["questions"]),
        "excluded": excluded, "additional_edits": EDITS, "context_edits": GROUP_EDITS,
    })
    ocean = next(s for s in data["sources"] if s["id"] == "ocean-mit")
    ocean["usage"] = f"Đối chiếu toàn bộ {len(snapshot['questions'])} câu ở revision đã chốt; {len(existing) + len(imported)} câu được dùng sau rà soát, có lời giải tiếng Việt. Loại {len(excluded)} câu có vấn đề. Ảnh gồm cảnh AI theo MIT và 5 ảnh Pexels có ghi nguồn riêng; audio tổng hợp lại từ transcript."
    data["sources"].extend([
        {"id": "ngsl", "title": "NGSL 1.2 · Từ vựng nền tảng", "url": "https://www.newgeneralservicelist.com/new-general-service-list", "provider": "Browne, Culligan & Phillips", "access": "CC BY-SA 4.0 · từ và định nghĩa tiếng Anh", "stage": "Nền tảng / mọi level", "usage": "Đã nhập 2.809 từ theo bảng tần suất và định nghĩa của tác giả. Tìm kiếm và ôn thẻ trong Kho từ mở; thứ hạng không phải điểm TOEIC."},
        {"id": "tsl", "title": "TOEIC Service List 1.2 · Từ vựng bổ trợ", "url": "https://www.newgeneralservicelist.com/toeic-service-list", "provider": "Browne & Culligan", "access": "CC BY-SA 4.0 · từ và định nghĩa tiếng Anh", "stage": "Sau nền tảng / ôn TOEIC", "usage": "Đã nhập 1.250 từ xếp hạng, bổ sung các mục chỉ có trong bảng định nghĩa và ghi rõ phần DHV bổ sung. Đây là danh sách từ, không phải đề thi ETS."},
        {"id": "toeic-practice-reference", "title": "TOEIC Practice · Phạm vi dữ liệu và giấy phép", "url": "https://github.com/seikaikyo/toeic-practice", "provider": "seikaikyo", "access": "Mã và ngân hàng đề: độc quyền · từ vựng có thông báo riêng", "stage": "Tham khảo nguồn", "usage": "Không nhập mã nguồn hoặc ngân hàng câu hỏi độc quyền. Dữ liệu NGSL/TSL dùng trong DHV được lấy trực tiếp từ tác giả theo CC BY-SA 4.0; không coi toàn bộ repository là nguồn mở."},
        {"id": "awesome-toeic", "title": "Awesome TOEIC · Danh mục tài nguyên", "url": "https://github.com/thu-tram/awesome-toeic", "provider": "thu-tram / cộng đồng", "access": "Liên kết tham khảo tại nguồn", "stage": "Listening & Reading", "usage": "Danh mục giúp tìm website, bài nghe và đề luyện. Không phải một ngân hàng được cấp phép để tải toàn bộ vào DHV; mở nguồn đích để học theo điều kiện của từng nơi."},
        {"id": "ednet-research", "title": "EdNet · Dữ liệu nghiên cứu hành vi học", "url": "https://github.com/riiid/ednet", "provider": "Riiid", "access": "CC BY-NC 4.0 · mục đích nghiên cứu", "stage": "Tham khảo nghiên cứu", "usage": "Dữ liệu tương tác và metadata không cung cấp đầy đủ đề, lựa chọn và audio. Chưa nhập vào ngân hàng luyện thi; chỉ dẫn nguồn nghiên cứu, không tạo câu hỏi từ metadata."},
    ])
    data["notice"] = "Học liệu DHV và câu hỏi MIT từ TOEIC Question Ocean được rà soát, có lời giải tiếng Việt. Không phải đề ETS; mục tiêu 900 không bảo đảm kết quả. Audio tổng hợp; ảnh Part 1 gồm minh họa, cảnh AI và ảnh Pexels ghi nguồn. Kho từ NGSL/TSL dùng định nghĩa tiếng Anh theo CC BY-SA 4.0. Điểm bài luyện là số câu đúng, không quy đổi điểm TOEIC chính thức."
    add_third_form(data)
    return data
