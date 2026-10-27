"""Check the shipped learning data and media, without connecting to a database."""
import array
import json
import hashlib
import gzip
import sys
import wave
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from core.toeic_content import content, select_questions, PART_COUNTS, study_catalog
from core.toeic_lexicon import lexicon, all_words
from core.dictionary_text import valid_ipa

data = content()
audio = {q["audio_id"] for q in data["questions"] if q.get("audio_id")}
manifest = {row["id"]: row for row in json.loads((ROOT / "frontend/public/toeic/audio/manifest.json").read_text(encoding="utf-8-sig"))}
assert audio == set(manifest), "Audio manifest does not match the course"
durations = []
size = 0
for aid in sorted(audio):
    path = ROOT / "frontend/public/toeic/audio" / f"{aid}.wav"
    size += path.stat().st_size
    assert manifest[aid]["bytes"] == path.stat().st_size
    with wave.open(str(path)) as stream:
        assert stream.getframerate() == 16000 and stream.getnchannels() == 1
        assert stream.getsampwidth() == 2
        samples = array.array("h", stream.readframes(stream.getnframes()))
        assert samples and max(samples) > 100, f"Silent audio: {aid}"
        durations.append(stream.getnframes() / stream.getframerate())
for q in data["questions"]:
    if q.get("audio_id"):
        assert manifest[q["audio_id"]]["transcript_sha256"] == hashlib.sha256(q["transcript"].encode()).hexdigest(), f"Rebuild changed audio: {q['id']}"
    if q.get("image"):
        assert (ROOT / "frontend/public" / q["image"].lstrip("/")).is_file()
    if q["part"] <= 2:
        for i, option in enumerate(q["options"]):
            assert f"{chr(65+i)}. {option}" in q["transcript"], q["id"]
for seed in range(30):
    rows = select_questions("mock", seed=seed)
    assert Counter(q["part"] for q in rows) == PART_COUNTS
    assert len({q["id"] for q in rows}) == 200
    assert len(select_questions("diagnostic", seed=seed)) == 25
preview = json.loads((ROOT / "frontend/src/features/toeic/previewCatalog.json").read_text(encoding="utf-8"))
assert "questions" not in preview
assert preview["version"] == data["version"]
assert preview["curriculum"] == data["curriculum"], "Preview curriculum is stale"
for key, value in study_catalog(data).items():
    assert preview[key] == value, f"Preview {key} are stale"
