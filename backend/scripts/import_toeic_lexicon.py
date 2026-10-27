"""Build the CC BY-SA 4.0 + MIT bilingual English-Vietnamese lexicon from pinned local sources.

No network access, spreadsheet formulas, or macros are executed. Pass --source-dir
once to copy the reviewed source files; later builds use the checked-in inputs.
"""
import argparse
import csv
import gzip
import hashlib
import json
import re
import shutil
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from toeic_bilingual_vi import POS_LABELS_VI

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "backend/data/toeic/vendor/ngsl-tsl"
FILES = {
    "NGSL_12_stats.csv": "2098bab8955a120a9766c6282a51d7d578c6cb0a7d946600d2ffb73ba25a0b44",
    "NGSL_12_with_English_definitions.xlsx": "27f8bb4e0948719ffef01a42de0f9e01089b78a12bd576b480d5f14df5e3341c",
    "TSL_12_stats.csv": "2259df25a1077b04067ef0c0e9e4c98b46c91e4d539741dfaceba88651ff486d",
    "TSL_12_definitions.xlsx": "c218acb24db0734498a4e175205c96ebb4981bd30542029868d37b3c0a772e74",
    "bilingual_enrichment.json": "3c88dd478221d26074320bb71b88851bb594b531305d8a4e7a9c17baf947901d",
    "IPA-MIT-LICENSE.txt": "2c6a7e4c71f834a8fc0114fa4f65ca85e80bc4b4dc7ed08746963a09a7b0d177",
    "THICHHOC-LICENSE-DATA.md": "2725831420daae51f62bf704bd57182c65ac4b9a85eb082c614a1e342fb82661",
}
EXTENDED_GZIP = ("lexicon_100k.json.gz", "c23daff82af05f7b956e934ec2cf6a5d9b71a58570b0759e9582739736b21f1d")
UPSTREAM_URLS = {
    "NGSL_12_stats.csv": "https://www.newgeneralservicelist.com/s/NGSL_12_stats.csv",
    "NGSL_12_with_English_definitions.xlsx": "https://www.newgeneralservicelist.com/s/NGSL_12_with_English_definitions.xlsx",
    "TSL_12_stats.csv": "https://www.newgeneralservicelist.com/s/TSL_12_stats.csv",
    "TSL_12_definitions.xlsx": "https://www.newgeneralservicelist.com/s/TSL_12_definitions.xlsx",
    "bilingual_enrichment.json": "https://vi.wiktionary.org/",
    "IPA-MIT-LICENSE.txt": "https://github.com/open-dict-data/ipa-dict/blob/master/LICENSE.txt",
    "THICHHOC-LICENSE-DATA.md": "https://github.com/thichhoc-org/thichhoc-dict/blob/main/dict-en-vi/LICENSE-DATA",
}
ADDED_DEFINITIONS = {
    "by-law": "a rule made by a local authority or an organization to govern its own affairs",
    "café": "a small place where people can buy coffee, other drinks, and light meals",
    "e-book": "a book in a digital format that can be read on an electronic device",
    "entrée": "the main dish of a meal in American English; a dish served before the main course in some other varieties of English",
    "résumé": "a short written summary of a person's education, skills, and work experience, used when applying for a job",
    "smartphone": "a mobile phone that can run applications and access the internet",
}
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
SOURCES = [
    {"id": "ngsl", "name": "NGSL 1.2", "authors": "Charles Browne, Brent Culligan, Joseph Phillips",
     "url": "https://www.newgeneralservicelist.com/new-general-service-list", "license": "CC BY-SA 4.0", "license_url": LICENSE_URL},
    {"id": "tsl", "name": "TOEIC Service List 1.2", "authors": "Charles Browne, Brent Culligan",
     "url": "https://www.newgeneralservicelist.com/toeic-service-list", "license": "CC BY-SA 4.0", "license_url": LICENSE_URL},
    {"id": "thichhoc", "name": "Từ điển Anh–Việt thichhoc.com (thichhoc-dict v0.9.0: WordNet 3.1, CMUdict, Wiktionary)",
     "authors": "thichhoc.com, Princeton University (WordNet 3.1), Carnegie Mellon University (CMUdict), Wiktionary Contributors",
     "url": "https://github.com/thichhoc-org/thichhoc-dict", "license": "CC BY-SA 4.0", "license_url": LICENSE_URL},
    {"id": "wiktionary-vi", "name": "Vietnamese Wiktionary (via Kaikki.org / Wiktextract) & DHV Bilingual Adaptations",
     "authors": "Wiktionary Contributors, Tatu Ylönen (Wiktextract), DHV English Studio",
     "url": "https://vi.wiktionary.org/", "license": "CC BY-SA 4.0", "license_url": LICENSE_URL},
    {"id": "ipa-dict", "name": "open-dict-data / ipa-dict (en_US)", "authors": "open-dict-data Contributors",
     "url": "https://github.com/open-dict-data/ipa-dict", "license": "MIT", "license_url": "https://opensource.org/licenses/MIT"},
]


