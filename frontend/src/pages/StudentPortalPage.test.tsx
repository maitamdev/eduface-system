// @vitest-environment jsdom
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { StudentPortalPage } from "./StudentPortalPage";

const mocks = vi.hoisted(() => ({
  user: { id: "student-a", username: "student-a", display_name: "Test Student", google_email: "", role: "student" },
  profile: vi.fn(), refresh: vi.fn(), enroll: vi.fn(), analyze: vi.fn(),
  stop: vi.fn(), start: vi.fn(), flip: vi.fn(),
}));
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ user: mocks.user, role: "student", refreshProfile: mocks.refresh }) }));
vi.mock("@/context/LanguageContext", () => ({ useLanguage: () => ({ t: (vi: string) => vi, lang: "vi" }) }));
vi.mock("@/context/ToastContext", () => ({ useToast: () => ({ success: vi.fn(), error: vi.fn() }) }));
vi.mock("@/hooks/useCamera", () => ({
  useCamera: () => ({ videoRef: { current: null }, streaming: false, starting: false, facing: "user", error: null, stop: mocks.stop, start: mocks.start, flip: mocks.flip }),
  captureVideoFrame: vi.fn(),
}));
vi.mock("@/api/client", () => ({
  authApi: { getStudentPortal: mocks.profile },
  personsApi: { list: vi.fn().mockResolvedValue([]), selfEnroll: mocks.enroll, analyzePhotos: mocks.analyze },
  academicApi: {
    getMyGrade: vi.fn().mockResolvedValue(null),
    getTranscript: vi.fn().mockResolvedValue({ courses: [], credits_graded: 0, weighted_gpa: null }),
    listLeaves: vi.fn().mockResolvedValue([]), listAnnouncements: vi.fn().mockResolvedValue([]), listCourses: vi.fn().mockResolvedValue([]),
  },
}));

const emptyPortal = { person: null, total_sessions: 0, present_count: 0, absent_count: 0, attendance_rate: 0, is_defaulter: false, sessions: [] };
function openPortal() {
  return render(<MemoryRouter initialEntries={["/student"]}><Routes>
    <Route path="/student" element={<StudentPortalPage />} />
    <Route path="/toeic" element={<h1>TOEIC learning</h1>} />
  </Routes></MemoryRouter>);
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  mocks.user.id = "student-a";
  mocks.profile.mockResolvedValue(emptyPortal);
  vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:test-photo");
  vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => {});
});
afterEach(() => { cleanup(); vi.restoreAllMocks(); });

it("lets a new student defer without submitting a profile or consent and enter TOEIC", async () => {
  openPortal();
  fireEvent.click(await screen.findByRole("button", { name: "Để sau" }));
  expect(screen.queryByRole("button", { name: "Hoàn tất đăng ký hồ sơ & khuôn mặt" })).toBeNull();
  expect(screen.queryByText("Đã có hồ sơ sinh viên")).toBeNull();
  expect(screen.getByRole("button", { name: "Hoàn tất thiết lập" })).toBeTruthy();
  expect(mocks.stop).toHaveBeenCalled();
  expect(mocks.start).not.toHaveBeenCalled();
  expect(mocks.enroll).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("link", { name: "Học TOEIC ngay" }));
  expect(await screen.findByRole("heading", { name: "TOEIC learning" })).toBeTruthy();
});

it("remembers defer for the same account, allows resuming, and keeps another account independent", async () => {
  const first = openPortal();
  fireEvent.click(await screen.findByRole("button", { name: "Để sau" }));
  first.unmount();
  const again = openPortal();
  fireEvent.click(await screen.findByRole("button", { name: "Hoàn tất thiết lập" }));
  expect(await screen.findByRole("button", { name: "Để sau" })).toBeTruthy();
  expect((screen.getByRole("checkbox") as HTMLInputElement).checked).toBe(false);
  expect(screen.getByRole("button", { name: "Hoàn tất đăng ký hồ sơ & khuôn mặt" }).hasAttribute("disabled")).toBe(true);
  again.unmount();
  mocks.user.id = "student-b";
  openPortal();
  expect(await screen.findByRole("button", { name: "Để sau" })).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Hoàn tất thiết lập" })).toBeNull();
});

it("stops the camera and releases unsaved photos when deferring", async () => {
  openPortal();
  await screen.findByRole("button", { name: "Để sau" });
  fireEvent.click(screen.getByRole("button", { name: "Tải ảnh từ máy" }));
  fireEvent.change(screen.getByLabelText("Chọn từ 1 đến 5 ảnh rõ khuôn mặt"), { target: { files: [new File(["synthetic"], "test.jpg", { type: "image/jpeg" })] } });
  fireEvent.click(screen.getByRole("checkbox"));
  expect(screen.getByAltText("Ảnh khuôn mặt 1")).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "Để sau" }));
  expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:test-photo");
  fireEvent.click(screen.getByRole("button", { name: "Hoàn tất thiết lập" }));
  expect(screen.queryByAltText("Ảnh khuôn mặt 1")).toBeNull();
  expect((screen.getByRole("checkbox") as HTMLInputElement).checked).toBe(false);
  expect(mocks.enroll).not.toHaveBeenCalled();
});

it("still permits deferral when browser storage is unavailable", async () => {
  vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => { throw new Error("Storage blocked"); });
  vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => { throw new Error("Storage blocked"); });
  openPortal();
  fireEvent.click(await screen.findByRole("button", { name: "Để sau" }));
  expect(screen.getByRole("button", { name: "Hoàn tất thiết lập" })).toBeTruthy();
});

it("keeps an enrolled student's academic profile and recapture flow available", async () => {
  mocks.profile.mockResolvedValue({ ...emptyPortal, person: { id: "person-a", name: "Enrolled Student", student_id: "TEST01", department: "CS", email: null } });
  openPortal();
  expect(await screen.findByText("Đã có hồ sơ sinh viên")).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Để sau" })).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "Đăng ký / Chụp lại khuôn mặt" }));
  expect(screen.getByRole("button", { name: "Đóng" })).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Để sau" })).toBeNull();
});
