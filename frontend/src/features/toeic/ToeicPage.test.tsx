// @vitest-environment jsdom
import {afterEach,beforeEach,expect,it,vi} from "vitest";
import {cleanup,fireEvent,render,screen,waitFor} from "@testing-library/react";
import {ToeicPage} from "./ToeicPage";
import catalog from "./previewCatalog.json";
const api=vi.hoisted(()=>({catalog:vi.fn(),progress:vi.fn(),lesson:vi.fn(),vocabulary:vi.fn(),review:vi.fn(),start:vi.fn()}));
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
 expect(await screen.findByText("Vững nền tảng, rồi tăng tốc.")).toBeTruthy();
 fireEvent.click(screen.getByRole("button",{name:"Luyện tập"}));
 expect(screen.getByRole("button",{name:/Bắt đầu 200 câu/}).hasAttribute("disabled")).toBe(true);
 expect(screen.getAllByText(/Giọng tổng hợp|Audio tổng hợp/).length).toBeGreaterThan(0);
 expect(api.start).not.toHaveBeenCalled();
});
it("requires revealing a flashcard before rating and persists the FSRS review",async()=>{
 api.review.mockResolvedValue({version:1,due:new Date(Date.now()+600000).toISOString()});
 render(<ToeicPage/>); await screen.findByText("Vững nền tảng, rồi tăng tốc.");
 fireEvent.click(screen.getByRole("button",{name:"Từ vựng"}));
 await screen.findByRole("button",{name:"Hiện nghĩa & ví dụ"});
 expect(screen.queryByRole("button",{name:"Nhớ được"})).toBeNull();
 fireEvent.click(screen.getByRole("button",{name:"Hiện nghĩa & ví dụ"}));
 expect(screen.getByText("cuộc hẹn")).toBeTruthy();
 fireEvent.click(screen.getByRole("button",{name:"Nhớ được"}));
 await waitFor(()=>expect(api.review).toHaveBeenCalledWith("f01-v01",3,0,expect.any(String)));
 expect(await screen.findByText("Đã ôn xong các thẻ đang đến hạn.")).toBeTruthy();
});
