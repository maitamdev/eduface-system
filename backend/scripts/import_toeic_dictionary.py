"""Build an indexed bilingual dictionary from pinned, openly licensed data.

Explicit authoring step, never invoked by the application. Uses local copies of
the two checksum-pinned downloads; JSON and archive members are read as data only.
No external code is executed and archives are never extracted into the project.
Existing headword IDs are kept so all learner FSRS schedules remain valid.
"""
import argparse
import gzip
import hashlib
import json
import re
import sqlite3
import sys
import tarfile
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from core.dictionary_text import normalize, compact, valid_ipa
from toeic_dictionary_editorial import EDITORIAL, ALIASES

DATA = ROOT / "backend/data/toeic"
PUBLIC = ROOT / "frontend/public/toeic"
REVISION = "4d6e92e8bcf8e3e762410c2b0a9f98fea8e62e5b"
INPUTS = {
    "thichhoc.tar.gz": ("afe7e47166173e3867454444b2ca76c57713640a61ad4b3ccd393b2e6374a1fb",
        f"https://codeload.github.com/thichhoc-org/thichhoc-dict/tar.gz/{REVISION}"),
    "vi-extract.jsonl.gz": ("d2359c7e969616302f9cc06272d1fcd9c850af824576b59cdf824b1895dca29a",
        "https://kaikki.org/dictionary/downloads/vi/vi-extract.jsonl.gz"),
}
POS = {"noun":"n", "name":"n", "verb":"v", "adj":"adj", "adv":"adv", "prep":"prep",
       "conj":"conj", "pron":"pron", "det":"det", "intj":"interj", "num":"num",
       "phrase":"phrase", "abbrev":"abbr", "particle":"particle", "prefix":"prefix", "suffix":"suffix"}
VI = re.compile(r"[ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ]", re.I)
HEAD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ0-9 '’/.,&+()–-]{0,79}")
FORM = re.compile(r"^(?:Quá khứ(?: đơn)?(?: và phân từ quá khứ)?|Phân từ (?:quá khứ|hiện tại)|Hiện tại phân từ|Số nhiều|Động từ quá khứ|Động từ chia ở ngôi thứ ba số ít)(?: của)?\s+(?:của\s+)?([A-Za-z][A-Za-z '-]+)\.?$", re.I)
DECK_BITS = {"ngsl":1, "tsl":2, "thichhoc":4, "wiktionary":8, "dhv":16}


def clean(text):
    return " ".join(str(text).replace("\x00", "").split()).strip()


def unique(items):
    return list(dict.fromkeys(items))


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def transport_metadata(path):
    """Browsers may receive gzip bytes or transparently decoded JSON from a CDN."""
    decoded_hash = hashlib.sha256()
    decoded_size = 0
    with gzip.open(path, "rb") as stream:
        while chunk := stream.read(1024 * 1024):
            decoded_hash.update(chunk)
            decoded_size += len(chunk)
    return {"sha256":digest(path), "bytes":path.stat().st_size,
            "decoded_sha256":decoded_hash.hexdigest(), "decoded_bytes":decoded_size}


def gzip_json(path, data):
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode()
    path.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))


def stable_new(term):
    return "lex-wk-" + hashlib.sha256(term.encode()).hexdigest()[:20]


