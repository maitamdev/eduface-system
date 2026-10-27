"""Local, separately licensed bilingual English-Vietnamese lexicon; never fetched at request time."""
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "data/toeic/lexicon.json"
FUNC_POS = {"prep", "conj", "pron", "det", "interj"}


def normalize(value):
    folded = value.casefold().replace("e-mail", "email").replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFKD", folded) if not unicodedata.combining(c)).strip()


@lru_cache(maxsize=1)
def lexicon():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    assert data["license"] == "CC BY-SA 4.0"
    assert len(data["words"]) == data["word_count"]
    assert len({w["id"] for w in data["words"]}) == data["word_count"]
    assert all(w.get("ipa") and w.get("pos") and w.get("meaning_vi") for w in data["words"])
    return data


@lru_cache(maxsize=1)
def index():
    return {w["id"]: w for w in lexicon()["words"]}


@lru_cache(maxsize=1)
def search_text():
    return {
        w["id"]: normalize(
            w["term"] + " " + w["meaning_vi"] + " " + " ".join(d["text"] for d in w["definitions"]) + " " + w.get("example", "")
        )
        for w in lexicon()["words"]
    }


@lru_cache(maxsize=1)
def vi_senses():
    return {
        w["id"]: (
            normalize(w["meaning_vi"]),
            {s.strip() for s in re.split(r"[;,]", normalize(w["meaning_vi"])) if s.strip()},
        )
        for w in lexicon()["words"]
    }


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
    words = [
        w for w in lexicon()["words"]
        if (deck == "all" or any(s["id"] == deck for s in w["lists"]))
        and matches_pos(w, pos)
        and matches_letter(w, letter)
        and (not query or query in search_text()[w["id"]])
    ]
    if deck != "all":
        words.sort(key=lambda w: (next(s["rank"] for s in w["lists"] if s["id"] == deck) or 100000, w["term"]))
    elif letter and letter != "all" and not query:
        words.sort(key=lambda w: w["term"])
    if query:
        def rank_match(w):
            term_norm = normalize(w["term"])
            vi_norm, vi_parts = vi_senses()[w["id"]]
            return (
                term_norm != query,
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
