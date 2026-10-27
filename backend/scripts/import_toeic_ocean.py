"""Fetch a pinned MIT source snapshot for offline, curated authoring (no eval).

Run explicitly when refreshing the vendor snapshot. The ordinary course build
never accesses the network. Review and translate in toeic_expansion.py afterward.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import re
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
REVISION = "a940bb8b479ef4d06af468015d757041c3d2e457"
BASE = f"https://raw.githubusercontent.com/kdeppaei/toeic-question-ocean/{REVISION}/"
FILES = ["question-bank.js", "question-bank-v50.js", "question-bank-v47.js", "question-bank-v32.js", "question-bank-v33.js"]


def main():
    vendor = ROOT / "backend/data/toeic/vendor"
    vendor.mkdir(parents=True, exist_ok=True)
    payload = {"repository": "https://github.com/kdeppaei/toeic-question-ocean", "revision": REVISION, "license": "MIT", "files": {}}
    with tempfile.TemporaryDirectory(prefix="dhv-toeic-import-") as temp:
        for name in FILES:
            raw = urlopen(BASE + name, timeout=30).read()
            text = raw.decode("utf-8")
            if name == "question-bank.js":
                data = {"questions": json.JSONDecoder().raw_decode(text[text.index("["):])[0]}
            else:
                path = Path(temp) / name
                path.write_bytes(raw)
                parsed = subprocess.run(["node", str(ROOT / "frontend/scripts/extract-toeic-literals.mjs"), str(path)], check=True, capture_output=True)
                data = json.loads(parsed.stdout)
            payload["files"][name] = {"sha256": hashlib.sha256(raw).hexdigest(), "data": data}
            print(name, {k: len(v) for k, v in data.items()})
    images = ROOT / "frontend/public/toeic/images"
    attribution = ["# TOEIC Question Ocean · selected generated images", "", "Adapted with the MIT source snapshot by Chun-Hsiung Luo (2026). These ten scenes are identified upstream as AI-generated original simulations, not ETS material or photographs. No Pexels images are included in this import.", "", "[MIT permission notice](OCEAN-MIT-LICENSE.txt)", "", "| Local file | Pinned original | SHA-256 |", "|---|---|---|"]
    payload["images"] = []
    for name in ("question-bank-v32.js", "question-bank-v33.js"):
        for item in payload["files"][name]["data"]["items"]:
            source = item["image"]
            assert re.fullmatch(r"assets/part1/[a-z0-9-]+\.jpg", source)
            raw = urlopen(BASE + source, timeout=30).read()
            filename = "ocean-" + Path(source).name
            (images / filename).write_bytes(raw)
            digest = hashlib.sha256(raw).hexdigest()
            payload["images"].append({"file": filename, "source": source, "sha256": digest, "generated": True})
            attribution.append(f"| {filename} | [Original]({BASE + source}) | `{digest}` |")
    (vendor / "ocean-snapshot.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    license_text = urlopen(BASE + "LICENSE", timeout=30).read()
    (vendor / "OCEAN-MIT-LICENSE.txt").write_bytes(license_text)
    public = ROOT / "frontend/public/toeic/licenses"
    public.mkdir(exist_ok=True)
    (public / "OCEAN-MIT-LICENSE.txt").write_bytes(license_text)
    (public / "OCEAN-ATTRIBUTION.md").write_text("\n".join(attribution) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