def build(source_dir):
    source_dir = Path(source_dir)
    for name, (sha, _) in INPUTS.items():
        assert digest(source_dir / name) == sha, f"Source checksum mismatch: {name}"
    legacy = json.loads((DATA / "lexicon.json").read_text(encoding="utf-8"))
    words = {w["term"].casefold(): dict(w) for w in legacy["words"]}
    assert len(words) == 4060
    old_rows = json.loads(gzip.decompress((DATA / "lexicon_100k.json.gz").read_bytes()))
    assert len(old_rows) == 143185
    for i, row in enumerate(old_rows, 1):
        term, _unverified_ipa, pos, vi, en, tier, forms = row
        assert term not in words
        words[term] = {"id":f"lex-th-{i:06d}", "term":term, "ipa":"", "pos":pos,
                      "meaning_vi":vi, "definitions":[{"source_id":"thichhoc", "text":en,
                      "source_term":term, "adapted_by_dhv":False}],
                      "lists":[{"id":"thichhoc", "rank":None, "tier":tier, "supplemental":False}],
                      "inflections":forms, "vi_source":"thichhoc", "translation_status":"machine"}
    original_ids = {term:w["id"] for term,w in words.items()}
    for word in words.values():
        word["meaning_language"] = "vi"
        word["senses_vi"] = []
        word["examples"] = []
        word["aliases"] = []
        if word["id"].startswith("lex-th-"):
            word["source_url"] = f"https://github.com/thichhoc-org/thichhoc-dict/tree/{REVISION}/dict-en-vi/data/entries"
        else:
            word["translation_status"] = "edited" if word.get("vi_source", "").startswith("dhv") else "community"
            word["ipa_source"] = "ipa-dict / DHV"
            word["source_url"] = "https://vi.wiktionary.org/wiki/" + quote(word["term"], safe="")
        if not valid_ipa(word.get("ipa", "")): word["ipa"] = ""
    # Recover only actual upstream pronunciations. The previous importer filled
    # missing pronunciations with guessed characters, including literal '?'.
    with tarfile.open(source_dir / "thichhoc.tar.gz") as archive:
        for member in archive.getmembers():
            if not member.isfile() or "/data/entries/" not in member.name or not member.name.endswith(".jsonl"):
                continue
            for line in archive.extractfile(member):
                entry = json.loads(line)
                term = entry["headword"].casefold()
                if term not in words: continue
                word = words[term]
                pron = entry.get("pron", "")
                if not word.get("ipa") and valid_ipa(pron):
                    word["ipa"] = pron; word["ipa_source"] = "CMUdict / thichhoc"
                word["inflections"] = unique(word.get("inflections", []) + entry.get("inflections", []))
    # Preserve every Vietnamese sense (not just the first three). Never label an
    # English gloss as Vietnamese or promote an inflected-form cross-reference
    # into an unrelated standalone translation.
    wiki = {}; aliases = []; skipped = Counter()
    with gzip.open(source_dir / "vi-extract.jsonl.gz", "rt", encoding="utf-8") as stream:
        for line in stream:
            entry = json.loads(line)
            if entry.get("lang_code") != "en": continue
            term = clean(entry["word"]).casefold()
            if not HEAD.fullmatch(term): skipped["unsupported_headword"] += 1; continue
            pos = POS.get(entry.get("pos"), "other")
            senses = []; examples = []
            for sense in entry.get("senses", []):
                for base in sense.get("form_of", []): aliases.append((clean(base["word"]).casefold(), term))
                if sense.get("form_of"): continue
                for gloss in sense.get("glosses", []):
                    gloss = clean(gloss)
                    form = FORM.fullmatch(gloss)
                    if form:
                        aliases.append((form[1].rstrip(".").casefold(), term)); continue
                    if not VI.search(gloss) or "{{" in gloss or "}}" in gloss:
                        skipped["non_vietnamese_or_template_gloss"] += 1; continue
                    senses.append({"pos":pos, "text":gloss, "source":"wiktionary-vi"})
                    for ex in sense.get("examples", []):
                        en, vi = clean(ex.get("text", "")), clean(ex.get("translation", ""))
                        if en and vi and VI.search(vi) and len(en) <= 350 and len(vi) <= 450:
                            examples.append({"en":en, "vi":vi, "source":"wiktionary-vi"})
            if not senses: continue
            item = wiki.setdefault(term, {"senses":[], "examples":[], "sounds":[], "pos":[], "source_term":entry["word"]})
            item["senses"].extend(senses); item["examples"].extend(examples); item["pos"].append(pos)
            item["sounds"].extend(sound.get("ipa", "") for sound in entry.get("sounds", []))
    for term, item in wiki.items():
        if term not in words:
            words[term] = {"id":stable_new(term), "term":term, "ipa":"", "pos":[], "definitions":[],
                           "lists":[{"id":"wiktionary", "rank":None, "supplemental":True}],
                           "inflections":[], "meaning_language":"vi", "aliases":[]}
        word = words[term]
        word["senses_vi"] = list({(s["pos"],s["text"]):s for s in item["senses"]}.values())
        word["examples"] = list({e["en"]:e for e in item["examples"]}.values())[:12]
        word["pos"] = unique(word["pos"] + item["pos"])
        if not word.get("vi_source", "").startswith("dhv"):
            word["meaning_vi"] = "; ".join(s["text"].rstrip(".") for s in word["senses_vi"][:3])
            word["vi_source"] = "wiktionary-vi"; word["translation_status"] = "community"
        word["source_url"] = "https://vi.wiktionary.org/wiki/" + quote(item["source_term"], safe="")
        if not word.get("ipa"):
            pron = next((p for p in item["sounds"] if valid_ipa(p)), "")
            if pron:
                word["ipa"] = "/" + pron.strip("/[]") + "/"; word["ipa_source"] = "Wiktionary"
    for term, edit in EDITORIAL.items():
        if term not in words:
            words[term] = {"id":stable_new(term), "term":term, "ipa":"", "definitions":[],
                          "lists":[{"id":"dhv", "rank":None, "supplemental":True}], "inflections":[],
                          "senses_vi":[], "examples":[], "meaning_language":"vi", "aliases":[]}
        word = words[term]
        word["meaning_vi"] = edit["meaning_vi"]
        word["pos"] = unique(edit["pos"] + word.get("pos", []))
        word["examples"] = edit["examples"] + word.get("examples", [])[:11]
        word["vi_source"] = "dhv"; word["translation_status"] = "edited"
        word["senses_vi"] = [{"pos":edit["pos"][0], "text":edit["meaning_vi"], "source":"dhv"}] + word.get("senses_vi", [])
    for base, form in aliases:
        if base in words and form != base:
            words[base]["inflections"] = unique(words[base].get("inflections", []) + [form])
    for term, forms in ALIASES.items():
        if term in words: words[term]["aliases"] = unique(words[term].get("aliases", []) + forms)
    for term, word in words.items():
        if not word.get("senses_vi"):
            word["senses_vi"] = [{"pos":word["pos"][0] if word["pos"] else "other", "text":word["meaning_vi"],
                                  "source":word.get("vi_source", "thichhoc")}]
        word["examples"] = word.get("examples", [])
        word["example"] = word["examples"][0]["en"] if word["examples"] else word.get("example", "")
        word["inflections"] = unique(clean(f) for f in word.get("inflections", []) if clean(f) and clean(f) != term)
        assert word["meaning_vi"] and word["senses_vi"] and word["pos"], term
        assert not word["ipa"] or valid_ipa(word["ipa"]), term
        assert "\ufffd" not in word["meaning_vi"], term
        if term in original_ids: assert word["id"] == original_ids[term]
    assert len({w["id"] for w in words.values()}) == len(words)
    print(f"Merged {len(words):,} headwords; {len(words)-len(original_ids):,} new; {len(wiki):,} enriched from Wiktionary", flush=True)
    publish(words, legacy, skipped)


