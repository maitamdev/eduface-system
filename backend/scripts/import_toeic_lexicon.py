"""Build the CC BY-SA lexicon from pinned, locally cached author publications.

No network access, spreadsheet formulas, or macros are executed. Pass --source-dir
once to copy the reviewed source files; later builds use the checked-in inputs.
"""
import argparse
import csv
import hashlib
import json
import re
import shutil
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "backend/data/toeic/vendor/ngsl-tsl"
FILES = {
    "NGSL_12_stats.csv": "2098bab8955a120a9766c6282a51d7d578c6cb0a7d946600d2ffb73ba25a0b44",
    "NGSL_12_with_English_definitions.xlsx": "27f8bb4e0948719ffef01a42de0f9e01089b78a12bd576b480d5f14df5e3341c",
    "TSL_12_stats.csv": "2259df25a1077b04067ef0c0e9e4c98b46c91e4d539741dfaceba88651ff486d",
    "TSL_12_definitions.xlsx": "c218acb24db0734498a4e175205c96ebb4981bd30542029868d37b3c0a772e74",
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


def build(source_dir=None):
    if source_dir:
        VENDOR.mkdir(parents=True, exist_ok=True)
        for name, expected in FILES.items():
            source = Path(source_dir) / name
            assert hashlib.sha256(source.read_bytes()).hexdigest() == expected, f"Changed source: {name}"
            shutil.copyfile(source, VENDOR / name)
    for name, expected in FILES.items():
        assert hashlib.sha256((VENDOR / name).read_bytes()).hexdigest() == expected, f"Changed source: {name}"
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
            word = words.setdefault(term, {"id": "lex-" + hashlib.sha256(term.encode()).hexdigest()[:20], "term": term,
                                           "definitions": [], "lists": [], "meaning_language": "en"})
            word["definitions"].append({"source_id": source_id, "text": definition["text"],
                                         "source_term": definition["term"], "adapted_by_dhv": term in missing})
            word["lists"].append({"id": source_id, "rank": ranked.get(term), "supplemental": term not in ranked})
    ordered = sorted(words.values(), key=lambda w: (0 if any(x["id"] == "ngsl" for x in w["lists"]) else 1,
                                                   min(x["rank"] or 100000 for x in w["lists"]), w["term"]))
    data = {"version": "ngsl-tsl-1.2-dhv-2026.10", "language": "en", "license": "CC BY-SA 4.0", "license_url": LICENSE_URL,
            "sources": SOURCES, "source_files": [{"file": name, "sha256": digest, "url": "https://www.newgeneralservicelist.com/s/" + name} for name, digest in FILES.items()],
            "word_count": len(ordered), "ranked_counts": {"ngsl": 2809, "tsl": 1250},
            "changes": ["Normalized e-mail to email for lookup; retained the original source term.",
                        "Merged shared headword criteria while retaining both source definitions.",
                        "Preserved unranked TSL definition entries born and criteria; no ranks invented.",
                        "DHV supplied missing English definitions for: " + ", ".join(ADDED_DEFINITIONS) + ". These adaptations are CC BY-SA 4.0."],
            "words": ordered}
    assert len(ordered) == 4060
    assert len({w["id"] for w in ordered}) == len(ordered)
    serialized = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    for path in (ROOT / "backend/data/toeic/lexicon.json", ROOT / "frontend/public/toeic/lexicon.json"):
        path.write_text(serialized, encoding="utf-8")
    notice = """# NGSL / TOEIC Service List — data license and attribution

The word lists, ranks and English definitions in `lexicon.json` are derived from
NGSL 1.2 by Charles Browne, Brent Culligan and Joseph Phillips, and TOEIC Service
List 1.2 by Charles Browne and Brent Culligan.

- NGSL: https://www.newgeneralservicelist.com/new-general-service-list
- TSL: https://www.newgeneralservicelist.com/toeic-service-list
- License: Creative Commons Attribution-ShareAlike 4.0 International
- License terms: https://creativecommons.org/licenses/by-sa/4.0/
- Legal code: https://creativecommons.org/licenses/by-sa/4.0/legalcode.en

This adapted dataset is also licensed under CC BY-SA 4.0. Preserve attribution,
link to the license, indicate changes, and share adaptations under the same
license. No endorsement by the authors or ETS is implied. This notice applies
to these data; it does not relicense the application or unrelated media.

DHV changes: normalized spelling for lookup, merged the shared headword criteria
while preserving both definitions, retained two unranked TSL entries without
inventing ranks, and supplied six missing English definitions (by-law, café,
e-book, entrée, résumé, smartphone). The definitions are English, not Vietnamese.
The JSON records source membership, ranks, adaptations and source-file SHA-256
digests. Its 4,060 unique headwords comprise 4,059 ranked entries plus the
unranked headword born; criteria is already ranked in NGSL.

Source publications were retrieved on 2026-10-27. The source XLSX/CSV files are
retained under backend/data/toeic/vendor/ngsl-tsl for reproducible offline builds.
No question bank or proprietary code from seikaikyo/toeic-practice is included.
"""
    (VENDOR / "LICENSE.md").write_text(notice, encoding="utf-8")
    (ROOT / "frontend/public/toeic/licenses/NGSL-TSL.md").write_text(notice, encoding="utf-8")
    print(f"Built {len(ordered)} unique English headwords; 2809 NGSL ranks, 1250 TSL ranks, 2 unranked TSL memberships.")
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path)
    build(parser.parse_args().source_dir)
