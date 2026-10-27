import type { AnnouncementOut, AttendanceOut, CourseOut, LeaveRequestOut, PersonOut, SessionOut, StudentGradeRow, UserOut } from "@/api/client";
import type { DashboardSnapshot } from "@/pages/DashboardPage";

const date = new Date();
const at = (hour: number, minute: number) => { const value = new Date(date); value.setHours(hour, minute, 0, 0); return value.toISOString(); };
const names = ["Nguyễn Minh Anh", "Trần Hoàng Nam", "Lê Phương Linh", "Phạm Đức Huy"];
const departments = ["CNTT · K24", "CNTT · K24", "Thiết kế · K23", "CNTT · K24"];
const initialSessions: SessionOut[] = [
  { id: "sample-1", label: "Lập trình ứng dụng Web", department: departments[0], started_at: at(8, 0), ended_at: null, is_active: true },
  { id: "sample-2", label: "Thiết kế giao diện người dùng", department: departments[2], started_at: at(8, 30), ended_at: null, is_active: true },
  { id: "sample-3", label: "Cơ sở dữ liệu · Buổi 4", department: departments[0], started_at: at(7, 0), ended_at: at(7, 50), is_active: false },
];
let sessions: SessionOut[] = [];
let people: PersonOut[] = [];
let records: AttendanceOut[] = [];
let users: UserOut[] = [];
let empty = false;
export function resetPreviewData(isEmpty = false) {
  empty = isEmpty;
  sessions = isEmpty ? [] : structuredClone(initialSessions);
  people = isEmpty ? [] : names.map((name, index) => ({ id: `person-${index + 1}`, name, department: departments[index], email: `student${index + 1}@example.edu`, photo_url: null, enrolled_at: at(7, 0), is_active: true }));
  records = isEmpty ? [] : people.map((person, index) => ({ id: `record-${index + 1}`, person_id: person.id, person_name: person.name, department: person.department, session_id: index === 2 ? "sample-2" : "sample-1", session_label: initialSessions[index === 2 ? 1 : 0].label, marked_at: at(8, 42 - index), confidence: [.99, .98, .99, .97][index], status: "present" }));
  users = isEmpty ? [] : [{ id: "preview-admin", username: "admin_demo", role: "admin", is_active: true, created_at: at(7, 0) }, { id: "preview-operator", username: "giangvien_demo", role: "operator", is_active: true, created_at: at(7, 10) }];
}
resetPreviewData();
const departmentKey = (value?: string | null) => (value || "").trim().toLocaleLowerCase();
const localDay = (value: string) => new Date(new Date(value).getTime() + 7 * 60 * 60 * 1000).toISOString().slice(0, 10);
const attended = (status?: string) => ["present", "late", "excused"].includes(status || "");
const inDepartment = (value: string | null | undefined, selected: string | null) => !selected?.trim() || departmentKey(value) === departmentKey(selected);
function applicableSessions(person: PersonOut, days = 365) {
  const since = new Date(date); since.setDate(since.getDate() - days + 1);
  return sessions.filter((session) => (!departmentKey(session.department) || departmentKey(session.department) === departmentKey(person.department)) && localDay(session.started_at) >= localDay(person.enrolled_at) && localDay(session.started_at) >= localDay(since.toISOString()) && localDay(session.started_at) <= localDay(date.toISOString()));
}
function assessedSessions(person: PersonOut, days = 365) {
  return applicableSessions(person, days).map((session) => ({ session, record: records.find((record) => record.person_id === person.id && record.session_id === session.id) })).filter(({ session, record }) => !session.is_active || !!session.ended_at || attended(record?.status));
}
function personReport(person: PersonOut, days = 365) {
  const assessed = assessedSessions(person, days);
  const present = assessed.filter(({ record }) => attended(record?.status)).length;
  const rate = assessed.length ? Math.round(1000 * present / assessed.length) / 10 : 0;
  return { person_id: person.id, name: person.name, department: person.department, total_sessions: assessed.length, present_count: present, attendance_rate: rate, is_defaulter: assessed.length > 0 && rate < 75 };
}
function demoGrades(department: string | null): StudentGradeRow[] {
  return people.filter((person) => inDepartment(person.department, department)).map((person) => {
    const stats = personReport(person);
    return { ...stats, student_id: person.student_id, attendance_score: stats.attendance_rate / 10, midterm_score: 8, final_score: null, bonus_score: 0, total_10: null, gpa_4: null, letter_grade: null, exam_eligible: stats.total_sessions > 0 && stats.attendance_rate >= 75, note: "Dữ liệu minh họa, chưa có điểm cuối kỳ" };
  });
}
function demoCourses(): CourseOut[] {
  return empty ? [] : [
    { id: "course-web", code: "WEB201", name: "Lập trình ứng dụng Web", department: departments[0], credits: 3, lecturer: "Giảng viên mẫu", schedule: "Thứ 2 · 08:00–10:30", room: "A.302", semester: "HK1 2026–2027", created_at: at(7, 0) },
    { id: "course-design", code: "UX101", name: "Thiết kế giao diện người dùng", department: departments[2], credits: 3, lecturer: "Giảng viên mẫu", schedule: "Thứ 4 · 08:30–11:00", room: "B.204", semester: "HK1 2026–2027", created_at: at(7, 0) },
  ];
}
function demoLeaves(): LeaveRequestOut[] {
  return people.slice(1, 3).map((person, index) => ({ id: `leave-${index}`, person_id: person.id, person_name: person.name, student_id: person.student_id, department: person.department, session_id: index ? "sample-2" : "sample-1", session_label: index ? initialSessions[1].label : initialSessions[0].label, leave_date: localDay(date.toISOString()), reason: "Nghỉ có lý do · dữ liệu minh họa", status: index ? "approved" : "pending", reviewer_note: index ? "Đơn minh họa đã duyệt" : null, created_at: at(7, 10), reviewed_at: index ? at(7, 30) : null }));
}
function demoAnnouncements(): AnnouncementOut[] {
  return empty ? [] : [
    { id: "announcement-all", title: "Lịch học tuần tới", content: "Thông báo minh họa: kiểm tra lịch học và có mặt trước giờ bắt đầu 10 phút.", department: null, priority: "normal", author: "Phòng đào tạo · Mẫu", created_at: at(7, 0) },
    { id: "announcement-cntt", title: "Chuẩn bị bài thực hành Web", content: "Mang theo máy tính và hoàn thành bài thực hành trước buổi học. Đây là dữ liệu mẫu.", department: departments[0], priority: "important", author: "Giảng viên · Mẫu", created_at: at(7, 20) },
  ];
}
function trend(days: number) {
  return empty ? [] : Array.from({ length: days }, (_, index) => {
    const value = new Date(date); value.setDate(date.getDate() - days + 1 + index);
    return { date: `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`, total_present: [890, 1040, 960, 1120, 1070, 1180, 1106][index % 7], total_sessions: 24, attendance_rate: [79, 85, 82, 90, 86, 94, 88.6][index % 7] };
  });
}
export function previewSnapshot(): DashboardSnapshot {
  return { metrics: { total_enrolled: empty ? 0 : 1248, present_today: empty ? 0 : 1106, sessions_today: empty ? 0 : 24, attendance_rate: empty ? 0 : 88.6 }, sessions: sessions.filter((session) => session.is_active), activity: records, trend: trend(14) };
}
export async function previewRequest(path: string, init: RequestInit = {}): Promise<unknown> {
  const url = new URL(path, "http://preview.local");
  const route = url.pathname;
  const method = init.method || "GET";
  const payload = typeof init.body === "string" ? JSON.parse(init.body) : null;
  if (route.startsWith("/api/toeic/")) {
    if (method !== "GET") throw new Error("Bản xem thử TOEIC chỉ đọc. Đăng nhập để lưu tiến độ và làm bài.");
    const data = (await import("@/features/toeic/previewCatalog.json")).default;
    if (route === "/api/toeic/catalog") return data;
    if (route === "/api/toeic/review") return {window:50,count:0,items:[],parts:[]};
    if (route === "/api/toeic/progress") return {target: 650, daily_minutes: 30, lessons: {}, recent: [], active: [], days: [], streak: 0, cards_learned: 0, cards_due: 0};
    if (route === "/api/toeic/vocabulary") return data.vocabulary.map(c => ({...c, version: 0, due: null, reviews: 0}));
    if (route === "/api/toeic/lexicon") return (await import("@/features/toeic/lexiconPreview")).previewLexicon(url.searchParams);
    if (route.startsWith("/api/toeic/lessons/")) { const id = route.split("/").pop(); const lesson = data.lessons.find(x => x.id === id); if (!lesson) throw new Error("Không tìm thấy bài học"); return {...lesson, vocabulary: data.vocabulary.filter(c => c.lesson_id === id)}; }
    throw new Error("Không có lượt làm bài trong bản xem thử.");
  }
  if (route === "/health") return { status: "ok" };
  if (route === "/api/auth/google/config") return { enabled: false, client_id: "" };
  if (route === "/api/auth/microsoft/config") return { enabled: false, client_id: "", tenant_id: "" };
  if (route === "/api/dashboard/metrics") return previewSnapshot().metrics;
  if (route === "/api/dashboard/activity") return structuredClone(records);
  if (route === "/api/sessions" && method === "GET") return structuredClone(sessions.filter((session) => !url.searchParams.has("active") || session.is_active === (url.searchParams.get("active") === "true")));
  if (route === "/api/sessions" && method === "POST") { const result = { id: crypto.randomUUID(), ...payload, department: payload.department || null, started_at: new Date().toISOString(), ended_at: null, is_active: true }; sessions.unshift(result); return structuredClone(result); }
  if (/^\/api\/sessions\/[^/]+\/end$/.test(route) && method === "PATCH") { const session = sessions.find((item) => item.id === route.split("/")[3]); if (!session) throw new Error("Preview session not found"); session.is_active = false; session.ended_at = new Date().toISOString(); return structuredClone(session); }
  if (route === "/api/persons" && method === "GET") return structuredClone(people.filter((person) => inDepartment(person.department, url.searchParams.get("department"))));
  if (/^\/api\/persons\/[^/]+$/.test(route) && method === "DELETE") { people = people.filter((person) => person.id !== route.split("/")[3]); return undefined; }
  if (route === "/api/persons/enroll/analyze") throw new Error("Bản xem thử không phân tích ảnh thật / Preview does not analyze real photos.");
  if (route === "/api/persons/enroll") throw new Error("Bản xem thử không lưu dữ liệu khuôn mặt / Preview does not save facial data.");
  if (route === "/api/attendance") return structuredClone(records.filter((record) => (!url.searchParams.has("session_id") || record.session_id === url.searchParams.get("session_id")) && (!url.searchParams.has("person_id") || record.person_id === url.searchParams.get("person_id")) && (!url.searchParams.has("date") || record.marked_at.slice(0, 10) === url.searchParams.get("date"))));
  const reportPeople = people.filter((person) => inDepartment(person.department, url.searchParams.get("department")));
  const reportDays = Number(url.searchParams.get("days")) || 7;
  if (route === "/api/reports/daily") return trend(reportDays).map((day) => {
    const assessed = reportPeople.flatMap((person) => assessedSessions(person, reportDays)).filter(({ session }) => localDay(session.started_at) === day.date);
    const present = assessed.filter(({ record }) => attended(record?.status)).length;
    return { date: day.date, total_sessions: new Set(assessed.map(({ session }) => session.id)).size, total_present: present, attendance_rate: assessed.length ? Math.round(1000 * present / assessed.length) / 10 : 0 };
  });
  if (route === "/api/reports/persons") return reportPeople.map((person) => personReport(person, reportDays));
  if (route === "/api/reports/heatmap") { const dates = trend(Number(url.searchParams.get("days")) || 14).map((day) => day.date); return { dates, persons: reportPeople.map((person) => ({ person_id: person.id, name: person.name, department: person.department, data: dates.map((day) => { const assessed = assessedSessions(person, reportDays).filter(({ session }) => localDay(session.started_at) === day); return assessed.length ? Number(assessed.every(({ record }) => attended(record?.status))) : null; }) })) }; }
  if (route.startsWith("/api/academic/") && method !== "GET") throw new Error("Bản xem thử học vụ chỉ đọc dữ liệu mẫu / Academic preview is read-only sample data.");
  if (route === "/api/academic/courses") return demoCourses().filter((course) => inDepartment(course.department, url.searchParams.get("department")));
  if (route === "/api/academic/grades") return demoGrades(url.searchParams.get("department"));
  if (route === "/api/academic/my-transcript") return { courses: [], credits_graded: 0, weighted_gpa: null };
  if (route === "/api/academic/my-grade") return demoGrades(null).find((grade) => grade.person_id === (url.searchParams.get("person_id") || people[0]?.id)) || null;
  if (route === "/api/academic/leaves") return demoLeaves().filter((leave) => inDepartment(leave.department, url.searchParams.get("department")) && (!url.searchParams.get("status") || leave.status === url.searchParams.get("status")));
  if (route === "/api/academic/announcements") return demoAnnouncements().filter((announcement) => !announcement.department || inDepartment(announcement.department, url.searchParams.get("department")));
  if (route === "/api/auth/users") return structuredClone(users);
  if (route === "/api/auth/student-portal") {
    const pid = url.searchParams.get("person_id") || people[0]?.id;
    const person = people.find((item) => item.id === pid) || null;
    if (!person) return { person: null, total_sessions: 0, present_count: 0, absent_count: 0, attendance_rate: 0, is_defaulter: false, sessions: [] };
    const studentSessions = applicableSessions(person).map((s) => {
      const rec = records.find((r) => r.person_id === person.id && r.session_id === s.id);
      return {
        session_id: s.id,
        label: s.label,
        department: s.department,
        started_at: s.started_at,
        ended_at: s.ended_at,
        is_active: s.is_active,
        attended: attended(rec?.status),
        marked_at: rec?.marked_at || null,
        confidence: rec?.confidence ?? null,
        status: attended(rec?.status) ? rec!.status : s.is_active ? "open" : "absent",
      };
    });
    const presentCount = studentSessions.filter((s) => s.attended).length;
    const absentCount = studentSessions.filter((s) => s.status === "absent").length;
    const assessedCount = presentCount + absentCount;
    const rate = assessedCount ? Math.round((presentCount / assessedCount) * 1000) / 10 : 0;
    return { person, total_sessions: studentSessions.length, present_count: presentCount, absent_count: absentCount, attendance_rate: rate, is_defaulter: assessedCount > 0 && rate < 75, sessions: studentSessions };
  }
  if (route === "/api/auth/register") { if (users.some((user) => user.username === payload.username)) throw new Error("Tên tài khoản đã tồn tại / Username already exists."); const result = { id: crypto.randomUUID(), username: payload.username, role: payload.role, person_id: payload.person_id || null, is_active: true, created_at: new Date().toISOString() }; users.unshift(result); return structuredClone(result); }
  if (route === "/api/persons/debug-config") return { status: "ok", issues: [], MONGODB_URL: "Sample configuration", MONGODB_DB_NAME: "attendance_demo", MIN_CONFIDENCE: "0.40", DUPLICATE_THRESHOLD: "0.45", AZURE_STORAGE_CONNECTION_STRING: "not set (optional)", API_KEY_ADMIN_configured: false, API_KEY_OPERATOR_configured: false, API_KEY_legacy_configured: false };
  if (route === "/api/persons/debug-encodings") return { total_active_persons: people.length, persons_with_encodings: people.length, persons_missing_encodings: 0, missing: [] };
  throw new Error("Chức năng này cần đăng nhập hệ thống thật / This action requires the real authenticated application.");
}
export function downloadPreviewCsv(filters?: { session_id?: string; date?: string }) {
  const selected = records.filter((record) => (!filters?.session_id || record.session_id === filters.session_id) && (!filters?.date || record.marked_at.slice(0, 10) === filters.date));
  const cell = (value: string) => `"${value.replace(/"/g, '""')}"`;
  const csv = ["Name,Department,Session,Time", ...selected.map((record) => [record.person_name, record.department || "", record.session_label, record.marked_at].map(cell).join(","))].join("\r\n");
  const url = URL.createObjectURL(new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a"); link.href = url; link.download = "attendance-demo.csv"; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
