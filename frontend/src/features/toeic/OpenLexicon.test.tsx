// @vitest-environment jsdom
import {afterEach,beforeEach,expect,it,vi} from "vitest";
import {act,cleanup,fireEvent,render,screen,waitFor} from "@testing-library/react";
import {OpenLexicon} from "./OpenLexicon";
import type {LexiconCard,LexiconFilters,LexiconPage} from "./api";
const api=vi.hoisted(()=>({lexicon:vi.fn(),review:vi.fn()}));
vi.mock("./api",async original=>({...await original<typeof import("./api")>(),toeicApi:api}));
const word:LexiconCard={id:"lex-test",lesson_id:"open-lexicon",term:"smartphone",meaning:"a mobile phone that runs applications",example:"",version:0,due:null,reviews:0,meaning_language:"en",definitions:[{source_id:"tsl",text:"a mobile phone that runs applications",source_term:"smartphone",adapted_by_dhv:true}],lists:[{id:"tsl",rank:900,supplemental:false}]};
const page=(items:LexiconCard[]=[word],total=items.length):LexiconPage=>({version:"test",items,total,word_count:4060,offset:0,limit:30,due_count:0,new_count:total,license:"CC BY-SA 4.0",license_url:"https://creativecommons.org/licenses/by-sa/4.0/",sources:[],download_url:"/toeic/lexicon.json",attribution_url:"/toeic/licenses/NGSL-TSL.md"});
beforeEach(()=>{api.lexicon.mockReset();api.review.mockReset();api.lexicon.mockResolvedValue(page());});
afterEach(cleanup);

it("labels English definitions, reveals before rating and keeps preview read-only",async()=>{
 render(<OpenLexicon preview onReviewed={vi.fn()}/>);
 await screen.findByRole("heading",{name:"smartphone"});
 expect(screen.queryByText(word.definitions[0].text)).toBeNull();
 expect(screen.queryByRole("button",{name:"Nhớ được"})).toBeNull();
 fireEvent.click(screen.getByRole("button",{name:"Hiện định nghĩa tiếng Anh"}));
 expect(screen.getByRole("heading",{name:"Định nghĩa tiếng Anh"})).toBeTruthy();
 expect(screen.getByText(word.definitions[0].text).getAttribute("lang")).toBe("en");
 expect(screen.getByText(/định nghĩa do DHV bổ sung/)).toBeTruthy();
 expect(screen.getByRole("button",{name:"Nhớ được"}).hasAttribute("disabled")).toBe(true);
 expect(screen.getByRole("link",{name:/Tải dữ liệu từ vựng/}).getAttribute("href")).toBe("/toeic/lexicon.json");
 expect(api.review).not.toHaveBeenCalled();
});

it("persists a review and displays the returned due date instead of allowing an early review",async()=>{
 const onReviewed=vi.fn(),due=new Date(Date.now()+86400000).toISOString();
 api.review.mockResolvedValue({version:1,due});
 api.lexicon.mockResolvedValueOnce(page()).mockResolvedValue(page([{...word,version:1,due,reviews:1}]));
 render(<OpenLexicon preview={false} onReviewed={onReviewed}/>);
 fireEvent.click(await screen.findByRole("button",{name:"Hiện định nghĩa tiếng Anh"}));
 fireEvent.click(screen.getByRole("button",{name:"Nhớ được"}));
 await waitFor(()=>expect(onReviewed).toHaveBeenCalledTimes(1));
 expect(api.review).toHaveBeenCalledWith(word.id,3,0,expect.any(String));
 fireEvent.click(await screen.findByRole("button",{name:"Hiện định nghĩa tiếng Anh"}));
 expect(await screen.findByText(/Lần ôn tiếp:/)).toBeTruthy();
 expect(screen.queryByRole("button",{name:"Nhớ được"})).toBeNull();
});

it("retries a failed review with the same event ID",async()=>{
 api.review.mockRejectedValueOnce(new Error("Mất mạng thử nghiệm")).mockResolvedValue({version:1,due:new Date(Date.now()+86400000).toISOString()});
 render(<OpenLexicon preview={false} onReviewed={vi.fn()}/>);
 fireEvent.click(await screen.findByRole("button",{name:"Hiện định nghĩa tiếng Anh"}));
 fireEvent.click(screen.getByRole("button",{name:"Nhớ được"}));
 await screen.findByRole("alert");
 const id=api.review.mock.calls[0][3];
 fireEvent.click(screen.getByRole("button",{name:"Nhớ được"}));
 await waitFor(()=>expect(api.review).toHaveBeenCalledTimes(2));
 expect(api.review.mock.calls[1][3]).toBe(id);
});

