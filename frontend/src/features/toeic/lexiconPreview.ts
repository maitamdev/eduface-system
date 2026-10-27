import type { LexiconCard, LexiconPage, LexiconWord } from "./api";

type Dataset = Pick<LexiconPage, "version" | "word_count" | "license" | "license_url" | "sources"> & {words: LexiconWord[]};
let dataset: Promise<Dataset> | undefined;
const funcPos = new Set(["prep", "conj", "pron", "det", "interj"]);
const normalize = (value: string) => value.toLowerCase().replace(/e-mail/g, "email").replace(/đ/g, "d").normalize("NFKD").replace(/\p{M}/gu, "").trim();

export async function previewLexicon(params: URLSearchParams): Promise<LexiconPage> {
  if (!dataset) dataset = fetch("/toeic/lexicon.json").then(response => {
    if (!response.ok) throw new Error("Chưa tải được dữ liệu từ vựng xem thử.");
    return response.json() as Promise<Dataset>;
  }).catch(error => {dataset = undefined; throw error;});
  const data = await dataset;
  const deck = params.get("deck") || "all", query = normalize(params.get("q") || ""), state = params.get("state") || "all";
  const pos = params.get("pos") || "all", letter = normalize(params.get("letter") || "all");
  const limit = Math.max(1, Math.min(50, Number(params.get("limit")) || 30));
  const offset = Math.max(0, Number(params.get("offset")) || 0);
  const matching = data.words.filter(word => {
    const wordPos = word.pos || [];
    const posMatch = pos === "all" || (pos === "func" ? wordPos.some(p => funcPos.has(p)) : wordPos.includes(pos as never));
    const letterMatch = !letter || letter === "all" || normalize(word.term).startsWith(letter);
    const text = normalize(`${word.term} ${word.meaning_vi || ""} ${word.definitions.map(d => d.text).join(" ")} ${word.example || ""}`);
    return (deck === "all" || word.lists.some(source => source.id === deck)) && posMatch && letterMatch && (!query || text.includes(query));
  });
  if (deck !== "all") matching.sort((a, b) => (a.lists.find(s => s.id === deck)?.rank || 100000) - (b.lists.find(s => s.id === deck)?.rank || 100000) || a.term.localeCompare(b.term));
  else if (letter && letter !== "all" && !query) matching.sort((a, b) => a.term.localeCompare(b.term));
  if (query) {
    const rankMatch = (w: LexiconWord) => {
      const termNorm = normalize(w.term);
      const viNorm = normalize(w.meaning_vi || "");
      const viParts = viNorm.split(/[;,]/).map(s => s.trim()).filter(Boolean);
      return [
        Number(termNorm !== query),
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
