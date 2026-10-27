// @vitest-environment jsdom
import {afterEach,beforeEach,expect,it,vi} from "vitest";
import {act,cleanup,fireEvent,render,screen,waitFor,within} from "@testing-library/react";
import {OpenLexicon} from "./OpenLexicon";
import type {LexiconCard,LexiconFilters,LexiconPage} from "./api";
const api=vi.hoisted(()=>({lexicon:vi.fn(),review:vi.fn()}));
vi.mock("./api",async original=>({...await original<typeof import("./api")>(),toeicApi:api}));
const word:LexiconCard={id:"lex-test",lesson_id:"open-lexicon",term:"invoice",ipa:"/ˈɪnvɔɪs/",pos:["n","v"],meaning:"hóa đơn; lập hóa đơn",meaning_vi:"hóa đơn; lập hóa đơn",example:"Please pay the invoice.",examples:[{en:"Please pay the invoice.",vi:"Vui lòng thanh toán hóa đơn.",source:"dhv"}],senses_vi:[{pos:"n",text:"Hóa đơn yêu cầu thanh toán.",source:"dhv"},{pos:"v",text:"Lập hóa đơn cho khách hàng.",source:"dhv"}],version:0,due:null,reviews:0,meaning_language:"vi",translation_status:"edited",definitions:[{source_id:"tsl",text:"a document asking for payment",source_term:"invoice",adapted_by_dhv:false}],lists:[{id:"tsl",rank:90,supplemental:false}]};
const page=(items:LexiconCard[]=[word],total=items.length):LexiconPage=>({version:"test",items,total,word_count:191866,offset:0,limit:30,due_count:0,new_count:total,matched_count:total,suggestions:[],license:"CC BY-SA 4.0",license_url:"https://creativecommons.org/licenses/by-sa/4.0/",sources:[],download_url:"/toeic/dictionary/dictionary.json.gz",attribution_url:"/toeic/licenses/DICTIONARY.md"});
beforeEach(()=>{api.lexicon.mockReset();api.review.mockReset();api.lexicon.mockResolvedValue(page());});
afterEach(()=>{cleanup();vi.useRealTimers();});
const search=()=>screen.getByRole("searchbox",{name:"Tìm từ tiếng Anh hoặc nghĩa tiếng Việt"});
async function openCard() {
 await screen.findByRole("heading",{name:"invoice"});
 fireEvent.click(screen.getByRole("button",{name:"Ôn từ này"}));
 fireEvent.click(screen.getByRole("button",{name:"Hiện đáp án & ví dụ"}));
}

it("opens the complete dictionary and shows Vietnamese and translated examples without a flip",async()=>{
 render(<OpenLexicon preview onReviewed={vi.fn()}/>);
 const detail=await screen.findByRole("article",{name:"Chi tiết từ vựng"});
 expect(within(detail).getByText("hóa đơn; lập hóa đơn")).toBeTruthy();
 expect(within(detail).getByText("Vui lòng thanh toán hóa đơn.")).toBeTruthy();
 expect(within(detail).getByText("/ˈɪnvɔɪs/")).toBeTruthy();
 expect(screen.queryByRole("button",{name:"Nhớ được"})).toBeNull();
 fireEvent.click(screen.getByText("Xem đầy đủ 2 nghĩa theo từ loại"));
 expect(within(detail).getByText("Lập hóa đơn cho khách hàng.")).toBeTruthy();
 expect(api.lexicon).toHaveBeenCalledWith(expect.objectContaining({deck:"all",scope:"lookup",limit:30}),expect.any(AbortSignal));
 expect(screen.getByRole("link",{name:/Tải từ điển đầy đủ/}).getAttribute("href")).toBe("/toeic/dictionary/dictionary.json.gz");
});

it("separates recall from lookup and does not expose the English answer in Vietnamese-to-English mode",async()=>{
 render(<OpenLexicon preview onReviewed={vi.fn()}/>);
 await screen.findByRole("heading",{name:"invoice"});
 fireEvent.click(screen.getByRole("button",{name:"Ôn thẻ"}));
 expect(screen.queryByText("Vui lòng thanh toán hóa đơn.")).toBeNull();
 fireEvent.click(screen.getByRole("button",{name:"Việt → Anh"}));
 const card=screen.getByRole("article",{name:"Thẻ từ đang chọn"});
 expect(within(card).queryByText("invoice")).toBeNull();
 expect(within(card).queryByText("/ˈɪnvɔɪs/")).toBeNull();
 expect(screen.queryByRole("button",{name:"Nghe phát âm invoice"})).toBeNull();
 fireEvent.click(screen.getByRole("button",{name:"Hiện đáp án & ví dụ"}));
 expect(within(card).getByRole("heading",{name:"invoice"})).toBeTruthy();
 expect(screen.getByRole("button",{name:"Nhớ được"}).hasAttribute("disabled")).toBe(true);
});

