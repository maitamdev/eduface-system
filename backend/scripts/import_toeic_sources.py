"""Explicit, pinned import of the complete MIT question source. No upstream JS runs.

Ordinary builds read the checked-in snapshot offline. --cache may point at a
previously downloaded checkout; every file is verified against the pinned Git tree.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = "kdeppaei/toeic-question-ocean"
REVISION = "a940bb8b479ef4d06af468015d757041c3d2e457"
BASE = f"https://raw.githubusercontent.com/{REPOSITORY}/{REVISION}/"


def normalize(packs, order):
    """Reproduce only reviewed data transformations, never arbitrary JS behavior."""
    bank = {}

    def put(row, filename):
        if isinstance(row, list):
            assert len(row) == 7, "Unexpected compact Part 5 schema"
            row = dict(zip(("id", "difficulty", "category", "prompt", "choices", "answer", "explanation"), row))
        q = dict(row)
        q.setdefault("part", q["id"][1])
        q["part"] = str(q["part"])
        q["source_file"] = filename
        assert q["id"] not in bank, f"Unreviewed duplicate upstream ID {q['id']}"
        bank[q["id"]] = q

    def flatten(group, filename, part=None):
        rows = group.get("questions", group.get("items", []))
        for index, row in enumerate(rows):
            q = {k:v for k,v in group.items() if k not in ("questions", "items", "ids")}
            q.update(row)
            q.setdefault("id", group["ids"][index] if "ids" in group else f"{group['groupId']}-Q{index+1}")
            q["part"] = str(part or group.get("part") or group["groupId"][1])
            put(q, filename)

    for filename in order:
        pack = packs[filename]
        assert not pack["unsupported"], f"Unsupported data in {filename}: {pack['unsupported']}"
        if pack.get("dynamicCalls"):
            assert filename == "question-bank-v29.js" and pack["dynamicCalls"] == ["pushSet", "pushSet"]
            assert [len(rows) for rows in pack["groupArrays"]] == [8, 17]
        values = pack["literals"]
        for rows in pack["appends"]:
            for row in rows:
                put(row, filename)
        for key in ("items", "p5Items", "grammarItems"):
            for row in values.get(key, []):
                put(row, filename)
        for rows in pack.get("groupArrays", []):
            for group in rows:
                flatten(group, filename)
        for call in pack["sets"]:
            assert call["name"] == "pushReadingSet" and len(call["args"]) == 1
            flatten(call["args"][0], filename, 7)
        for key in ("groups", "listeningGroups", "part6Groups", "readingGroups"):
            for group in values.get(key, []):
                flatten(group, filename, 6 if key == "part6Groups" else 7 if key == "readingGroups" else None)
        if "part6Group" in values:
            flatten(values["part6Group"], filename, 6)
        for qid, fix in values.get("corrections", {}).items():
            assert qid in bank
            bank[qid].update(fix)
        for old, fix in values.get("splitPart6Groups", {}).items():
            for q in bank.values():
                if q.get("groupId") == old and q["id"].startswith(fix["idPrefix"]):
                    q.update({k:v for k,v in fix.items() if k != "idPrefix"})
        for old, fix in values.get("movedReadingGroups", {}).items():
            for q in bank.values():
                if q.get("groupId") == old:
                    q.update(fix)
                    q["part"] = "7"
        for group in values.get("correctedGroups", []):
            for qid in group["ids"]:
                assert qid in bank
                del bank[qid]
            flatten(group, filename, 7)
    assert len(bank) == 1107, "Pinned source inventory changed unexpectedly"
    for q in bank.values():
        assert q["part"] in "1234567" and type(q["answer"]) is int
        assert len(q["choices"]) in (3,4) and 0 <= q["answer"] < len(q["choices"])
    return list(bank.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path)
    args = parser.parse_args()
    tree = json.load(urlopen(f"https://api.github.com/repos/{REPOSITORY}/git/trees/{REVISION}?recursive=1", timeout=30))
    blobs = {item["path"]:item["sha"] for item in tree["tree"] if item["type"] == "blob"}
    files = []

    def read(name):
        assert name in blobs and not Path(name).is_absolute() and ".." not in Path(name).parts
        cached = args.cache / name if args.cache else None
        raw = cached.read_bytes() if cached and cached.is_file() else urlopen(BASE + name, timeout=30).read()
        digest = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        assert digest == blobs[name], f"Source does not match pinned commit: {name}"
        files.append({"path": name, "git_blob_sha":digest, "sha256":hashlib.sha256(raw).hexdigest()})
        return raw

    html = read("index.html").decode("utf-8")
    order = re.findall(r'<script src="\./(question-bank[^" ]*\.js)"', html)
    packs = {}
    with tempfile.TemporaryDirectory(prefix="dhv-ocean-ast-") as temp:
        for filename in order:
            path = Path(temp) / filename
            path.write_bytes(read(filename))
            process = subprocess.run(["node", str(ROOT/"frontend/scripts/extract-toeic-source.mjs"), str(path)], check=True, capture_output=True)
            packs[filename] = json.loads(process.stdout)
            print("Parsed", filename, flush=True)
    questions = normalize(packs, order)
    images = []
    for q in questions:
        if q["part"] != "1":
            continue
        source = q["image"]
        assert re.fullmatch(r"assets/part1/[a-z0-9-]+\.jpg", source)
        raw = read(source)
        filename = "ocean-" + Path(source).name
        target = ROOT/"frontend/public/toeic/images"/filename
        target.write_bytes(raw)
        photo = bool(q.get("imageSource"))
        images.append({"file":filename, "source":source, "sha256":hashlib.sha256(raw).hexdigest(),
                       "license":"Pexels License" if photo else "MIT", "generated":not photo,
                       "creator":q.get("imageCredit", "TOEIC Question Ocean / OpenAI"),
                       "url":q.get("imageSource", BASE+source)})
    license_text = read("LICENSE")
    vendor = ROOT/"backend/data/toeic/vendor"
    public = ROOT/"frontend/public/toeic/licenses"
    (vendor/"OCEAN-MIT-LICENSE.txt").write_bytes(license_text)
    (public/"OCEAN-MIT-LICENSE.txt").write_bytes(license_text)
    snapshot = {"repository":"https://github.com/"+REPOSITORY, "revision":REVISION,
                "license":"MIT", "source_files":files, "questions":questions, "images":images}
    (vendor/"ocean-complete-snapshot.json").write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    attribution = ["# TOEIC Question Ocean · media attribution", "",
                   "Question text: MIT, Copyright (c) 2026 Chun-Hsiung Luo. Imported from commit `"+REVISION+"`.",
                   "[MIT permission notice](OCEAN-MIT-LICENSE.txt). Twenty scenes are AI-generated originals; five photographs have their own [Pexels License](https://www.pexels.com/license/). The Pexels photographs are not relicensed under MIT.",
                   "Images are used for language exercises; no endorsement by creators, people, brands or ETS is implied. Files retain the source pixels.", "",
                   "| File | Creator | License | Original | SHA-256 |", "|---|---|---|---|---|"]
    for asset in images:
        attribution.append(f"| {asset['file']} | {asset['creator']} | {asset['license']} | [Source]({asset['url']}) | `{asset['sha256']}` |")
    (public/"OCEAN-ATTRIBUTION.md").write_text("\n".join(attribution)+"\n",encoding="utf-8")
    print(f"Saved {len(questions)} upstream questions and {len(images)} images. Publication requires the separate DHV review manifest.")


if __name__ == "__main__":
    main()
