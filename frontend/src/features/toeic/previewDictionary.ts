import type {LexiconCard,LexiconPage,LexiconSource,LexiconWord,PosTag} from "./api";
import {normalizeLookup as normalize,compactLookup as compact,containsPhrase,editDistance} from "./dictionarySearch";

type Meta = {version:string;word_count:number;license:string;license_url:string;sources:LexiconSource[];deck_counts:Record<string,number>;download_url:string;attribution_url:string;files:Record<string,{sha256:string;bytes:number;decoded_sha256:string;decoded_bytes:number}>};
type PackedRow = [string,string,string,string[],PosTag[],number,number,string,string,string];
type Row = {id:string;term:string;key:string;compact:string;forms:string[];formsText:string;pos:PosTag[];decks:number;priority:number;vi:string;segments:Set<string>;en:string;bucket:string};
const decks:Record<string,number>={all:0,core:3,ngsl:1,tsl:2,thichhoc:4,wiktionary:8,dhv:16};
const funcPos=new Set(["prep","conj","pron","det","interj"]);
let dataset:Promise<{meta:Meta;rows:Row[]}> | undefined;
const shards=new Map<string,Promise<Record<string,LexiconWord>>>();

async function readCompressed<T>(name:string,meta:Meta):Promise<T> {
  const response=await fetch(`/toeic/dictionary/${name}`);
  if(!response.ok) throw new Error("Chưa tải đủ dữ liệu từ điển. Hãy thử lại khi có kết nối.");
  const bytes=await response.arrayBuffer();
  const signature=new Uint8Array(bytes,0,Math.min(2,bytes.byteLength));
  const compressed=signature[0]===0x1f && signature[1]===0x8b;
  const expected=meta.files[name];
  if(!expected || bytes.byteLength!==(compressed?expected.bytes:expected.decoded_bytes)) throw new Error("Gói từ điển chưa đầy đủ hoặc khác phiên bản. Hãy tải lại trang.");
  if(globalThis.crypto?.subtle) {
    const hash=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",bytes)),b=>b.toString(16).padStart(2,"0")).join("");
    if(hash!==(compressed?expected.sha256:expected.decoded_sha256)) throw new Error("Gói từ điển khác phiên bản. Hãy tải lại trang.");
  }
  // Vite/CDNs can set Content-Encoding: gzip, so fetch already decoded the body.
  if(!compressed) return new Response(bytes).json() as Promise<T>;
  if(typeof DecompressionStream==="undefined") throw new Error("Trình duyệt chưa hỗ trợ dữ liệu xem thử. Hãy cập nhật trình duyệt hoặc đăng nhập để tra từ trên máy chủ.");
  return new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"))).json() as Promise<T>;
}
async function load() {
  if(!dataset) dataset=(async()=>{
    const response=await fetch("/toeic/dictionary-meta.json");
    if(!response.ok) throw new Error("Chưa tải được thông tin từ điển.");
    const meta=await response.json() as Meta;
    const packed=await readCompressed<PackedRow[]>("search.json.gz",meta);
    if(packed.length!==meta.word_count) throw new Error("Chỉ mục từ điển chưa đầy đủ. Hãy tải lại trang.");
    const rows:Row[]=packed.map(r=>({id:r[0],term:r[1],key:normalize(r[1]),compact:compact(r[1]),forms:r[3].map(compact),formsText:normalize(r[3].join(" ; ")),pos:r[4],decks:r[5],priority:r[6],vi:normalize(r[7]),segments:new Set(r[7].split(/[;,]/).map(normalize)),en:normalize(r[8]),bucket:r[9]}));
    return {meta,rows};
  })().catch(error=>{dataset=undefined;shards.clear();throw error;});
  return dataset;
}