def canonical(term):
    term = unicodedata.normalize("NFKC", term).strip().casefold()
    return "email" if term == "e-mail" else term


def definitions(path):
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as book:
        shared = ["".join(x.itertext()) for x in ET.fromstring(book.read("xl/sharedStrings.xml")).findall("s:si", ns)]
        sheet = ET.fromstring(book.read("xl/worksheets/sheet1.xml"))
    rows = {}
    for row in sheet.findall("s:sheetData/s:row", ns):
        values = {}
        for cell in row.findall("s:c", ns):
            column = re.sub(r"\d", "", cell.attrib["r"])
            value = cell.find("s:v", ns)
            if value is None or value.text is None:
                continue
            values[column] = (shared[int(value.text)] if cell.get("t") == "s" else value.text).strip()
        term, definition = values.get("A", ""), values.get("B", "")
        if not term or not definition or (row.get("r") == "1" and term.casefold() in {"word", "lemma", "tsl word"}):
            continue
        key = canonical(term)
        assert key not in rows, f"Duplicate definition: {term}"
        rows[key] = {"term": term, "text": definition}
    return rows


def build_handbook(ordered):
    tsl_words = [
        w for w in ordered if any(s["id"] == "tsl" for s in w["lists"])
    ]
    tsl_words.sort(key=lambda w: (next(s["rank"] for s in w["lists"] if s["id"] == "tsl") or 100000, w["term"]))
    ngsl_top = [
        w for w in ordered if any(s["id"] == "ngsl" and s["rank"] and s["rank"] <= 600 for s in w["lists"])
    ]
    ngsl_top.sort(key=lambda w: next(s["rank"] for s in w["lists"] if s["id"] == "ngsl"))

    def esc(text):
        return str(text).replace("|", "\\|").replace("\n", " ")

    lines = [
        "# Sổ tay từ vựng trọng tâm NGSL/TSL · Bản trích lịch sử",
        "",
        "> **Giấy phép & Ghi nguồn:** Dữ liệu từ điển song ngữ trên hệ thống kết hợp **NGSL 1.2** (Charles Browne, Brent Culligan, Joseph Phillips — `CC BY-SA 4.0`), **TOEIC Service List 1.2** (Charles Browne, Brent Culligan — `CC BY-SA 4.0`), **Từ điển Anh–Việt thichhoc.com (`thichhoc-dict v0.9.0`, `CC BY-SA 4.0`, nguồn gốc: Princeton WordNet 3.1, CMUdict, Wiktionary)**, nghĩa tiếng Việt từ **Vietnamese Wiktionary / Kaikki.org** & biên tập ngữ cảnh **DHV English Studio** (`CC BY-SA 4.0`), cùng phiên âm Mỹ từ **open-dict-data/ipa-dict** (`MIT`). Bản tổng hợp được phát hành theo giấy phép [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).",
        "",
        "## Tổng quan",
        "- Sổ tay này trích nhóm từ trọng tâm từ bản dữ liệu trước. Để xem nghĩa được cập nhật và toàn bộ kho, mở **Từ vựng → Từ điển Anh–Việt** trong ứng dụng.",
        "- Không phải mọi mục từ đều có IPA hoặc ví dụ đã dịch. Số liệu, nguồn và công bố chất lượng hiện hành có trong `/toeic/licenses/DICTIONARY.md`; bản đầy đủ tại `/toeic/dictionary/dictionary.json.gz`.",
        "",
        "---",
        "",
        "## Phần 1 · Trọn bộ 1.252 Từ vựng Công sở & Thương mại TOEIC (TSL 1.2)",
        "",
        "| Hạng TSL | Từ vựng | Phiên âm (IPA) | Từ loại | Nghĩa tiếng Việt | Định nghĩa tiếng Anh (TSL) |",
        "|---:|---|---|---|---|---|",
    ]
    for w in tsl_words:
        rank = next((s["rank"] for s in w["lists"] if s["id"] == "tsl"), None)
        rank_label = f"#{rank}" if rank else "Bổ sung"
        pos_label = ", ".join(POS_LABELS_VI.get(p, p) for p in w["pos"])
        en_def = next((d["text"] for d in w["definitions"] if d["source_id"] == "tsl"), w["definitions"][0]["text"])
        lines.append(
            f"| {rank_label} | **{esc(w['term'])}** | `{esc(w['ipa'])}` | {esc(pos_label)} | {esc(w['meaning_vi'])} | {esc(en_def)} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Phần 2 · 600 Từ vựng Nền tảng Tần suất Cao nhất (NGSL 1.2 Top 600)",
        "",
        "*(Tra kho đầy đủ và nghĩa cập nhật tại **Từ vựng → Từ điển Anh–Việt** trên ứng dụng.)*",
        "",
        "| Hạng NGSL | Từ vựng | Phiên âm (IPA) | Từ loại | Nghĩa tiếng Việt | Định nghĩa tiếng Anh (NGSL) |",
        "|---:|---|---|---|---|---|",
    ])
    for w in ngsl_top:
        rank = next(s["rank"] for s in w["lists"] if s["id"] == "ngsl")
        pos_label = ", ".join(POS_LABELS_VI.get(p, p) for p in w["pos"])
        en_def = next((d["text"] for d in w["definitions"] if d["source_id"] == "ngsl"), w["definitions"][0]["text"])
        lines.append(
            f"| #{rank} | **{esc(w['term'])}** | `{esc(w['ipa'])}` | {esc(pos_label)} | {esc(w['meaning_vi'])} | {esc(en_def)} |"
        )
    lines.append("")
    return "\n".join(lines)


