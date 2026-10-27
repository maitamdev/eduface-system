"""Indexed local English–Vietnamese dictionary; no network calls or user data cache.

Only the requested page of definitions is decoded. The compressed, versioned
SQLite artifact is expanded atomically to a disposable local cache, preventing
hundreds of thousands of Python dictionaries from filling the API worker's RAM.
"""
import gzip
import hashlib
import json
import os
import re
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from threading import Lock

from core.dictionary_text import normalize, compact

ROOT = Path(__file__).resolve().parents[1] / "data/toeic"
DECKS = {"all":0, "core":3, "ngsl":1, "tsl":2, "thichhoc":4, "wiktionary":8, "dhv":16}
FUNC_POS = ("prep", "conj", "pron", "det", "interj")
_database_lock = Lock()


@lru_cache(maxsize=1)
def lexicon():
    return json.loads((ROOT / "dictionary-meta.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def database_path():
    meta = lexicon()["database"]
    source = ROOT / meta["file"]
    with source.open("rb") as stream:
        assert hashlib.file_digest(stream, "sha256").hexdigest() == meta["sha256"], "Dictionary checksum mismatch"
    folder = Path(tempfile.gettempdir()) / "eduface-dictionary-cache"
    folder.mkdir(exist_ok=True)
    destination = folder / (meta["sha256"] + ".sqlite3")
    with _database_lock:
        if not destination.exists():
            handle, name = tempfile.mkstemp(prefix="dictionary-", suffix=".tmp", dir=folder)
            try:
                with os.fdopen(handle, "wb") as output, gzip.open(source, "rb") as input_file:
                    shutil.copyfileobj(input_file, output)
                os.replace(name, destination)
            finally:
                Path(name).unlink(missing_ok=True)
    return destination


@contextmanager
def connection():
    db = sqlite3.connect(database_path().as_uri() + "?mode=ro", uri=True)
    try:
        db.execute("PRAGMA query_only=ON")
        yield db
    finally:
        db.close()


def _filters(deck, pos, letter):
    where = []; args = []
    if DECKS.get(deck, 0): where.append("w.decks & ? != 0"); args.append(DECKS[deck])
    bits = lexicon()["pos_bits"]
    if pos != "all":
        bit = sum(bits[p] for p in FUNC_POS) if pos == "func" else bits.get(pos, 0)
        where.append("w.pos & ? != 0"); args.append(bit)
    if letter and letter != "all": where.append("w.letter = ?"); args.append(letter.lower())
    return where, args


@lru_cache(maxsize=24)
def search_ids(deck="all", query="", pos="all", letter="all", scope="lookup"):
    query = query.strip()
    key = normalize(query)
    if query and not key: return ()
    where, args = _filters(deck, pos, letter)
    score = "w.priority, w.term"
    if key:
        # The user's text is normalized into tokens, never interpreted as SQL
        # or FTS operators. Phrase-prefix search respects word boundaries.
        fields = "{headword forms vi en}" if scope == "full" else "{headword forms vi}"
        expression = fields + ' : "' + key + '"*'
        where.append("(w.rowid IN (SELECT rowid FROM search WHERE search MATCH ?) OR w.id IN (SELECT word_id FROM forms WHERE lookup = ?))")
        args.extend([expression, compact(key)])
        score = """CASE
          WHEN w.term = ? COLLATE NOCASE THEN 0
          WHEN w.lookup = ? THEN 1
          WHEN w.compact = ? THEN 2
          WHEN w.id IN (SELECT word_id FROM forms WHERE lookup = ?) THEN 3
          WHEN instr(w.vi_exact, ?) > 0 THEN 4
          WHEN substr(w.lookup, 1, length(?)) = ? THEN 5
          ELSE 6 END, w.priority, length(w.term), w.term"""
        order_args = [query.casefold(), key, compact(key), compact(key), "|"+key+"|", key, key]
    else:
        order_args = []
        if letter and letter != "all": score = "w.term, w.priority"
    with connection() as db:
        return tuple(row[0] for row in db.execute("SELECT w.id FROM words w" + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY " + score, args + order_args))


def read_words(ids):
    if not ids: return []
    with connection() as db:
        found = {row[0]:json.loads(row[1]) for row in db.execute(
            "SELECT id, data FROM words WHERE id IN (" + ",".join("?" for _ in ids) + ")", list(ids))}
    return [found[wid] for wid in ids if wid in found]


def all_words():
    """Streaming interface for offline data validation, never for an HTTP page."""
    with connection() as db:
        for row in db.execute("SELECT data FROM words ORDER BY rowid"):
            yield json.loads(row[0])


def has_word(word_id):
    with connection() as db:
        return db.execute("SELECT 1 FROM words WHERE id = ?", (word_id,)).fetchone() is not None


def search_words(deck="all", query="", pos="all", letter="all", scope="lookup"):
    """Compatibility helper for authoring/tests. HTTP uses paged read_words."""
    ids = search_ids(deck, query, pos, letter, scope)
    return [word for start in range(0,len(ids),500) for word in read_words(ids[start:start+500])]


def _edit_distance(a, b, limit):
    """Bounded Damerau–Levenshtein, including a swapped adjacent character."""
    if abs(len(a)-len(b)) > limit: return limit+1
    previous = list(range(len(b)+1)); before = previous
    for i, ca in enumerate(a,1):
        current = [i] + [limit+1]*len(b)
        for j in range(max(1,i-limit),min(len(b),i+limit)+1):
            current[j] = min(current[j-1]+1,previous[j]+1,previous[j-1]+(ca!=b[j-1]))
            if i>1 and j>1 and ca==b[j-2] and a[i-2]==b[j-1]: current[j]=min(current[j],before[j-2]+1)
        if min(current)>limit: return limit+1
        before,previous=previous,current
    return previous[-1]


@lru_cache(maxsize=128)
def suggestions(query):
    key=normalize(query)
    # Suggestions are separate, clickable alternatives; never silently replace
    # a query or fabricate a translation. Avoid suggesting English for VI text.
    if not re.fullmatch(r"[a-z]{3,30}",query.strip().casefold()): return ()
    with connection() as db:
        if db.execute("SELECT 1 FROM forms WHERE lookup=? LIMIT 1",(compact(key),)).fetchone(): return ()
        limit=1 if len(key)<6 else 2
        candidates=db.execute("""SELECT term,lookup,priority FROM words
            WHERE length(lookup) BETWEEN ? AND ? AND instr(lookup,' ')=0
            AND (letter=? OR substr(lookup,2,2)=? OR substr(lookup,1,2)=?)""",
            (len(key)-limit,len(key)+limit,key[0],key[1:3],key[1:3])).fetchall()
    ranked=[]
    for term,normalized,priority in candidates:
        distance=_edit_distance(key,normalized,limit)
        if 0<distance<=limit: ranked.append((distance,priority,abs(len(normalized)-len(key)),term))
    ranked.sort()
    seen=set(); result=[]
    for distance,priority,delta,term in ranked:
        if normalize(term) not in seen: result.append(term); seen.add(normalize(term))
        if len(result)==5: break
    return tuple(result)


def lookup_result(deck="all", query="", pos="all", letter="all", scope="lookup"):
    ids=search_ids(deck,query,pos,letter,scope)
    alternatives=suggestions(query) if query and not ids else ()
    global_total=len(search_ids("all",query,scope=scope)) if query and not ids and (deck!="all" or pos!="all" or letter!="all") else None
    return ids, alternatives, global_total


def card_view(word, stored=None, query=""):
    current=stored or {}
    key=normalize(query)
    forms={compact(f) for f in word.get("inflections",[])+word.get("aliases",[])}
    match="headword" if key and compact(word["term"])==compact(key) else "form" if key and compact(key) in forms else None
    return word | {"lesson_id":"open-lexicon", "meaning":word["meaning_vi"],
        "meaning_en":" / ".join(dict.fromkeys(d["text"] for d in word["definitions"])),
        "example":word.get("example", ""), "version":current.get("version",0),
        "due":current.get("due"), "reviews":current.get("reviews",0), "match_kind":match}