assert all("question_ids" not in e for e in preview["exams"])
vendor = json.loads((ROOT / "backend/data/toeic/vendor/ocean-complete-snapshot.json").read_text(encoding="utf-8"))
for asset in vendor["images"]:
    path = ROOT / "frontend/public/toeic/images" / asset["file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == asset["sha256"], f"Changed source image: {asset['file']}"
assert (ROOT / "backend/data/toeic/vendor/OCEAN-MIT-LICENSE.txt").read_text(encoding="utf-8") == (ROOT / "frontend/public/toeic/licenses/OCEAN-MIT-LICENSE.txt").read_text(encoding="utf-8")
handbook = (ROOT / "docs/toeic/SO_TAY_DANG_BAI.md").read_text(encoding="utf-8")
assert handbook == (ROOT / "frontend/public/toeic/so-tay-dang-bai.md").read_text(encoding="utf-8")
assert handbook.count("## Part ") == len(data["topics"])
assert data["exams"] == json.loads((ROOT / "backend/data/toeic/exam-forms.json").read_text(encoding="utf-8"))
lex = lexicon()
assert (ROOT / "backend/data/toeic/lexicon.json").read_bytes() == (ROOT / "frontend/public/toeic/lexicon.json").read_bytes()
assert (ROOT / "backend/data/toeic/lexicon_100k.json.gz").read_bytes() == (ROOT / "frontend/public/toeic/lexicon_100k.json.gz").read_bytes()
assert hashlib.sha256((ROOT / "backend/data/toeic/lexicon_100k.json.gz").read_bytes()).hexdigest() == lex["extended_file"]["sha256"]
assert (ROOT / "backend/data/toeic/vendor/ngsl-tsl/LICENSE.md").read_bytes() == (ROOT / "frontend/public/toeic/licenses/NGSL-TSL.md").read_bytes()
assert (ROOT / "backend/data/toeic/vendor/ngsl-tsl/IPA-MIT-LICENSE.txt").read_bytes() == (ROOT / "frontend/public/toeic/licenses/IPA-MIT-LICENSE.txt").read_bytes()
assert (ROOT / "backend/data/toeic/vendor/ngsl-tsl/THICHHOC-LICENSE-DATA.md").read_bytes() == (ROOT / "frontend/public/toeic/licenses/THICHHOC-LICENSE-DATA.md").read_bytes()
assert (ROOT / "docs/toeic/SO_TAY_TU_VUNG.md").read_bytes() == (ROOT / "frontend/public/toeic/so-tay-tu-vung-song-ngu.md").read_bytes()
assert preview["lexicon_count"] == lex["word_count"]
ids = set()
for word in all_words():
    assert word["id"] not in ids
    ids.add(word["id"])
    assert word.get("pos") and word.get("meaning_vi") and word.get("senses_vi")
    assert not word.get("ipa") or (valid_ipa(word["ipa"]) and word.get("ipa_source"))
assert len(ids) == lex["word_count"]
assert (ROOT / "backend/data/toeic/dictionary-meta.json").read_bytes() == (ROOT / "frontend/public/toeic/dictionary-meta.json").read_bytes()
for name, expected in lex["files"].items():
    path = ROOT / "frontend/public/toeic/dictionary" / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected["sha256"]
    with gzip.open(path, "rb") as stream:
        assert hashlib.file_digest(stream, "sha256").hexdigest() == expected["decoded_sha256"]
assert all(c.get("ipa") and c.get("pos") and c.get("meaning") for c in data["vocabulary"])
for source in lex["source_files"]:
    payload = (ROOT / "backend/data/toeic/vendor/ngsl-tsl" / source["file"]).read_bytes()
    if source.get("repository_normalization") == "CRLF to LF":
        payload = payload.replace(b"\r\n", b"\n")
    assert hashlib.sha256(payload).hexdigest() == source.get("repository_sha256", source["sha256"]), f"Changed source: {source['file']}"
guide = (ROOT / "docs/toeic/LO_TRINH_CHI_TIET.md").read_text(encoding="utf-8")
public_guide = (ROOT / "frontend/public/toeic/lo-trinh-dhv.md").read_text(encoding="utf-8")
assert guide.count("### Buổi ") == len(data["curriculum"]["sessions"])
assert public_guide.count("### Buổi ") == len(data["curriculum"]["sessions"])
report = {"lessons": len(data["lessons"]), "questions": len(data["questions"]), "vocabulary": len(data["vocabulary"]), "lexicon_words": lex["word_count"],
          "topics": len(data["topics"]), "exam_forms": len(data["exams"]),
          "adapted_questions": data["expansion"]["adapted_questions"], "new_original_questions": data["expansion"]["original_questions"],
          "images": len({q["image"] for q in data["questions"] if q.get("image")}),
          "curriculum_levels": len(data["curriculum"]["levels"]), "curriculum_sessions": len(data["curriculum"]["sessions"]),
          "self_checks": sum(len(s["checks"]) for s in data["curriculum"]["sessions"]),
          "by_part": dict(Counter(q["part"] for q in data["questions"])), "audio_files": len(audio),
          "audio_minutes": round(sum(durations)/60, 2), "audio_MB": round(size/1e6, 2),
          "shortest_audio_seconds": round(min(durations), 2), "longest_audio_seconds": round(max(durations), 2)}
print(json.dumps(report, ensure_ascii=False, indent=2))