it("ignores stale searches and keeps the first matching word even when it is already scheduled",async()=>{
 let resolveOld!:(value:LexiconPage)=>void;
 const hello={...word,id:"lex-hello",term:"hello",due:new Date(Date.now()+86400000).toISOString()};
 api.lexicon.mockImplementation((filters:LexiconFilters)=>filters.q?Promise.resolve(page([hello,word])):new Promise<LexiconPage>(resolve=>{resolveOld=resolve;}));
 render(<OpenLexicon preview onReviewed={vi.fn()}/>);
 fireEvent.change(search(),{target:{value:"hello"}});
 await screen.findByRole("heading",{name:"hello"});
 expect(api.lexicon.mock.calls[0][1].aborted).toBe(true);
 await act(async()=>resolveOld(page()));
 expect(screen.queryByRole("heading",{name:"invoice"})).toBeNull();
});

it("offers an explicit spelling correction without silently changing the submitted query",async()=>{
 api.lexicon.mockImplementation((f:LexiconFilters)=>Promise.resolve(f.q==="accomodation"?{...page([],0),suggestions:["accommodation"]}:page([{...word,term:"accommodation"}])));
 render(<OpenLexicon preview initialQuery="accomodation" onReviewed={vi.fn()}/>);
 fireEvent.click(await screen.findByRole("button",{name:"accommodation"}));
 await screen.findByRole("heading",{name:"accommodation"});
 expect((search() as HTMLInputElement).value).toBe("accommodation");
 expect(api.review).not.toHaveBeenCalled();
});

it("makes hidden results discoverable and clears filters without losing the query",async()=>{
 api.lexicon.mockImplementation((f:LexiconFilters)=>Promise.resolve(f.deck==="ngsl"?{...page([],0),global_total:3}:page()));
 render(<OpenLexicon preview initialQuery="invoice" onReviewed={vi.fn()}/>);
 await screen.findByRole("heading",{name:"invoice"});
 fireEvent.change(screen.getByLabelText("Bộ từ"),{target:{value:"ngsl"}});
 await screen.findByText("Từ này có trong kho nhưng đang bị bộ lọc ẩn đi.");
 fireEvent.click(screen.getByRole("button",{name:"Tìm trong toàn bộ từ điển"}));
 await screen.findByRole("heading",{name:"invoice"});
 expect(api.lexicon).toHaveBeenLastCalledWith(expect.objectContaining({deck:"all",q:"invoice"}),expect.any(AbortSignal));
 expect((search() as HTMLInputElement).value).toBe("invoice");
});

it("clears alphabet restrictions when typing and paginates on the server",async()=>{
 api.lexicon.mockResolvedValue(page([word],61));
 render(<OpenLexicon preview onReviewed={vi.fn()}/>);
 await screen.findByRole("heading",{name:"invoice"});
 fireEvent.click(screen.getByRole("button",{name:"Sau"}));
 await waitFor(()=>expect(api.lexicon).toHaveBeenLastCalledWith(expect.objectContaining({offset:30}),expect.any(AbortSignal)));
 await screen.findByRole("heading",{name:"invoice"});
 fireEvent.click(screen.getByRole("button",{name:"Z"}));
 await waitFor(()=>expect(api.lexicon).toHaveBeenLastCalledWith(expect.objectContaining({letter:"z"}),expect.any(AbortSignal)));
 fireEvent.change(search(),{target:{value:"invoice"}});
 await waitFor(()=>expect(api.lexicon).toHaveBeenLastCalledWith(expect.objectContaining({q:"invoice",offset:0}),expect.any(AbortSignal)));
 expect(api.lexicon.mock.lastCall?.[0].letter).toBeUndefined();
});

