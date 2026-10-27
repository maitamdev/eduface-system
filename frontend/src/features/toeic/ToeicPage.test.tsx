// @vitest-environment jsdom
import {afterEach,beforeEach,expect,it,vi} from "vitest";
import {cleanup,fireEvent,render,screen,waitFor,within} from "@testing-library/react";
import {ToeicPage} from "./ToeicPage";
import catalog from "./previewCatalog.json";
const api=vi.hoisted(()=>({catalog:vi.fn(),progress:vi.fn(),lesson:vi.fn(),vocabulary:vi.fn(),review:vi.fn(),reviewBook:vi.fn(),start:vi.fn(),completeSession:vi.fn()}));
vi.mock("./api",async importOriginal=>({...await importOriginal<typeof import("./api")>(),toeicApi:api}));
beforeEach(()=>{
 vi.clearAllMocks(); window.scrollTo=vi.fn();
 api.start.mockReset(); api.reviewBook.mockReset();
 api.reviewBook.mockResolvedValue({window:50,count:0,parts:[],items:[]});
 api.catalog.mockResolvedValue(catalog);
 api.progress.mockResolvedValue({target:650,daily_minutes:30,lessons:{},recent:[],active:[],days:[],streak:0,cards_learned:0,cards_due:0});
 api.vocabulary.mockResolvedValue([{id:"f01-v01",lesson_id:"f01",term:"appointment",meaning:"cuộc hẹn",example:"My appointment is tomorrow.",version:0,due:null,reviews:0}]);
});
afterEach(cleanup);
it("loads real course metadata and keeps preview practice read-only",async()=>{
 render(<ToeicPage preview/>);
 expect(await screen.findByText("Học theo buổi, biết rõ việc cần làm.")).toBeTruthy();
 fireEvent.click(screen.getByRole("button",{name:"Luyện tập"}));
 expect(screen.getByRole("button",{name:/Luyện dạng này/}).hasAttribute("disabled")).toBe(true);
 fireEvent.click(screen.getByRole("button",{name:"Đề thi thử"}));
 expect(screen.getByRole("button",{name:/Ghép một đề ngẫu nhiên/}).hasAttribute("disabled")).toBe(true);
 expect(screen.getAllByText(/audio điều khiển thủ công/i).length).toBeGreaterThan(0);
 expect(api.start).not.toHaveBeenCalled();
});

it("finds accented grammar topics, shows the full guide and retries the same request",async()=>{
 api.start.mockRejectedValue(new Error("Mất kết nối thử nghiệm"));
 render(<ToeicPage/>); await screen.findByText("Học theo buổi, biết rõ việc cần làm.");
 fireEvent.click(screen.getByRole("button",{name:"Luyện tập"}));
 fireEvent.change(screen.getByLabelText("Dạng bài theo Part"),{target:{value:"5"}});
 fireEvent.change(screen.getByLabelText("Tìm chuyên đề"),{target:{value:"bi dong"}});
 expect(screen.getByRole("heading",{name:"Hiểu bản chất"})).toBeTruthy();
 expect(screen.getByRole("heading",{name:"Ví dụ có phân tích"})).toBeTruthy();
 fireEvent.click(screen.getByRole("button",{name:/Luyện dạng này/}));
 await screen.findByRole("alert");
 const requestId=api.start.mock.calls[0][1];
 expect(api.start).toHaveBeenLastCalledWith("topic",requestId,undefined,undefined,{topic_id:"p5-passive"});
 fireEvent.click(screen.getByRole("button",{name:/Luyện dạng này/}));
 await waitFor(()=>expect(api.start).toHaveBeenCalledTimes(2));
 expect(api.start.mock.calls[1][1]).toBe(requestId);
 expect(screen.getByRole("link",{name:"Tải sổ tay"}).getAttribute("href")).toBe("/toeic/so-tay-dang-bai.md");
});

