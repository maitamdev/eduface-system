// @vitest-environment jsdom
import { beforeEach, afterEach, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AttemptRunner } from "./AttemptRunner";
import type { Attempt } from "./api";
const api = vi.hoisted(() => ({save: vi.fn(), submit: vi.fn(), attempt: vi.fn()}));
vi.mock("./api", async importOriginal => ({...await importOriginal<typeof import("./api")>(), toeicApi: api}));
const makeAttempt = (): Attempt => ({id:"test",kind:"lesson",status:"active",started_at:new Date().toISOString(),server_now:new Date().toISOString(),deadline:new Date(Date.now()+600000).toISOString(),revision:0,answers:{},questions:[{id:"q1",lesson_id:"f01",part:2,prompt:"Listen and choose.",options:["One","Two","Three"],audio_id:"f01-q01"},{id:"q2",lesson_id:"f02",part:5,prompt:"Choose a verb.",options:["run","runner","running","runs"]}]});
beforeEach(()=>{vi.clearAllMocks();api.save.mockResolvedValue({revision:1});});
afterEach(cleanup);

it("hides listening response text and reveals explanations only after grading", async()=>{
 const attempt=makeAttempt();
 api.submit.mockResolvedValue({...attempt,status:"submitted",answers:{q1:1},result:{correct:1,total:2,percent:50,parts:[],suggested_stage:2,score_notice:"Kết quả luyện tập nội bộ"},questions:attempt.questions.map((q,i)=>({...q,correct:i?0:1,explanation:"Giải thích tiếng Việt",transcript:i?undefined:"What time? Two."}))});
 render(<AttemptRunner initial={attempt} onExit={vi.fn()} onComplete={vi.fn()}/>);
 expect(screen.queryByText("Two")).toBeNull();
 fireEvent.click(screen.getByRole("radio",{name:/Lựa chọn B/}));
 fireEvent.click(screen.getByRole("button",{name:"Nộp bài"}));
 fireEvent.click(screen.getByRole("button",{name:"Xác nhận nộp"}));
 expect(await screen.findByText("Giải thích tiếng Việt")).toBeTruthy();
 expect(screen.getByText("Two")).toBeTruthy();
 expect(api.submit).toHaveBeenCalledWith("test",{q1:1},0);
});

it("serializes autosave and submits the newest answer with the new revision",async()=>{
 let release!: (x:{revision:number})=>void;
 api.save.mockImplementationOnce(()=>new Promise(resolve=>{release=resolve;}));
 const attempt=makeAttempt(); api.submit.mockResolvedValue({...attempt,status:"submitted"});
 render(<AttemptRunner initial={attempt} onExit={vi.fn()} onComplete={vi.fn()}/>);
 fireEvent.click(screen.getByRole("radio",{name:/Lựa chọn A/}));
 await waitFor(()=>expect(api.save).toHaveBeenCalledTimes(1));
 fireEvent.click(screen.getByRole("radio",{name:/Lựa chọn B/}));
 fireEvent.click(screen.getByRole("button",{name:"Nộp bài"}));
 fireEvent.click(screen.getByRole("button",{name:"Xác nhận nộp"}));
 expect(api.submit).not.toHaveBeenCalled();
 release({revision:1});
 await waitFor(()=>expect(api.submit).toHaveBeenCalledWith("test",{q1:1},1));
 expect(api.save).toHaveBeenCalledTimes(1);
});

it("keeps unsaved answers visible and prevents exit when saving fails",async()=>{
 api.save.mockRejectedValue(new Error("Mạng bị ngắt")); const exit=vi.fn();
 render(<AttemptRunner initial={makeAttempt()} onExit={exit} onComplete={vi.fn()}/>);
 fireEvent.click(screen.getByRole("radio",{name:/Lựa chọn C/}));
 fireEvent.click(screen.getByRole("button",{name:"Lưu & về góc học tập"}));
 expect(await screen.findByText("Mạng bị ngắt")).toBeTruthy();
 expect(exit).not.toHaveBeenCalled();
 expect((screen.getByRole("radio",{name:/Lựa chọn C/}) as HTMLInputElement).checked).toBe(true);
});

it("automatically submits an expired attempt only once",async()=>{
 const attempt=makeAttempt(); attempt.deadline=new Date(Date.now()-10000).toISOString();
 api.submit.mockRejectedValue(new Error("Thử lại sau"));
 render(<AttemptRunner initial={attempt} onExit={vi.fn()} onComplete={vi.fn()}/>);
 await waitFor(()=>expect(api.submit).toHaveBeenCalledTimes(1));
 expect(await screen.findByRole("button",{name:"Nộp lại bài đã lưu"})).toBeTruthy();
 expect((screen.getByRole("radio",{name:/Lựa chọn A/}) as HTMLInputElement).disabled || screen.getByRole("group").hasAttribute("disabled")).toBe(true);
});