it("saves a review once and respects its future due date",async()=>{
 const onReviewed=vi.fn(),due=new Date(Date.now()+86400000).toISOString();
 api.review.mockResolvedValue({version:1,due});
 api.lexicon.mockResolvedValueOnce(page()).mockResolvedValue(page([{...word,version:1,due,reviews:1}]));
 render(<OpenLexicon preview={false} onReviewed={onReviewed}/>);
 await openCard();fireEvent.click(screen.getByRole("button",{name:"Nhớ được"}));
 await waitFor(()=>expect(onReviewed).toHaveBeenCalledTimes(1));
 expect(api.review).toHaveBeenCalledWith(word.id,3,0,expect.any(String));
 fireEvent.click(await screen.findByRole("button",{name:"Hiện đáp án & ví dụ"}));
 expect(await screen.findByText(/Lần ôn tiếp:/)).toBeTruthy();
 expect(screen.queryByRole("button",{name:"Nhớ được"})).toBeNull();
});

it("retries a review failure using the same event ID",async()=>{
 api.review.mockRejectedValueOnce(new Error("Mất mạng thử nghiệm")).mockResolvedValue({version:1,due:new Date(Date.now()+86400000).toISOString()});
 render(<OpenLexicon preview={false} onReviewed={vi.fn()}/>);
 await openCard();fireEvent.click(screen.getByRole("button",{name:"Nhớ được"}));
 await screen.findByRole("alert");const id=api.review.mock.calls[0][3];
 fireEvent.click(screen.getByRole("button",{name:"Nhớ được"}));
 await waitFor(()=>expect(api.review).toHaveBeenCalledTimes(2));
 expect(api.review.mock.calls[1][3]).toBe(id);
});

it("recovers load failures and is explicit when a pronunciation is unavailable",async()=>{
 api.lexicon.mockRejectedValueOnce(new Error("Kho từ chưa tải được")).mockResolvedValue(page([{...word,ipa:"",translation_status:"machine"}]));
 render(<OpenLexicon preview onReviewed={vi.fn()}/>);
 await screen.findByRole("alert");fireEvent.click(screen.getByRole("button",{name:"Thử lại"}));
 await screen.findByRole("heading",{name:"invoice"});
 expect(screen.getByText("Chưa có phiên âm được xác minh")).toBeTruthy();
 expect(screen.getByText(/Nghĩa tham khảo từ bản dịch máy/)).toBeTruthy();
});

it("times out a stuck lookup and ignores a late response after retry",async()=>{
 vi.useFakeTimers();
 let resolveOld!:(value:LexiconPage)=>void;
 api.lexicon.mockImplementationOnce(()=>new Promise<LexiconPage>(resolve=>{resolveOld=resolve;}));
 render(<OpenLexicon preview onReviewed={vi.fn()}/>);
 await act(async()=>vi.advanceTimersByTime(45001));
 expect(screen.getByRole("alert").textContent).toContain("Tra cứu mất quá nhiều thời gian");
 expect(api.lexicon.mock.calls[0][1].aborted).toBe(true);
 await act(async()=>fireEvent.click(screen.getByRole("button",{name:"Thử lại"})));
 expect(screen.getByRole("heading",{name:"invoice"})).toBeTruthy();
 await act(async()=>resolveOld(page([{...word,term:"stale"}])));
 expect(screen.queryByRole("heading",{name:"stale"})).toBeNull();
});

it("returns to a valid page when the final new card has been reviewed",async()=>{
 let rated=false;
 api.lexicon.mockImplementation((f:LexiconFilters)=>Promise.resolve(page(f.offset===30 && rated?[]:[word],rated?30:31)));
 api.review.mockImplementation(()=>{rated=true;return Promise.resolve({version:1,due:new Date(Date.now()+86400000).toISOString()});});
 render(<OpenLexicon preview={false} onReviewed={vi.fn()}/>);
 await screen.findByRole("heading",{name:"invoice"});
 fireEvent.change(screen.getByLabelText("Trạng thái ôn"),{target:{value:"new"}});
 await screen.findByRole("heading",{name:"invoice"});fireEvent.click(screen.getByRole("button",{name:"Sau"}));
 await openCard();fireEvent.click(screen.getByRole("button",{name:"Nhớ được"}));
 await waitFor(()=>expect(api.lexicon).toHaveBeenLastCalledWith(expect.objectContaining({offset:0,state:"new"}),expect.any(AbortSignal)));
});