it("filters fixed exam types and starts the chosen code",async()=>{
 api.start.mockResolvedValue(undefined);
 render(<ToeicPage/>); await screen.findByText("Học theo buổi, biết rõ việc cần làm.");
 fireEvent.click(screen.getByRole("button",{name:"Luyện tập"}));
 fireEvent.click(screen.getByRole("button",{name:"Đề thi thử"}));
 expect(screen.getAllByRole("article")).toHaveLength(8);
 fireEvent.change(screen.getByLabelText("Loại đề"),{target:{value:"listening"}});
 expect(screen.getAllByRole("article")).toHaveLength(1);
 expect(screen.getByText("45 phút")).toBeTruthy();
 fireEvent.click(screen.getByRole("button",{name:"Làm bài thi"}));
 await waitFor(()=>expect(api.start).toHaveBeenCalledWith("exam",expect.any(String),undefined,undefined,{exam_id:"dhv-listening-01-v1"}));
});

it("loads a private mistake book, filters parts and starts review",async()=>{
 api.reviewBook.mockResolvedValue({window:50,count:2,parts:[{part:3,count:1},{part:5,count:1}],items:[{id:"q3",part:3,prompt:"What will the man do?",topic_ids:[]},{id:"q5",part:5,prompt:"The request was _____.",topic_ids:[]}]});
 render(<ToeicPage/>); await screen.findByText("Học theo buổi, biết rõ việc cần làm.");
 fireEvent.click(screen.getByRole("button",{name:"Luyện tập"}));
 fireEvent.click(screen.getByRole("button",{name:"Ôn câu sai"}));
 await screen.findByText("2 câu cần ôn lại");
 fireEvent.change(screen.getByLabelText("Lọc câu sai theo Part"),{target:{value:"5"}});
 expect(screen.queryByText("What will the man do?")).toBeNull();
 expect(screen.getByText("The request was _____.")).toBeTruthy();
 fireEvent.click(screen.getByRole("button",{name:/Ôn lại · tối đa 30 câu/}));
 await waitFor(()=>expect(api.start).toHaveBeenCalledWith("review",expect.any(String),undefined,5,undefined));
});

it("recovers a failed mistake-book load and handles an empty history",async()=>{
 api.reviewBook.mockRejectedValueOnce(new Error("Không tải được lịch sử"));
 render(<ToeicPage/>); await screen.findByText("Học theo buổi, biết rõ việc cần làm.");
 fireEvent.click(screen.getByRole("button",{name:"Luyện tập"}));
 fireEvent.click(screen.getByRole("button",{name:"Ôn câu sai"}));
 await screen.findByRole("alert");
 fireEvent.click(screen.getByRole("button",{name:"Tải lại sổ câu sai"}));
 await screen.findByText("0 câu cần ôn lại");
 expect(screen.getByRole("button",{name:/Ôn lại · tối đa 30 câu/}).hasAttribute("disabled")).toBe(true);
 expect(api.reviewBook).toHaveBeenCalledTimes(2);
});

it("does not fetch personal mistake history in preview",async()=>{
 render(<ToeicPage preview/>); await screen.findByText("Học theo buổi, biết rõ việc cần làm.");
 fireEvent.click(screen.getByRole("button",{name:"Luyện tập"}));
 fireEvent.click(screen.getByRole("button",{name:"Ôn câu sai"}));
 expect(screen.getByText("Sổ câu sai theo tài khoản")).toBeTruthy();
 expect(api.reviewBook).not.toHaveBeenCalled();
});

it("offers a usable empty-search recovery and all seven part drills",async()=>{
 render(<ToeicPage preview/>); await screen.findByText("Học theo buổi, biết rõ việc cần làm.");
 fireEvent.click(screen.getByRole("button",{name:"Luyện tập"}));
 fireEvent.change(screen.getByLabelText("Tìm chuyên đề"),{target:{value:"no-match-xyz"}});
 expect(screen.getByText("Chưa tìm thấy dạng bài phù hợp")).toBeTruthy();
 fireEvent.click(screen.getByRole("button",{name:"Xóa bộ lọc"}));
 expect(screen.getByText("38 chuyên đề khớp bộ lọc")).toBeTruthy();
 fireEvent.click(screen.getByRole("button",{name:"Luyện từng Part"}));
 expect(screen.getAllByRole("button",{name:/Luyện phần này/})).toHaveLength(7);
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
