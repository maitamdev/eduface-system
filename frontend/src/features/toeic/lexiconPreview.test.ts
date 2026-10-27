import {beforeEach,afterEach,expect,it,vi} from "vitest";
import {readFileSync} from "node:fs";
import {gunzipSync} from "node:zlib";
import {normalizeLookup,editDistance} from "./dictionarySearch";
const meta=JSON.parse(readFileSync(new URL("../../../public/toeic/dictionary-meta.json",import.meta.url),"utf8"));
function publicFile(url:string) {
  if(!url.startsWith("/toeic/")) throw new Error("Unexpected resource");
  return new Response(readFileSync(new URL(`../../../public${url}`,import.meta.url)));
}
beforeEach(()=>{vi.resetModules();vi.stubGlobal("fetch",vi.fn(async (url:string)=>publicFile(url)));});
afterEach(()=>vi.unstubAllGlobals());

it("keeps accented, punctuated and inflected lookup consistent with the shipped server dictionary",async()=>{
 const {previewLexicon}=await import("./lexiconPreview");
 for(const [q,term] of [["xin chào","hello"],["tình yêu","love"],["hoa don","invoice"],["went","go"],["studies","study"],["social media","social media"],["résumé","résumé"],["resume","resume"]]) {
   const result=await previewLexicon(new URLSearchParams({q,limit:"5"}));
   expect(result.items[0].term,q).toBe(term);
   expect(result.items[0].meaning_vi).toBeTruthy();
   expect(result.word_count).toBe(meta.word_count);
 }
 const typo=await previewLexicon(new URLSearchParams("q=accomodation"));
 expect(typo.items).toHaveLength(0);expect(typo.suggestions).toContain("accommodation");
 const hidden=await previewLexicon(new URLSearchParams("q=invoice&deck=ngsl&letter=z"));
 expect(hidden.items).toHaveLength(0);expect(hidden.global_total).toBeGreaterThan(0);
 expect(vi.mocked(fetch).mock.calls.filter(([url])=>String(url).endsWith("search.json.gz"))).toHaveLength(1);
},60000);

it("paginates without pretending to have private learner progress",async()=>{
 const {previewLexicon}=await import("./lexiconPreview");
 const first=await previewLexicon(new URLSearchParams("deck=ngsl&limit=30"));
 const next=await previewLexicon(new URLSearchParams("deck=ngsl&limit=30&offset=30"));
 expect(first.total).toBe(2809);expect(first.items).toHaveLength(30);expect(first.items[0].term).toBe("the");
 expect(next.items.some(w=>first.items.some(a=>a.id===w.id))).toBe(false);
 const due=await previewLexicon(new URLSearchParams("state=due&deck=core"));
 expect(due.total).toBe(0);expect(due.new_count).toBe(4060);
 expect(first.items.every(w=>w.version===0 && w.due===null)).toBe(true);
},60000);

it("validates JSON transparently decompressed by Vite or a CDN",async()=>{
 vi.mocked(fetch).mockImplementation(async url=>{
   const result=publicFile(String(url));
   return String(url).endsWith(".gz") ? new Response(gunzipSync(Buffer.from(await result.arrayBuffer())),{headers:{"Content-Encoding":"gzip"}}):result;
 });
 const {previewLexicon}=await import("./lexiconPreview");
 expect((await previewLexicon(new URLSearchParams("q=hoa+don&limit=5"))).items[0].term).toBe("invoice");
},60000);

it("reports an incomplete download as an error, then retries instead of returning a partial dictionary",async()=>{
 let failed=false;
 vi.mocked(fetch).mockImplementation(async (url)=>{
   if(String(url).endsWith("search.json.gz") && !failed){failed=true;return new Response("broken");}
   return publicFile(String(url));
 });
 const {previewLexicon}=await import("./lexiconPreview");
 await expect(previewLexicon(new URLSearchParams("q=invoice"))).rejects.toThrow(/chưa đầy đủ|khác phiên bản/);
 expect((await previewLexicon(new URLSearchParams("q=invoice"))).items[0].term).toBe("invoice");
},60000);

it("normalizes combining Vietnamese accents and catches transposed letters",()=>{
 expect(normalizeLookup("  HÓA\tĐƠN ")).toBe("hoa don");
 expect(normalizeLookup("hoa\u0301 đo\u031bn")).toBe("hoa don");
 expect(normalizeLookup("you’re-welcome")).toBe("you re welcome");
 expect(editDistance("recieve","receive",2)).toBe(1);
 expect(editDistance("invoice","xyz",2)).toBeGreaterThan(2);
});
