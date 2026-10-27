"""Local, separately licensed 147,245-word bilingual English-Vietnamese lexicon; never fetched at request time."""
import gzip
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "data/toeic/lexicon.json"
EXT_PATH = Path(__file__).resolve().parents[1] / "data/toeic/lexicon_100k.json.gz"
FUNC_POS = {"prep", "conj", "pron", "det", "interj"}

_DIACRITIC_CHARS = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđéèêëáàäâíìïîóòöôúùüûçñ"
_VI_TRANS = str.maketrans({
    c: "".join(ch for ch in unicodedata.normalize("NFKD", c.replace("đ", "d").replace("Đ", "d")) if not unicodedata.combining(ch))
    for c in _DIACRITIC_CHARS + _DIACRITIC_CHARS.upper()
})


def normalize(value):
    return value.casefold().replace("e-mail", "email").translate(_VI_TRANS).strip()


@lru_cache(maxsize=1)
def lexicon():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    ext_rows = json.loads(gzip.decompress(EXT_PATH.read_bytes()).decode("utf-8"))
    ext_words = [
        {
            "id": f"lex-th-{i:06d}",
            "term": row[0],
            "ipa": row[1],
            "pos": row[2],
            "meaning_vi": row[3],
            "meaning_language": "en",
            "definitions": [{"source_id": "thichhoc", "text": row[4], "source_term": row[0], "adapted_by_dhv": False}],
            "lists": [{"id": "thichhoc", "rank": None, "tier": row[5], "supplemental": False}],
            "inflections": row[6],
        }
        for i, row in enumerate(ext_rows, 1)
    ]
    data["words"] = data["words"] + ext_words
    assert data["license"] == "CC BY-SA 4.0"
    assert len(data["words"]) == data["word_count"] == 147245
    assert len({w["id"] for w in data["words"]}) == data["word_count"]
    assert all(w.get("ipa") and w.get("pos") and w.get("meaning_vi") for w in data["words"])
    return data


@lru_cache(maxsize=1)
def index():
    return {w["id"]: w for w in lexicon()["words"]}


@lru_cache(maxsize=1)
def deck_pools():
    all_words = lexicon()["words"]
    ngsl = sorted(
        [w for w in all_words if any(s["id"] == "ngsl" for s in w["lists"])],
        key=lambda w: (next(s["rank"] for s in w["lists"] if s["id"] == "ngsl") or 100000, w["term"]),
    )
    tsl = sorted(
        [w for w in all_words if any(s["id"] == "tsl" for s in w["lists"])],
        key=lambda w: (next(s["rank"] for s in w["lists"] if s["id"] == "tsl") or 100000, w["term"]),
    )
    core = [w for w in all_words if any(s["id"] in ("ngsl", "tsl") for s in w["lists"])]
    thichhoc = [w for w in all_words if any(s["id"] == "thichhoc" for s in w["lists"])]
    return {"all": all_words, "core": core, "ngsl": ngsl, "tsl": tsl, "thichhoc": thichhoc}


_SEARCH_CACHE: dict[str, str] = {}


def word_blob(w):
    wid = w["id"]
    blob = _SEARCH_CACHE.get(wid)
    if blob is None:
        blob = normalize(
            w["term"]
            + " "
            + w["meaning_vi"]
            + " "
            + " ".join(d["text"] for d in w["definitions"])
            + " "
            + " ".join(w.get("inflections", []))
            + " "
            + w.get("example", "")
        )
        _SEARCH_CACHE[wid] = blob
    return blob


def matches_pos(word, pos):
    if pos == "all":
        return True
    if pos == "func":
        return any(p in FUNC_POS for p in word["pos"])
    return pos in word["pos"]


def matches_letter(word, letter):
    if not letter or letter == "all":
        return True
    return normalize(word["term"]).startswith(letter.casefold())


def search_words(deck="all", query="", pos="all", letter="all"):
    query = normalize(query)
    pool = deck_pools().get(deck, lexicon()["words"])
    words = [
        w for w in pool
        if matches_pos(w, pos)
        and matches_letter(w, letter)
        and (not query or query in word_blob(w))
    ]
    if letter and letter != "all" and not query and deck in ("all", "core", "thichhoc"):
        words.sort(key=lambda w: w["term"])
    if query:
        def rank_match(w):
            is_ext = w["id"].startswith("lex-th-")
            term_norm = normalize(w["term"])
            if term_norm == query:
                return (0, is_ext, 0, 0)
            infs = {normalize(inf) for inf in w.get("inflections", [])}
            if query in infs:
                return (1, is_ext, 0, 0)
            vi_norm = normalize(w["meaning_vi"])
            vi_parts = {s.strip() for s in re.split(r"[;,]", vi_norm) if s.strip()}
            return (
                2,
                not term_norm.startswith(query),
                query not in vi_parts and not vi_norm.startswith(query),
                query not in vi_norm,
            )
        words.sort(key=rank_match)
    return words


def card_view(word, stored=None):
    current = stored or {}
    return word | {
        "lesson_id": "open-lexicon",
        "meaning": word["meaning_vi"],
        "meaning_en": " / ".join(dict.fromkeys(d["text"] for d in word["definitions"])),
        "example": word.get("example", ""),
        "version": current.get("version", 0),
        "due": current.get("due"),
        "reviews": current.get("reviews", 0),
    }
