import type { AttendanceOut, PersonOut, SessionOut, UserOut } from "@/api/client";
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
  if (route === "/health") return { status: "ok" };
  if (route === "/api/dashboard/metrics") return previewSnapshot().metrics;
  if (route === "/api/dashboard/activity") return structuredClone(records);
  if (route === "/api/sessions" && method === "GET") return structuredClone(sessions.filter((session) => !url.searchParams.has("active") || session.is_active === (url.searchParams.get("active") === "true")));
  if (route === "/api/sessions" && method === "POST") { const result = { id: crypto.randomUUID(), ...payload, department: payload.department || null, started_at: new Date().toISOString(), ended_at: null, is_active: true }; sessions.unshift(result); return structuredClone(result); }
  if (/^\/api\/sessions\/[^/]+\/end$/.test(route) && method === "PATCH") { const session = sessions.find((item) => item.id === route.split("/")[3]); if (!session) throw new Error("Preview session not found"); session.is_active = false; session.ended_at = new Date().toISOString(); return structuredClone(session); }
  if (route === "/api/persons" && method === "GET") return structuredClone(people);
  if (/^\/api\/persons\/[^/]+$/.test(route) && method === "DELETE") { people = people.filter((person) => person.id !== route.split("/")[3]); return undefined; }
  if (route === "/api/persons/enroll/analyze") throw new Error("Bản xem thử không phân tích ảnh thật / Preview does not analyze real photos.");
  if (route === "/api/persons/enroll") throw new Error("Bản xem thử không lưu dữ liệu khuôn mặt / Preview does not save facial data.");
  if (route === "/api/attendance") return structuredClone(records.filter((record) => (!url.searchParams.has("session_id") || record.session_id === url.searchParams.get("session_id")) && (!url.searchParams.has("person_id") || record.person_id === url.searchParams.get("person_id")) && (!url.searchParams.has("date") || record.marked_at.slice(0, 10) === url.searchParams.get("date"))));
  if (route === "/api/reports/daily") return trend(Number(url.searchParams.get("days")) || 7);
  if (route === "/api/reports/persons") return people.map((person, index) => ({ person_id: person.id, name: person.name, department: person.department, total_sessions: 10, present_count: index === 3 ? 7 : 9, attendance_rate: index === 3 ? 70 : 90, is_defaulter: index === 3 }));
  if (route === "/api/reports/heatmap") { const dates = trend(Number(url.searchParams.get("days")) || 14).map((day) => day.date); return { dates, persons: people.map((person, index) => ({ person_id: person.id, name: person.name, department: person.department, data: dates.map((_, day) => (day + index) % 5 === 0 ? 0 : 1) })) }; }
  if (route === "/api/auth/users") return structuredClone(users);
  if (route === "/api/auth/student-portal") {
    const pid = url.searchParams.get("person_id") || people[0]?.id;
    const person = people.find((item) => item.id === pid) || people[0] || null;
    if (!person) return { person: null, total_sessions: 0, present_count: 0, absent_count: 0, attendance_rate: 0, is_defaulter: false, sessions: [] };
    const studentSessions = sessions.filter((s) => !s.department || !person.department || s.department === person.department).map((s) => {
      const rec = records.find((r) => r.person_id === person.id && r.session_id === s.id);
      return {
        session_id: s.id,
        label: s.label,
        department: s.department,
        started_at: s.started_at,
        ended_at: s.ended_at,
        is_active: s.is_active,
        attended: Boolean(rec),
        marked_at: rec?.marked_at || null,
        confidence: rec?.confidence ?? null,
        status: rec ? "present" : s.is_active ? "open" : "absent",
      };
    });
    const presentCount = studentSessions.filter((s) => s.attended).length;
    const absentCount = studentSessions.filter((s) => s.status === "absent").length;
    const rate = studentSessions.length ? Math.round((presentCount / studentSessions.length) * 1000) / 10 : 100;
    return { person, total_sessions: studentSessions.length, present_count: presentCount, absent_count: absentCount, attendance_rate: rate, is_defaulter: studentSessions.length > 0 && rate < 75, sessions: studentSessions };
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
