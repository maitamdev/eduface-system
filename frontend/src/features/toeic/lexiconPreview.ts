import type { LexiconCard, LexiconPage, LexiconWord } from "./api";

type Dataset = Pick<LexiconPage, "version" | "word_count" | "license" | "license_url" | "sources"> & {words: LexiconWord[]};
let dataset: Promise<Dataset> | undefined;
const normalize = (value: string) => value.toLowerCase().replace(/e-mail/g, "email").normalize("NFKD").replace(/\p{M}/gu, "").trim();

export async function previewLexicon(params: URLSearchParams): Promise<LexiconPage> {
  if (!dataset) dataset = fetch("/toeic/lexicon.json").then(response => {
    if (!response.ok) throw new Error("Chưa tải được dữ liệu từ vựng xem thử.");
    return response.json() as Promise<Dataset>;
  }).catch(error => {dataset = undefined; throw error;});
  const data = await dataset;
  const deck = params.get("deck") || "all", query = normalize(params.get("q") || ""), state = params.get("state") || "all";
  const limit = Math.max(1, Math.min(50, Number(params.get("limit")) || 30));
  const offset = Math.max(0, Number(params.get("offset")) || 0);
  const matching = data.words.filter(word => (deck === "all" || word.lists.some(source => source.id === deck)) &&
    (!query || normalize(word.term + " " + word.definitions.map(d => d.text).join(" ")).includes(query)));
  if (deck !== "all") matching.sort((a, b) => (a.lists.find(s => s.id === deck)?.rank || 100000) - (b.lists.find(s => s.id === deck)?.rank || 100000) || a.term.localeCompare(b.term));
  if (query) matching.sort((a, b) => Number(normalize(a.term) !== query) - Number(normalize(b.term) !== query) || Number(!normalize(a.term).startsWith(query)) - Number(!normalize(b.term).startsWith(query)));
  const filtered = state === "due" || state === "learned" ? [] : matching;
  const items: LexiconCard[] = filtered.slice(offset, offset + limit).map(word => ({...word, lesson_id:"open-lexicon", meaning:[...new Set(word.definitions.map(d => d.text))].join(" / "), example:"", due:null, version:0, reviews:0}));
  return {version:data.version, word_count:data.word_count, total:filtered.length, offset, limit, due_count:0, new_count:matching.length, items, license:data.license, license_url:data.license_url, sources:data.sources, download_url:"/toeic/lexicon.json", attribution_url:"/toeic/licenses/NGSL-TSL.md"};
}
