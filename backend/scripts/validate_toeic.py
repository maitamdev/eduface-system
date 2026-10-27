"""Check the shipped learning data and media, without connecting to a database."""
import array
import json
import hashlib
import sys
import wave
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from core.toeic_content import content, select_questions, PART_COUNTS

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
guide = (ROOT / "docs/toeic/LO_TRINH_CHI_TIET.md").read_text(encoding="utf-8")
public_guide = (ROOT / "frontend/public/toeic/lo-trinh-dhv.md").read_text(encoding="utf-8")
assert guide.count("### Buổi ") == len(data["curriculum"]["sessions"])
assert public_guide.count("### Buổi ") == len(data["curriculum"]["sessions"])
report = {"lessons": len(data["lessons"]), "questions": len(data["questions"]), "vocabulary": len(data["vocabulary"]),
          "curriculum_levels": len(data["curriculum"]["levels"]), "curriculum_sessions": len(data["curriculum"]["sessions"]),
          "self_checks": sum(len(s["checks"]) for s in data["curriculum"]["sessions"]),
          "by_part": dict(Counter(q["part"] for q in data["questions"])), "audio_files": len(audio),
          "audio_minutes": round(sum(durations)/60, 2), "audio_MB": round(size/1e6, 2),
          "shortest_audio_seconds": round(min(durations), 2), "longest_audio_seconds": round(max(durations), 2)}
print(json.dumps(report, ensure_ascii=False, indent=2))