it("ignores stale responses when the debounced search changes",async()=>{
 let resolveOld!:(value:LexiconPage)=>void;
 const cafe={...word,id:"lex-cafe",term:"café"};
 api.lexicon.mockImplementation((filters:LexiconFilters)=>filters.q?Promise.resolve(page([cafe])):new Promise<LexiconPage>(resolve=>{resolveOld=resolve;}));
 render(<OpenLexicon preview onReviewed={vi.fn()}/>);
 fireEvent.change(screen.getByLabelText("Tìm từ hoặc định nghĩa tiếng Anh"),{target:{value:"cafe"}});
 await screen.findByRole("heading",{name:"café"});
 expect(api.lexicon.mock.calls[0][1].aborted).toBe(true);
 await act(async()=>resolveOld(page()));
 expect(screen.queryByRole("heading",{name:"smartphone"})).toBeNull();
 expect(screen.getByRole("heading",{name:"café"})).toBeTruthy();
});

it("paginates on the server and resets the page when the deck or state changes",async()=>{
 api.lexicon.mockResolvedValue(page([word],61));
 render(<OpenLexicon preview onReviewed={vi.fn()}/>);
 await screen.findByRole("heading",{name:"smartphone"});
 fireEvent.click(screen.getByRole("button",{name:"Sau"}));
 await waitFor(()=>expect(api.lexicon).toHaveBeenLastCalledWith(expect.objectContaining({offset:30,limit:30}),expect.any(AbortSignal)));
 await screen.findByRole("heading",{name:"smartphone"});
 fireEvent.change(screen.getByLabelText("Bộ từ"),{target:{value:"tsl"}});
 await waitFor(()=>expect(api.lexicon).toHaveBeenLastCalledWith(expect.objectContaining({offset:0,deck:"tsl"}),expect.any(AbortSignal)));
 api.lexicon.mockResolvedValue(page([],0));
 fireEvent.change(screen.getByLabelText("Trạng thái thẻ"),{target:{value:"due"}});
 await screen.findByText("Chưa có thẻ đến hạn trong bộ lọc.");
 expect(screen.getByRole("button",{name:"Sau"}).hasAttribute("disabled")).toBe(true);
});

it("recovers a failed dictionary load",async()=>{
 api.lexicon.mockRejectedValueOnce(new Error("Kho từ chưa tải được")).mockResolvedValue(page());
 render(<OpenLexicon preview onReviewed={vi.fn()}/>);
 await screen.findByRole("alert");
 fireEvent.click(screen.getByRole("button",{name:"Tải lại kho từ"}));
 await screen.findByRole("heading",{name:"smartphone"});
 expect(api.lexicon).toHaveBeenCalledTimes(2);
});

it("returns to the preceding page when reviewing the final new card removes the last page",async()=>{
 let rated=false;
 api.lexicon.mockImplementation((filters:LexiconFilters)=>Promise.resolve(page(filters.offset===30 && rated?[]:[word],rated?30:31)));
 api.review.mockImplementation(()=>{rated=true;return Promise.resolve({version:1,due:new Date(Date.now()+86400000).toISOString()});});
 render(<OpenLexicon preview={false} onReviewed={vi.fn()}/>);
 await screen.findByRole("heading",{name:"smartphone"});
 fireEvent.change(screen.getByLabelText("Trạng thái thẻ"),{target:{value:"new"}});
 await screen.findByRole("heading",{name:"smartphone"});
 fireEvent.click(screen.getByRole("button",{name:"Sau"}));
 fireEvent.click(await screen.findByRole("button",{name:"Hiện định nghĩa tiếng Anh"}));
 fireEvent.click(screen.getByRole("button",{name:"Nhớ được"}));
 await waitFor(()=>expect(api.lexicon).toHaveBeenLastCalledWith(expect.objectContaining({offset:0,state:"new"}),expect.any(AbortSignal)));
 await screen.findByRole("heading",{name:"smartphone"});
 expect(screen.getByRole("button",{name:"Trước"}).hasAttribute("disabled")).toBe(true);
});
