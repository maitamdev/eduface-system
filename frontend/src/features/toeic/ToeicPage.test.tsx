// @vitest-environment jsdom
import {afterEach,beforeEach,expect,it,vi} from "vitest";
import {cleanup,fireEvent,render,screen,waitFor,within} from "@testing-library/react";
import {ToeicPage} from "./ToeicPage";
import catalog from "./previewCatalog.json";
const api=vi.hoisted(()=>({catalog:vi.fn(),progress:vi.fn(),lesson:vi.fn(),vocabulary:vi.fn(),review:vi.fn(),start:vi.fn(),completeSession:vi.fn()}));
vi.mock("./api",async importOriginal=>({...await importOriginal<typeof import("./api")>(),toeicApi:api}));
beforeEach(()=>{
 vi.clearAllMocks(); window.scrollTo=vi.fn();
 api.catalog.mockResolvedValue(catalog);
 api.progress.mockResolvedValue({target:650,daily_minutes:30,lessons:{},recent:[],active:[],days:[],streak:0,cards_learned:0,cards_due:0});
 api.vocabulary.mockResolvedValue([{id:"f01-v01",lesson_id:"f01",term:"appointment",meaning:"cuộc hẹn",example:"My appointment is tomorrow.",version:0,due:null,reviews:0}]);
});
afterEach(cleanup);
it("loads real course metadata and keeps preview practice read-only",async()=>{
 render(<ToeicPage preview/>);
 expect(await screen.findByText("Học theo buổi, biết rõ việc cần làm.")).toBeTruthy();
 fireEvent.click(screen.getByRole("button",{name:"Luyện tập"}));
 expect(screen.getByRole("button",{name:/Bắt đầu 200 câu/}).hasAttribute("disabled")).toBe(true);
 expect(screen.getAllByText(/Giọng tổng hợp|Audio tổng hợp/).length).toBeGreaterThan(0);
 expect(api.start).not.toHaveBeenCalled();
});
it("requires revealing a flashcard before rating and persists the FSRS review",async()=>{
 api.review.mockResolvedValue({version:1,due:new Date(Date.now()+600000).toISOString()});
 render(<ToeicPage/>); await screen.findByText("Học theo buổi, biết rõ việc cần làm.");
 fireEvent.click(screen.getByRole("button",{name:"Từ vựng"}));
 await screen.findByRole("button",{name:"Hiện nghĩa & ví dụ"});
 expect(screen.queryByRole("button",{name:"Nhớ được"})).toBeNull();
 fireEvent.click(screen.getByRole("button",{name:"Hiện nghĩa & ví dụ"}));
 expect(screen.getByText("cuộc hẹn")).toBeTruthy();
 fireEvent.click(screen.getByRole("button",{name:"Nhớ được"}));
 await waitFor(()=>expect(api.review).toHaveBeenCalledWith("f01-v01",3,0,expect.any(String)));
 expect(await screen.findByText("Đã ôn xong các thẻ đang đến hạn.")).toBeTruthy();
});

it("preserves the requested 24 and 12 sessions and exposes advanced levels and schedule",async()=>{
 render(<ToeicPage preview/>);
 await screen.findByText("Học theo buổi, biết rõ việc cần làm.");
 expect(within(screen.getByRole("complementary",{name:"Các buổi Level 1"})).getAllByRole("button")).toHaveLength(24);
 expect(screen.getByText("19 tuần")).toBeTruthy();
 fireEvent.change(screen.getByLabelText("Nhịp học"),{target:{value:"2"}});
 expect(screen.getByText("28 tuần")).toBeTruthy();
 fireEvent.change(screen.getByLabelText("Nhịp học"),{target:{value:"4"}});
 expect(screen.getByText("14 tuần")).toBeTruthy();
 for(const [level,count] of [[2,12],[3,12],[4,8]]){
   fireEvent.click(screen.getByRole("button",{name:new RegExp(`Level ${level} · ${count} BUỔI`)}));
   expect(within(screen.getByRole("complementary",{name:`Các buổi Level ${level}`})).getAllByRole("button")).toHaveLength(count);
 }
 expect(screen.getByRole("button",{name:"Đánh dấu đã học buổi này"}).hasAttribute("disabled")).toBe(true);
 expect(screen.getByRole("link",{name:/Tải lộ trình/}).getAttribute("href")).toBe("/toeic/lo-trinh-dhv.md");
});

