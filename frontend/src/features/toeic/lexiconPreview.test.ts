import {beforeEach,afterEach,expect,it,vi} from "vitest";
import {readFileSync} from "node:fs";
const data=JSON.parse(readFileSync(new URL("../../../public/toeic/lexicon.json",import.meta.url),"utf8"));
beforeEach(()=>{vi.resetModules();vi.stubGlobal("fetch",vi.fn().mockResolvedValue({ok:true,json:async()=>data}));});
afterEach(()=>vi.unstubAllGlobals());
it("loads the real licensed dataset lazily and mirrors paginated deck lookup",async()=>{
 const {previewLexicon}=await import("./lexiconPreview");
 const first=await previewLexicon(new URLSearchParams("deck=ngsl&limit=30"));
 const next=await previewLexicon(new URLSearchParams("deck=ngsl&limit=30&offset=30"));
 expect(first.total).toBe(2809);expect(first.items).toHaveLength(30);
 expect(first.items[0].term).toBe("the");
 expect(next.items.some(w=>first.items.some(a=>a.id===w.id))).toBe(false);
 expect(fetch).toHaveBeenCalledTimes(1);
 const cafe=await previewLexicon(new URLSearchParams("deck=tsl&q=cafe"));
 expect(cafe.items.some(w=>w.term==="café")).toBe(true);
 const due=await previewLexicon(new URLSearchParams("state=due"));
 expect(due.total).toBe(0);expect(due.new_count).toBe(4060);
});
it("allows retrying a failed public-data fetch",async()=>{
 vi.mocked(fetch).mockRejectedValueOnce(new Error("offline"));
 const {previewLexicon}=await import("./lexiconPreview");
 await expect(previewLexicon(new URLSearchParams())).rejects.toThrow("offline");
 expect((await previewLexicon(new URLSearchParams("q=e-mail"))).items[0].term).toBe("email");
});