function find(rows:Row[],q:string,deck:string,pos:string,letter:string,scope:string) {
  const key=normalize(q),form=compact(q),raw=q.toLowerCase().trim();
  if(q.trim() && !key) return [];
  const matches=rows.filter(w=>(!decks[deck] || !!(w.decks & decks[deck])) && (pos==="all" || (pos==="func" ? w.pos.some(p=>funcPos.has(p)):w.pos.includes(pos as PosTag))) && (letter==="all" || w.key.startsWith(letter)) && (!key || w.compact===form || w.forms.includes(form) || containsPhrase(w.key,key) || containsPhrase(w.formsText,key) || containsPhrase(w.vi,key) || (scope==="full" && containsPhrase(w.en,key))));
  const rank=(w:Row)=>w.term.toLowerCase()===raw?0:w.key===key?1:w.compact===form?2:w.forms.includes(form)?3:w.segments.has(key)?4:w.key.startsWith(key)?5:6;
  matches.sort((a,b)=>key ? rank(a)-rank(b) || a.priority-b.priority || a.term.length-b.term.length || (a.term<b.term?-1:a.term>b.term?1:0) : letter!=="all" ? (a.term<b.term?-1:a.term>b.term?1:0) || a.priority-b.priority : a.priority-b.priority || (a.term<b.term?-1:a.term>b.term?1:0));
  return matches;
}

function suggest(rows:Row[],q:string) {
  const raw=q.toLowerCase().trim(),key=normalize(q),form=compact(q);
  if(!/^[a-z]{3,30}$/.test(raw) || rows.some(w=>w.compact===form || w.forms.includes(form))) return [];
  const limit=key.length<6?1:2;
  const candidates=rows.filter(w=>!w.key.includes(" ") && Math.abs(w.key.length-key.length)<=limit && (w.key[0]===key[0] || w.key.slice(1,3)===key.slice(1,3) || w.key.slice(0,2)===key.slice(1,3))).map(w=>({w,d:editDistance(key,w.key,limit)})).filter(x=>x.d>0 && x.d<=limit);
  candidates.sort((a,b)=>a.d-b.d || a.w.priority-b.w.priority || Math.abs(a.w.key.length-key.length)-Math.abs(b.w.key.length-key.length) || (a.w.term<b.w.term?-1:a.w.term>b.w.term?1:0));
  const seen=new Set<string>();return candidates.filter(x=>{if(seen.has(x.w.key)) return false;seen.add(x.w.key);return true;}).slice(0,5).map(x=>x.w.term);
}

export async function previewDictionary(params:URLSearchParams):Promise<LexiconPage> {
  const {meta,rows}=await load();
  const deck=params.get("deck") || "all",q=(params.get("q") || "").trim(),state=params.get("state") || "all",pos=params.get("pos") || "all",letter=(params.get("letter") || "all").toLowerCase(),scope=params.get("scope") || "lookup";
  const limit=Math.max(1,Math.min(50,Number(params.get("limit")) || 30)),offset=Math.max(0,Number(params.get("offset")) || 0);
  const matched=find(rows,q,deck,pos,letter,scope),filtered=state==="due" || state==="learned"?[]:matched;
  const page=filtered.slice(offset,offset+limit);
  const buckets=[...new Set(page.map(w=>w.bucket))];
  const loaded=await Promise.all(buckets.map(async bucket=>{
    let pending=shards.get(bucket);
    if(!pending) {
      pending=readCompressed<Record<string,LexiconWord>>(`entries-${bucket}.json.gz`,meta).catch(error=>{shards.delete(bucket);throw error;});
      shards.set(bucket,pending);
    }
    return pending;
  }));
  // Keep only detail shards needed by the current page in memory.
  for(const bucket of shards.keys()) if(!buckets.includes(bucket)) shards.delete(bucket);
  const words=Object.assign({},...loaded) as Record<string,LexiconWord>;
  const items:LexiconCard[]=page.map(row=>{
    const word=words[row.id];
    if(!word?.meaning_vi) throw new Error("Chưa tải được nghĩa của từ. Hãy thử lại.");
    return {...word,lesson_id:"open-lexicon",meaning:word.meaning_vi,example:word.example || "",meaning_en:word.definitions.map(d=>d.text).join(" / "),version:0,reviews:0,due:null,match_kind:q && compact(word.term)===compact(q)?"headword":q && row.forms.includes(compact(q))?"form":null};
  });
  return {version:meta.version,word_count:meta.word_count,total:filtered.length,offset,limit,due_count:0,new_count:matched.length,items,suggestions:!matched.length?suggest(rows,q):[],global_total:q && !matched.length && (deck!=="all" || pos!=="all" || letter!=="all")?find(rows,q,"all","all","all",scope).length:null,matched_count:matched.length,deck_counts:meta.deck_counts,license:meta.license,license_url:meta.license_url,sources:meta.sources,download_url:meta.download_url,attribution_url:meta.attribution_url};
}