it("checks answers only after answering and resets the self-check on session changes",async()=>{
 render(<ToeicPage preview/>);
 await screen.findByText("Học theo buổi, biết rõ việc cần làm.");
 expect(screen.getByRole("button",{name:"Kiểm tra câu trả lời"}).hasAttribute("disabled")).toBe(true);
 fireEvent.click(screen.getByRole("radio",{name:"A. equipment"}));
 fireEvent.click(screen.getByRole("radio",{name:"A. applicants"}));
 fireEvent.click(screen.getByRole("button",{name:"Kiểm tra câu trả lời"}));
 expect(screen.getByRole("status").textContent).toContain("1/2 câu");
 expect(screen.getByText(/Equipment là danh từ không đếm được/)).toBeTruthy();
 fireEvent.click(screen.getByRole("button",{name:/^Buổi 2: Đại từ/}));
 expect(screen.queryByRole("status")).toBeNull();
 expect(screen.getAllByRole("radio").every(r=>!(r as HTMLInputElement).checked)).toBe(true);
 expect(api.start).not.toHaveBeenCalled();
 expect(api.completeSession).not.toHaveBeenCalled();
});

it("persists manual session completion and keeps the chosen session open",async()=>{
 api.completeSession.mockResolvedValue({session_id:"l1-s01",completed:true});
 render(<ToeicPage/>);
 await screen.findByText("Học theo buổi, biết rõ việc cần làm.");
 api.progress.mockResolvedValue({target:650,daily_minutes:30,lessons:{},curriculum_completed:["l1-s01"],recent:[],active:[],days:[],streak:0,cards_learned:0,cards_due:0});
 fireEvent.click(screen.getByRole("button",{name:"Đánh dấu đã học buổi này"}));
 await waitFor(()=>expect(api.completeSession).toHaveBeenCalledWith("l1-s01",true));
 expect(await screen.findByRole("button",{name:"Bỏ đánh dấu đã học"})).toBeTruthy();
 expect(screen.getByRole("article",{name:"Nội dung buổi 1"})).toBeTruthy();
 fireEvent.click(screen.getByRole("button",{name:"Bỏ đánh dấu đã học"}));
 await waitFor(()=>expect(api.completeSession).toHaveBeenCalledWith("l1-s01",false));
});

it("does not mark a session complete when saving fails",async()=>{
 api.completeSession.mockRejectedValue(new Error("Chưa lưu được buổi học."));
 render(<ToeicPage/>); await screen.findByText("Học theo buổi, biết rõ việc cần làm.");
 fireEvent.click(screen.getByRole("button",{name:"Đánh dấu đã học buổi này"}));
 await waitFor(()=>expect(screen.getAllByRole("alert").some(a=>a.textContent?.includes("Chưa lưu được"))).toBe(true));
 expect(screen.queryByRole("button",{name:"Bỏ đánh dấu đã học"})).toBeNull();
 expect(screen.getByRole("button",{name:"Đánh dấu đã học buổi này"}).hasAttribute("disabled")).toBe(false);
});

it("returns from a supporting lesson to the same curriculum session",async()=>{
 api.lesson.mockResolvedValue(catalog.lessons.find(l=>l.id==="i03"));
 render(<ToeicPage/>); await screen.findByText("Học theo buổi, biết rõ việc cần làm.");
 fireEvent.click(screen.getByRole("button",{name:/Level 2 · 12 BUỔI/}));
 fireEvent.click(screen.getByRole("button",{name:/^Buổi 5: Part 5 · Rút gọn/}));
 fireEvent.click(screen.getByRole("button",{name:"Bị động, mệnh đề quan hệ và liên từ"}));
 await screen.findByRole("button",{name:"Về lộ trình"});
 fireEvent.click(screen.getByRole("button",{name:"Về lộ trình"}));
 expect(screen.getByRole("article",{name:"Nội dung buổi 5"})).toBeTruthy();
 expect(screen.getByRole("heading",{name:"Part 5 · Rút gọn mệnh đề quan hệ và trạng ngữ"})).toBeTruthy();
});

it("keeps the lesson library usable during a rolling backend deployment",async()=>{
 const {curriculum: _curriculum,...legacy}=catalog;
 api.catalog.mockResolvedValue(legacy);
 render(<ToeicPage/>);
 expect(await screen.findByText("Vững nền tảng, rồi tăng tốc.")).toBeTruthy();
 expect(screen.queryByRole("region",{name:"Lộ trình học theo buổi"})).toBeNull();
});