def build(source_dir=None):
    if source_dir:
        VENDOR.mkdir(parents=True, exist_ok=True)
        for name, expected in FILES.items():
            source = Path(source_dir) / name
            if source.exists():
                assert hashlib.sha256(source.read_bytes()).hexdigest() == expected, f"Changed source: {name}"
                shutil.copyfile(source, VENDOR / name)
    for name, expected in FILES.items():
        assert hashlib.sha256((VENDOR / name).read_bytes()).hexdigest() == expected, f"Changed source: {name}"

    ext_name, ext_sha = EXTENDED_GZIP
    ext_path = ROOT / "backend/data/toeic" / ext_name
    assert ext_path.is_file(), f"Missing extended lexicon: {ext_path}"
    assert hashlib.sha256(ext_path.read_bytes()).hexdigest() == ext_sha, f"Changed extended lexicon: {ext_name}"
    ext_rows = json.loads(gzip.decompress(ext_path.read_bytes()).decode("utf-8"))
    assert len(ext_rows) == 143185
    shutil.copyfile(ext_path, ROOT / "frontend/public/toeic" / ext_name)

    bilingual = json.loads((VENDOR / "bilingual_enrichment.json").read_text(encoding="utf-8"))["entries"]
    words = {}
    for source_id, prefix, filename, encoding in (
        ("ngsl", "NGSL", "NGSL_12_with_English_definitions.xlsx", "utf-8-sig"),
        ("tsl", "TSL", "TSL_12_definitions.xlsx", "cp1252"),
    ):
        entries = definitions(VENDOR / filename)
        assert len(entries) == (2809 if source_id == "ngsl" else 1246)
        with (VENDOR / f"{prefix}_12_stats.csv").open(encoding=encoding, newline="") as stream:
            stats = list(csv.DictReader(stream))
        assert len(stats) == (2809 if source_id == "ngsl" else 1250)
        ranked = {canonical(row["Lemma" if source_id == "ngsl" else "Word"]): int(row["SFI Rank" if source_id == "ngsl" else "TSL Rank"]) for row in stats}
        missing = ranked.keys() - entries.keys()
        assert missing == (set() if source_id == "ngsl" else ADDED_DEFINITIONS.keys())
        for term in missing:
            entries[term] = {"term": term, "text": ADDED_DEFINITIONS[term]}
        for term, definition in entries.items():
            enrichment = bilingual[term]
            assert enrichment["ipa"] and enrichment["pos"] and enrichment["meaning_vi"], f"Incomplete bilingual data: {term}"
            word = words.setdefault(term, {
                "id": "lex-" + hashlib.sha256(term.encode()).hexdigest()[:20],
                "term": term,
                "ipa": enrichment["ipa"],
                "pos": enrichment["pos"],
                "meaning_vi": enrichment["meaning_vi"],
                "example": enrichment.get("example", ""),
                "vi_source": enrichment["vi_source"],
                "inflections": enrichment.get("inflections", []),
                "definitions": [],
                "lists": [],
                "meaning_language": "en",
            })
            word["definitions"].append({"source_id": source_id, "text": definition["text"],
                                         "source_term": definition["term"], "adapted_by_dhv": term in missing})
            word["lists"].append({"id": source_id, "rank": ranked.get(term), "supplemental": term not in ranked})

    ordered = sorted(words.values(), key=lambda w: (0 if any(x["id"] == "ngsl" for x in w["lists"]) else 1,
                                                   min(x["rank"] or 100000 for x in w["lists"]), w["term"]))
    total_word_count = len(ordered) + len(ext_rows)
    data = {
        "version": "ngsl-tsl-thichhoc-147k-dhv-2026.10",
        "language": "en-vi",
        "license": "CC BY-SA 4.0",
        "license_url": LICENSE_URL,
        "sources": SOURCES,
        "source_files": [{"file": name, "sha256": digest, "url": UPSTREAM_URLS[name]} for name, digest in FILES.items()],
        "extended_file": {"file": ext_name, "sha256": ext_sha, "count": len(ext_rows)},
        "word_count": total_word_count,
        "core_word_count": len(ordered),
        "extended_word_count": len(ext_rows),
        "ranked_counts": {"ngsl": 2809, "tsl": 1250},
        "changes": [
            "Normalized e-mail to email for lookup; retained the original source term.",
            "Merged shared headword criteria while retaining both source definitions.",
            "Preserved unranked TSL definition entries born and criteria; no ranks invented.",
            "DHV supplied missing English definitions for: " + ", ".join(ADDED_DEFINITIONS) + ". These adaptations are CC BY-SA 4.0.",
            "Added Vietnamese meanings (meaning_vi) and parts of speech (pos) from Vietnamese Wiktionary (via Kaikki.org / Wiktextract, CC BY-SA 4.0) and DHV TOEIC adaptations (CC BY-SA 4.0).",
            "Added 143,185 extended English-Vietnamese headwords and word inflections from thichhoc-org/thichhoc-dict v0.9.0 (CC BY-SA 4.0; derived from Princeton WordNet 3.1, CMUdict, and Wiktionary), including the required in-dictionary 'thichhoc' credit entry.",
            "Added American English phonetic transcriptions (ipa) from CMUdict, Wiktionary, open-dict-data/ipa-dict (MIT), and DHV phonetic composition.",
        ],
        "words": ordered,
    }
    assert len(ordered) == 4060 and total_word_count == 147245
    assert len({w["id"] for w in ordered}) == len(ordered)
    assert all(w["ipa"] and w["pos"] and w["meaning_vi"] for w in ordered)
    serialized = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    for path in (ROOT / "backend/data/toeic/lexicon.json", ROOT / "frontend/public/toeic/lexicon.json"):
        path.write_text(serialized, encoding="utf-8")

    preview_path = ROOT / "frontend/src/features/toeic/previewCatalog.json"
    if preview_path.is_file():
        preview = json.loads(preview_path.read_text(encoding="utf-8"))
        preview["lexicon_count"] = total_word_count
        preview_path.write_text(json.dumps(preview, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    notice = """# NGSL / TOEIC Service List & Đại Từ Điển Anh–Việt 147.245 Mục Từ — License & Attribution

Dữ liệu từ điển: Từ điển Anh–Việt thichhoc.com (thichhoc-dict),
giấy phép CC BY-SA 4.0.
https://github.com/thichhoc-org/thichhoc-dict
Nguồn gốc: WordNet 3.1 (Princeton), CMUdict (CMU), Wiktionary.
Đã chỉnh sửa dữ liệu.

The 147,245-headword bilingual English–Vietnamese dictionary combines:
1. **NGSL 1.2** (2,809 ranked core words) by Charles Browne, Brent Culligan and Joseph Phillips (CC BY-SA 4.0)
2. **TOEIC Service List 1.2** (1,250 ranked business words + 2 supplemental entries) by Charles Browne and Brent Culligan (CC BY-SA 4.0)
3. **Từ điển Anh–Việt thichhoc.com (`thichhoc-dict` v0.9.0)** (143,185 additional unique headwords from 155,139 POS-disambiguated entries, plus inflected forms and the `thichhoc` attribution entry) (CC BY-SA 4.0; derived from Princeton WordNet 3.1, CMUdict, and Wiktionary)
4. **Vietnamese Wiktionary / Kaikki.org** & curated TOEIC adaptations by **DHV English Studio** (CC BY-SA 4.0)
5. **open-dict-data / ipa-dict (`en_US`)** (MIT License)

Upstream notices & links:
- NGSL 1.2: https://www.newgeneralservicelist.com/new-general-service-list (CC BY-SA 4.0)
- TSL 1.2: https://www.newgeneralservicelist.com/toeic-service-list (CC BY-SA 4.0)
- thichhoc-dict: https://github.com/thichhoc-org/thichhoc-dict (CC BY-SA 4.0; see `THICHHOC-LICENSE-DATA.md`)
- WordNet 3.1: WordNet 3.1 Copyright 2011 The Trustees of Princeton University. All rights reserved. (https://wordnet.princeton.edu/)
- CMUdict: BSD 2-Clause License, Carnegie Mellon University (https://github.com/cmusphinx/cmudict)
- Vietnamese & English Wiktionary / Kaikki.org: https://vi.wiktionary.org/ & https://kaikki.org/ (CC BY-SA 4.0)
- open-dict-data / ipa-dict (en_US): https://github.com/open-dict-data/ipa-dict (MIT License; see `IPA-MIT-LICENSE.txt`)
- License: Creative Commons Attribution-ShareAlike 4.0 International
- License terms: https://creativecommons.org/licenses/by-sa/4.0/
- Legal code: https://creativecommons.org/licenses/by-sa/4.0/legalcode.en

This adapted bilingual dataset is licensed under CC BY-SA 4.0 (with `ipa-dict`
components under the MIT License; see `IPA-MIT-LICENSE.txt` and `THICHHOC-LICENSE-DATA.md`).
Preserve attribution, link to the license, indicate changes, keep the `thichhoc`
attribution headword in the dictionary, and share adaptations under the same
license. No endorsement by the authors or ETS is implied. This notice applies
to these data; it does not relicense the application or unrelated media.

DHV changes:
1. Normalized spelling (`e-mail` -> `email`) for lookup while preserving original source terms.
2. Merged the shared headword `criteria` while preserving both NGSL and TSL definitions.
3. Retained two unranked TSL entries (`born`, `criteria`) without inventing ranks.
4. Supplied six missing English definitions (`by-law`, `café`, `e-book`, `entrée`, `résumé`, `smartphone`).
5. Enriched all 4,060 NGSL/TSL entries with Vietnamese meanings (`meaning_vi`), standardized parts of speech (`pos`), American English IPA (`ipa`), and inflected word forms (`inflections`).
6. Integrated 143,185 extended English–Vietnamese headwords from `thichhoc-dict` v0.9.0 (preserving the `thichhoc` credit headword) into `lexicon_100k.json.gz` for a combined 147,245-word bilingual dictionary.

Source publications were retrieved on 2026-10-27. All pinned inputs and SHA-256 digests
are retained under `backend/data/toeic/vendor/ngsl-tsl` for reproducible offline builds.
No question bank or proprietary code from `seikaikyo/toeic-practice` is included.
"""
    (VENDOR / "LICENSE.md").write_text(notice, encoding="utf-8")
    (ROOT / "frontend/public/toeic/licenses/NGSL-TSL.md").write_text(notice, encoding="utf-8")
    shutil.copyfile(VENDOR / "IPA-MIT-LICENSE.txt", ROOT / "frontend/public/toeic/licenses/IPA-MIT-LICENSE.txt")
    shutil.copyfile(VENDOR / "THICHHOC-LICENSE-DATA.md", ROOT / "frontend/public/toeic/licenses/THICHHOC-LICENSE-DATA.md")

    handbook = build_handbook(ordered)
    (ROOT / "docs/toeic/SO_TAY_TU_VUNG.md").write_text(handbook, encoding="utf-8")
    (ROOT / "frontend/public/toeic/so-tay-tu-vung-song-ngu.md").write_text(handbook, encoding="utf-8")

    print(f"Built {total_word_count} bilingual English-Vietnamese headwords ({len(ordered)} core NGSL/TSL + {len(ext_rows)} extended thichhoc-dict).")
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path)
    build(parser.parse_args().source_dir)
