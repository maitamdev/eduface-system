import type { LexiconCard, LexiconPage, LexiconWord, PosTag } from "./api";

type Dataset = Pick<LexiconPage, "version" | "word_count" | "license" | "license_url" | "sources"> & {words: LexiconWord[]; _hasHeaders?: boolean; _extLoaded?: boolean};
type ExtRow = [string, string, PosTag[], string, string, number, string[]];
let dataset: Promise<Dataset> | undefined;
let extPromise: Promise<void> | undefined;
const funcPos = new Set(["prep", "conj", "pron", "det", "interj"]);
const normalize = (value: string) => value.toLowerCase().replace(/e-mail/g, "email").replace(/đ/g, "d").normalize("NFKD").replace(/\p{M}/gu, "").trim();

async function ensureExtended(data: Dataset) {
  if (data._extLoaded || !data._hasHeaders || typeof DecompressionStream === "undefined") return;
  if (!extPromise) {
    extPromise = fetch("/toeic/lexicon_100k.json.gz").then(async res => {
      if (!res.ok || !res.body) return;
      const stream = res.body.pipeThrough(new DecompressionStream("gzip"));
      const rows = (await new Response(stream).json()) as ExtRow[];
      const extWords: LexiconWord[] = rows.map((row, i) => ({
        id: `lex-th-${String(i + 1).padStart(6, "0")}`,
        term: row[0],
        ipa: row[1],
        pos: row[2],
        meaning_vi: row[3],
        meaning_language: "en",
        definitions: [{source_id: "thichhoc", text: row[4], source_term: row[0], adapted_by_dhv: false}],
        lists: [{id: "thichhoc", rank: null, tier: row[5], supplemental: false}],
        inflections: row[6],
      }));
      data.words = data.words.concat(extWords);
      data._extLoaded = true;
    }).catch(() => { extPromise = undefined; });
  }
  await extPromise;
}

export async function previewLexicon(params: URLSearchParams): Promise<LexiconPage> {
  if (!dataset) dataset = fetch("/toeic/lexicon.json").then(async response => {
    if (!response.ok) throw new Error("Chưa tải được dữ liệu từ vựng xem thử.");
    const parsed = (await response.json()) as Dataset;
    parsed._hasHeaders = Boolean(response.headers);
    return parsed;
  }).catch(error => {dataset = undefined; throw error;});
  const data = await dataset;
  const deck = params.get("deck") || "all", query = normalize(params.get("q") || ""), state = params.get("state") || "all";
  if (deck === "all" || deck === "thichhoc") await ensureExtended(data);
  const pos = params.get("pos") || "all", letter = normalize(params.get("letter") || "all");
  const limit = Math.max(1, Math.min(50, Number(params.get("limit")) || 30));
  const offset = Math.max(0, Number(params.get("offset")) || 0);
  const matching = data.words.filter(word => {
    const wordPos = word.pos || [];
    const posMatch = pos === "all" || (pos === "func" ? wordPos.some(p => funcPos.has(p)) : wordPos.includes(pos as never));
    const letterMatch = !letter || letter === "all" || normalize(word.term).startsWith(letter);
    const deckMatch = deck === "all" || (deck === "core" ? word.lists.some(s => s.id === "ngsl" || s.id === "tsl") : word.lists.some(source => source.id === deck));
    if (!deckMatch || !posMatch || !letterMatch) return false;
    if (!query) return true;
    const text = normalize(`${word.term} ${word.meaning_vi || ""} ${word.definitions.map(d => d.text).join(" ")} ${(word.inflections || []).join(" ")} ${word.example || ""}`);
    return text.includes(query);
  });
  if (deck === "ngsl" || deck === "tsl") matching.sort((a, b) => (a.lists.find(s => s.id === deck)?.rank || 100000) - (b.lists.find(s => s.id === deck)?.rank || 100000) || a.term.localeCompare(b.term));
  else if (letter && letter !== "all" && !query) matching.sort((a, b) => a.term.localeCompare(b.term));
  if (query) {
    const rankMatch = (w: LexiconWord) => {
      const isExt = Number(w.id.startsWith("lex-th-"));
      const termNorm = normalize(w.term);
      if (termNorm === query) return [0, isExt, 0, 0];
      const infs = (w.inflections || []).map(normalize);
      if (infs.includes(query)) return [1, isExt, 0, 0];
      const viNorm = normalize(w.meaning_vi || "");
      const viParts = viNorm.split(/[;,]/).map(s => s.trim()).filter(Boolean);
      return [
        2,
        Number(!termNorm.startsWith(query)),
        Number(!viParts.includes(query) && !viNorm.startsWith(query)),
        Number(!viNorm.includes(query)),
      ];
    };
    matching.sort((a, b) => {
      const ra = rankMatch(a), rb = rankMatch(b);
      for (let i = 0; i < ra.length; i++) if (ra[i] !== rb[i]) return ra[i] - rb[i];
      return 0;
    });
  }
  const filtered = state === "due" || state === "learned" ? [] : matching;
  const items: LexiconCard[] = filtered.slice(offset, offset + limit).map(word => ({
    ...word,
    lesson_id: "open-lexicon",
    meaning: word.meaning_vi || [...new Set(word.definitions.map(d => d.text))].join(" / "),
    meaning_en: [...new Set(word.definitions.map(d => d.text))].join(" / "),
    example: word.example || "",
    due: null,
    version: 0,
    reviews: 0,
  }));
  return {
    version: data.version, word_count: data.word_count, total: filtered.length, offset, limit,
    due_count: 0, new_count: matching.length, items, license: data.license, license_url: data.license_url,
    sources: data.sources, download_url: "/toeic/lexicon.json", handbook_url: "/toeic/so-tay-tu-vung-song-ngu.md",
    attribution_url: "/toeic/licenses/NGSL-TSL.md",
  };
}