def publish(words, legacy, skipped):
    folder = PUBLIC / "dictionary"; folder.mkdir(exist_ok=True)
    index_rows = []; buckets = {}
    def priority_of(word):
        decks = sum(DECK_BITS[s["id"]] for s in word["lists"] if s["id"] in DECK_BITS)
        rank = min((s["rank"] for s in word["lists"] if s.get("rank")), default=9000)
        tier = min((s.get("tier",4) for s in word["lists"]), default=4)
        return rank if decks & 3 else (4000 if word["vi_source"]=="dhv" else 10000+tier*1000)
    rows = sorted(words.values(), key=lambda w:(priority_of(w),w["term"]))
    pos_bits = {pos:1<<i for i,pos in enumerate(["n","v","adj","adv","prep","conj","pron","det","interj","num","phrase","abbr","particle","prefix","suffix","other"])}
    with tempfile.TemporaryDirectory(prefix="dhv-dictionary-build-") as build_dir:
        db_path = Path(build_dir) / "dictionary.sqlite3"
        db = sqlite3.connect(db_path)
        db.executescript("""
          PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF; PRAGMA page_size=4096;
          CREATE TABLE words (id TEXT PRIMARY KEY, term TEXT, lookup TEXT, compact TEXT, letter TEXT,
              decks INTEGER, pos INTEGER, priority INTEGER, vi_exact TEXT, data TEXT);
          CREATE TABLE forms (lookup TEXT, word_id TEXT, PRIMARY KEY (lookup, word_id)) WITHOUT ROWID;
          CREATE VIRTUAL TABLE search USING fts5(headword, forms, vi, en, content='', tokenize='unicode61 remove_diacritics 2');
        """)
        for number, word in enumerate(rows):
            decks = sum(DECK_BITS[s["id"]] for s in word["lists"] if s["id"] in DECK_BITS)
            bits = sum(pos_bits.get(p,pos_bits["other"]) for p in set(word["pos"]))
            priority = priority_of(word)
            vi = " ; ".join(unique([word["meaning_vi"]] + [s["text"] for s in word["senses_vi"]]))
            en = " ".join(d["text"] for d in word["definitions"])
            forms = unique(word["inflections"] + word.get("aliases", []))
            key = normalize(word["term"])
            segments = "|" + "|".join(unique(normalize(g) for g in re.split(r"[;,]", vi) if normalize(g))) + "|"
            encoded = json.dumps(word,ensure_ascii=False,separators=(",", ":"))
            db.execute("INSERT INTO words VALUES (?,?,?,?,?,?,?,?,?,?)", (word["id"],word["term"],key,compact(key),key[:1],decks,bits,priority,segments,encoded))
            rowid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            db.execute("INSERT INTO search(rowid,headword,forms,vi,en) VALUES (?,?,?,?,?)",(rowid,key,normalize(" ; ".join(forms)),normalize(vi),normalize(en)))
            db.executemany("INSERT OR IGNORE INTO forms VALUES (?,?)",[(compact(f),word["id"]) for f in forms+[word["term"]] if compact(f)])
            bucket=f"{number // 512:04x}"
            buckets.setdefault(bucket, {})[word["id"]]=word
            # Compact search payload; full senses/examples are loaded one shard at a time.
            index_rows.append([word["id"],word["term"],word["meaning_vi"],forms,word["pos"],decks,priority,vi,en,bucket])
        db.executescript("""
          CREATE INDEX words_lookup ON words(lookup);
          CREATE INDEX words_compact ON words(compact);
          CREATE INDEX words_priority ON words(priority,term);
          CREATE INDEX words_letter ON words(letter);
          INSERT INTO search(search) VALUES ('optimize');
        """)
        db.commit(); db.execute("VACUUM"); db.close()
        (DATA / "dictionary.sqlite3.gz").write_bytes(gzip.compress(db_path.read_bytes(),compresslevel=9,mtime=0))
    gzip_json(folder / "search.json.gz", index_rows)
    for bucket, content in buckets.items(): gzip_json(folder / f"entries-{bucket}.json.gz", content)
    # Public licensed export; no personal learning records are ever included.
    gzip_json(folder / "dictionary.json.gz", rows)
    stats = {"word_count":len(rows), "new_headwords":len(rows)-147245,
             "vietnamese_senses":sum(len(w["senses_vi"]) for w in rows),
             "bilingual_examples":sum(len(w["examples"]) for w in rows),
             "with_ipa":sum(bool(w["ipa"]) for w in rows),
             "translation_status":dict(Counter(w["translation_status"] for w in rows)),
             "editorial_entries":len(EDITORIAL), "skipped":dict(skipped)}
    meta = {k:v for k,v in legacy.items() if k not in ("words", "changes", "version", "word_count")}
    # .gitattributes normalizes text to LF. Keep the upstream byte fingerprint
    # and separately record the canonical repository representation.
    for source in meta["source_files"]:
        path = DATA / "vendor/ngsl-tsl" / source["file"]
        if path.suffix in {".csv", ".json", ".txt", ".md"}:
            source["repository_sha256"] = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            source["repository_normalization"] = "CRLF to LF"
    meta.update({"version":"dhv-dictionary-2026.10.28-v2", "word_count":len(rows), "stats":stats,
                 "inputs":[{"file":name,"sha256":sha,"url":url} for name,(sha,url) in INPUTS.items()],
                 "database":{"file":"dictionary.sqlite3.gz","sha256":digest(DATA/"dictionary.sqlite3.gz")},
                 "deck_counts":dict(Counter(s["id"] for w in rows for s in w["lists"])),
                 "pos_bits":pos_bits,
                 "files":{name:transport_metadata(folder/name) for name in ["search.json.gz","dictionary.json.gz"] + [f"entries-{bucket}.json.gz" for bucket in buckets]},
                 "download_url":"/toeic/dictionary/dictionary.json.gz",
                 "attribution_url":"/toeic/licenses/DICTIONARY.md"})
    for path in [DATA/"dictionary-meta.json",PUBLIC/"dictionary-meta.json"]:
        path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    notice = f"""# Từ điển Anh–Việt DHV · 2026-10-28

Dữ liệu tổng hợp: **CC BY-SA 4.0**. https://creativecommons.org/licenses/by-sa/4.0/
Gồm {len(rows):,} mục từ, {stats['vietnamese_senses']:,} nghĩa tiếng Việt và {stats['bilingual_examples']:,} ví dụ song ngữ.

## Nguồn
- NGSL 1.2 — Charles Browne, Brent Culligan, Joseph Phillips; TOEIC Service List 1.2 — Charles Browne, Brent Culligan. CC BY-SA 4.0. https://www.newgeneralservicelist.com/
- Wiktionary tiếng Việt, cộng đồng đóng góp; bản trích xuất Wiktextract qua Kaikki.org, tải 2026-10-28. https://vi.wiktionary.org/ · https://kaikki.org/dictionary/rawdata.html · CC BY-SA 4.0. Mỗi mục có URL nguồn để xem lịch sử đóng góp.
- Dữ liệu từ điển: Từ điển Anh–Việt thichhoc.com (thichhoc-dict), giấy phép CC BY-SA 4.0. https://github.com/thichhoc-org/thichhoc-dict · commit {REVISION}. Nguồn gốc: WordNet 3.1 (Princeton), CMUdict (CMU), Wiktionary. **Đã chỉnh sửa dữ liệu.** Giữ mục từ ghi nguồn `thichhoc`.
- Phiên âm nền tảng: open-dict-data/ipa-dict (MIT); CMUdict (BSD 2-clause); Wiktionary (CC BY-SA 4.0). Các thông báo cũ nằm ở NGSL-TSL.md, IPA-MIT-LICENSE.txt và THICHHOC-LICENSE-DATA.md cùng thư mục.
- {len(EDITORIAL)} mục từ được DHV bổ sung/biên tập nghĩa và ví dụ song ngữ, phát hành CC BY-SA 4.0. Không sử dụng định nghĩa từ từ điển thương mại.

## Thay đổi và giới hạn
Giữ ID cũ và lịch ôn tập; bổ sung nghĩa đầy đủ theo từ loại, ví dụ có bản dịch, biến thể và mục từ mới. Loại bỏ phiên âm đoán/ký tự hỏng; từ không có phiên âm đáng tin cậy để trống. Không tự gán giọng Mỹ cho phiên âm không ghi rõ vùng miền. Phiên âm có nguồn cho {stats['with_ipa']:,}/{len(rows):,} mục từ.

Nguồn thichhoc v0.9.0 tự công bố bản dịch máy chưa được con người duyệt. Các mục còn dựa vào nguồn này được gắn `translation_status: machine`; bản cộng đồng `community`; phần biên soạn DHV `edited`. Các nhãn này mô tả nguồn, không phải chứng nhận chính xác tuyệt đối. Không quảng cáo kho dữ liệu là đầy đủ mọi từ tiếng Anh.

Tái phân phối phải giữ ghi nguồn, giấy phép và nêu thay đổi. Giấy phép dữ liệu không thay đổi giấy phép mã nguồn ứng dụng. Mã SHA-256 và đường dẫn nguồn được ghi tại `/toeic/dictionary-meta.json`. Bản tải JSON không chứa tiến độ hay dữ liệu tài khoản.
"""
    (PUBLIC/"licenses/DICTIONARY.md").write_text(notice,encoding="utf-8")
    print(json.dumps(stats,ensure_ascii=False),flush=True)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir",required=True,help="Folder with the two pinned source archives")
    build(parser.parse_args().source_dir)
