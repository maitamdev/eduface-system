/**
 * src/api/client.ts
 * Tầng giao tiếp API chuẩn hóa 100% theo backend/core/schemas.py và backend/routers/*.py
 */

const RAW_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? "https://eduface-system.onrender.com" : "http://localhost:8000");
export const API_BASE_URL = RAW_BASE_URL.replace(/\/+$/, "").replace(/\/api$/i, "");
const FALLBACK_API_KEY = import.meta.env.DEV ? import.meta.env.VITE_API_KEY || "" : "";

const TOKEN_STORAGE_KEY = "aura_attend_jwt_token";
// Remove the previous persistent copy during the storage migration.
if (typeof window !== "undefined") window.localStorage.removeItem(TOKEN_STORAGE_KEY);

let inMemoryToken: string | null =
  typeof window !== "undefined" ? window.sessionStorage.getItem(TOKEN_STORAGE_KEY) : null;

export function getStoredToken(): string | null {
  return inMemoryToken;
}

export function setStoredToken(token: string | null): void {
  inMemoryToken = token;
  if (typeof window !== "undefined") {
    if (token) {
      window.sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
    } else {
      window.sessionStorage.removeItem(TOKEN_STORAGE_KEY);
    }
  }
}

export class ApiClientError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, message: string, detail?: unknown) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.detail = detail;
  }
}

function buildAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {};
  if (inMemoryToken) {
    headers["Authorization"] = `Bearer ${inMemoryToken}`;
  } else if (FALLBACK_API_KEY) {
    headers["X-API-Key"] = FALLBACK_API_KEY;
  }
  return headers;
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (import.meta.env.DEV && /^\/design-preview(?:\/|$)/.test(window.location.pathname)) {
    const { previewRequest } = await import("@/preview/mockApi");
    return previewRequest(path, init) as Promise<T>;
  }
  const isFormData = typeof FormData !== "undefined" && init.body instanceof FormData;

  const headers: Record<string, string> = {
    ...(!isFormData && init.body ? { "Content-Type": "application/json" } : {}),
    ...buildAuthHeaders(),
    ...(init.headers as Record<string, string> | undefined),
  };

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    signal: init.signal || AbortSignal.timeout(45000),
  });

  if (!response.ok) {
    if (response.status === 401 && path !== "/api/auth/login") window.dispatchEvent(new Event("aura:unauthorized"));
    const errBody = await response.json().catch(() => ({ detail: response.statusText }));
    let message = errBody?.detail || `HTTP ${response.status}`;
    if (Array.isArray(message)) {
      message = message.map((item: any) => item?.msg || JSON.stringify(item)).join("; ");
    }
    const requestId = response.headers.get("X-Request-ID") || errBody?.request_id;
    if (response.status >= 500 && typeof requestId === "string" && /^[A-Za-z0-9._-]{1,64}$/.test(requestId)) {
      message = `${message} (Mã yêu cầu: ${requestId})`;
    }
    throw new ApiClientError(response.status, String(message), errBody);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

// ── Schemas khớp 100% với backend/core/schemas.py ─────────────────────────────

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  role: "admin" | "operator" | "student";
  username: string;
}

export interface UserOut {
  id: string;
  username: string;
  display_name?: string | null;
  role: "admin" | "operator" | "student";
  is_active: boolean;
  created_at: string;
  person_id?: string | null;
  google_email?: string | null;
  microsoft_oid?: string | null;
}

export interface UserCreatePayload {
  username: string;
  password: string;
  role: "admin" | "operator" | "student";
  person_id?: string | null;
}

export interface UserUpdatePayload {
  role?: "admin" | "operator" | "student";
  is_active?: boolean;
  password?: string;
  person_id?: string | null;
}

export interface StudentSessionItem {
  session_id: string;
  label: string;
  department: string | null;
  started_at: string;
  ended_at: string | null;
  is_active: boolean;
  attended: boolean;
  marked_at: string | null;
  confidence: number | null;
  status: "present" | "late" | "excused" | "absent" | "open";
}

export interface StudentPortalSummary {
  person: PersonOut | null;
  total_sessions: number;
  present_count: number;
  absent_count: number;
  attendance_rate: number;
  is_defaulter: boolean;
  sessions: StudentSessionItem[];
}

export interface PersonOut {
  id: string;
  name: string;
  student_id?: string | null;
  email: string | null;
  department: string | null;
  phone?: string | null;
  date_of_birth?: string | null;
  gender?: string | null;
  cohort?: string | null;
  major?: string | null;
  advisor?: string | null;
  academic_status?: string | null;
  notes?: string | null;
  photo_url: string | null;
  enrolled_at: string;
  is_active: boolean;
  enrolled_by?: string | null;
}

export interface CourseOut {
  id: string;
  code: string;
  name: string;
  department: string;
  credits: number;
  lecturer?: string | null;
  schedule?: string | null;
  room?: string | null;
  semester?: string | null;
  created_at: string;
}

export interface StudentGradeRow {
  course_id?: string | null;
  course_name?: string | null;
  semester?: string | null;
  credits?: number;
  person_id: string;
  name: string;
  student_id?: string | null;
  department?: string | null;
  total_sessions: number;
  present_count: number;
  attendance_rate: number;
  attendance_score: number;
  midterm_score?: number | null;
  final_score?: number | null;
  bonus_score: number;
  total_10?: number | null;
  gpa_4?: number | null;
  letter_grade?: string | null;
  exam_eligible: boolean;
  note?: string | null;
}

export interface LeaveRequestOut {
  id: string;
  person_id: string;
  person_name: string;
  student_id?: string | null;
  department?: string | null;
  session_id?: string | null;
  session_label?: string | null;
  leave_date: string;
  reason: string;
  evidence_url?: string | null;
  status: "pending" | "approved" | "rejected";
  reviewer_note?: string | null;
  created_at: string;
  reviewed_at?: string | null;
}

export interface AnnouncementOut {
  id: string;
  title: string;
  content: string;
  department?: string | null;
  priority: "normal" | "important" | "exam";
  author: string;
  created_at: string;
}

export interface PhotoQualityItem {
  photo: number;
  ok: boolean;
  det_score: number | null;
  face_size: [number, number] | null;
  reason: string;
}

export interface EnrollmentAnalysisReport {
  total: number;
  valid: number;
  invalid: number;
  results: PhotoQualityItem[];
}

export interface SessionOut {
  course_id?: string | null;
  id: string;
  label: string;
  department: string | null;
  started_at: string;
  ended_at: string | null;
  is_active: boolean;
  late_after_minutes?: number | null;
}

export interface FaceBox {
  left: number;
  top: number;
  width: number;
  height: number;
}

export interface IdentifyResult {
  azure_person_id: string;
  name: string;
  confidence: number;
  face_box: FaceBox;
  already_marked: boolean;
  is_live?: boolean;
  liveness_score?: number | null;
  spoof_reason?: string | null;
}

export interface MarkAttendanceResponse {
  session_id: string;
  identified: IdentifyResult[];
  new_records: number;
}

export interface AttendanceOut {
  id: string;
  person_id: string;
  person_name: string;
  student_id?: string | null;
  department: string | null;
  session_id: string;
  session_label: string;
  marked_at: string;
  confidence: number | null;
  status: string;
  marked_by?: string | null;
}

export interface DashboardMetrics {
  total_enrolled: number;
  sessions_today: number;
  present_today: number;
  attendance_rate: number;
}

export interface ActivityItem {
  id: string;
  person_name: string;
  department: string | null;
  session_label: string;
  marked_at: string;
  confidence: number | null;
  status: string;
}

export interface DailyAttendanceStat {
  date: string;
  total_sessions: number;
  total_present: number;
  attendance_rate: number;
}

export interface PersonAttendanceStat {
  person_id: string;
  name: string;
  department: string | null;
  total_sessions: number;
  present_count: number;
  attendance_rate: number;
  is_defaulter: boolean;
}

export interface HeatmapPersonRow {
  person_id: string;
  name: string;
  department: string | null;
  data: Array<1 | 0 | null>;
}

export interface HeatmapReport {
  dates: string[];
  persons: HeatmapPersonRow[];
}

export interface SystemConfigReport {
  status: string;
  issues: string[];
  MONGODB_URL: string;
  MONGODB_DB_NAME: string;
  AZURE_STORAGE_CONNECTION_STRING: string;
  MIN_CONFIDENCE: string;
  DUPLICATE_THRESHOLD: string;
  API_KEY_ADMIN_configured: boolean;
  API_KEY_OPERATOR_configured: boolean;
  API_KEY_legacy_configured: boolean;
}

export interface MissingEncodingsReport {
  total_active_persons: number;
  persons_with_encodings: number;
  persons_missing_encodings: number;
  missing: Array<{
    person_id: string;
    name: string;
    enrolled_at: string;
    action_needed: string;
  }>;
}

export interface WsFrameResponse {
  timestamp: string;
  session_id: string;
  matches: IdentifyResult[];
  faces_detected: number;
  error?: string;
  status?: number;
}

// ── Các nhóm API tương ứng với backend/routers/*.py ───────────────────────────

export const healthApi = {
  check: () => apiFetch<{ status: string }>("/health"),
};

// Send credentials as the first socket message, never in a URL or access log.
export function getSocketAuthentication() {
  return inMemoryToken ? { authorization: `Bearer ${inMemoryToken}` } : { api_key: FALLBACK_API_KEY };
}

export const authApi = {
  changePassword: async (current: string, next: string) => {
    const result = await apiFetch<TokenResponse>("/api/auth/password", { method: "POST", body: JSON.stringify({ current_password: current, new_password: next }) });
    setStoredToken(result.access_token); return result;
  },
  googleConfig: () => apiFetch<{ enabled: boolean; client_id: string }>("/api/auth/google/config"),
  googleExchange: async (accessToken: string) => {
    const response = await apiFetch<TokenResponse>("/api/auth/google", {
      method: "POST",
      body: JSON.stringify({ access_token: accessToken }),
    });
    setStoredToken(response.access_token);
    return response;
  },
  linkGoogle: (userId: string, email: string | null) =>
    apiFetch<{ linked: boolean; google_email: string | null }>(
      `/api/auth/users/${encodeURIComponent(userId)}/google`,
      { method: "PUT", body: JSON.stringify({ email }) }
    ),
  microsoftConfig: () => apiFetch<{ enabled: boolean; client_id: string; tenant_id: string }>("/api/auth/microsoft/config"),
  microsoftChallenge: () => apiFetch<{ challenge_id: string; nonce: string }>("/api/auth/microsoft/challenge", { method: "POST" }),
  microsoftExchange: async (challengeId: string, idToken: string) => {
    const response = await apiFetch<TokenResponse>("/api/auth/microsoft", { method: "POST", body: JSON.stringify({ challenge_id: challengeId, id_token: idToken }) });
    setStoredToken(response.access_token);
    return response;
  },
  linkMicrosoft: (userId: string, objectId: string | null) => apiFetch<{ linked: boolean; object_id: string | null }>(`/api/auth/users/${encodeURIComponent(userId)}/microsoft`, { method: "PUT", body: JSON.stringify({ object_id: objectId }) }),
  login: async (username: string, password: string): Promise<TokenResponse> => {
    const res = await apiFetch<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    setStoredToken(res.access_token);
    return res;
  },
  logout: () => {
    setStoredToken(null);
  },
  me: () => apiFetch<UserOut>("/api/auth/me"),
  listUsers: () => apiFetch<UserOut[]>("/api/auth/users"),
  registerUser: (payload: UserCreatePayload) =>
    apiFetch<UserOut>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateUser: (userId: string, payload: UserUpdatePayload) =>
    apiFetch<UserOut>(`/api/auth/users/${encodeURIComponent(userId)}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  getStudentPortal: (personId?: string) =>
    apiFetch<StudentPortalSummary>(
      `/api/auth/student-portal${personId ? `?person_id=${encodeURIComponent(personId)}` : ""}`
    ),
};

export const dashboardApi = {
  getMetrics: () => apiFetch<DashboardMetrics>("/api/dashboard/metrics"),
  getActivity: () => apiFetch<ActivityItem[]>("/api/dashboard/activity"),
};

export const personsApi = {
  list: (department?: string) =>
    apiFetch<PersonOut[]>(
      `/api/persons${department ? `?department=${encodeURIComponent(department)}` : ""}`
    ),
  get: (id: string) => apiFetch<PersonOut>(`/api/persons/${id}`),
  update: (
    id: string,
    payload: {
      name?: string;
      student_id?: string | null;
      department?: string | null;
      email?: string | null;
      phone?: string | null;
      date_of_birth?: string | null;
      gender?: string | null;
      cohort?: string | null;
      major?: string | null;
      advisor?: string | null;
      academic_status?: string | null;
      notes?: string | null;
    }
  ) =>
    apiFetch<PersonOut>(`/api/persons/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  analyzePhotos: (photos: (Blob | File)[]) => {
    const fd = new FormData();
    photos.forEach((p, idx) => fd.append("photos", p, `photo_${idx + 1}.jpg`));
    return apiFetch<EnrollmentAnalysisReport>("/api/persons/enroll/analyze", {
      method: "POST",
      body: fd,
    });
  },
  enroll: (params: {
    person_id?: string;
    consent: boolean;
    name: string;
    student_id?: string;
    email?: string;
    department?: string;
    student_username?: string;
    student_password?: string;
    photos: (Blob | File)[];
  }) => {
    const fd = new FormData();
    fd.append("consent", String(params.consent));
    if (params.person_id) fd.append("person_id", params.person_id);
    fd.append("name", params.name.trim());
    if (params.student_id?.trim()) fd.append("student_id", params.student_id.trim());
    if (params.email?.trim()) fd.append("email", params.email.trim());
    if (params.department?.trim()) fd.append("department", params.department.trim());
    if (params.student_username?.trim()) fd.append("student_username", params.student_username.trim());
    if (params.student_password?.trim()) fd.append("student_password", params.student_password.trim());
    params.photos.forEach((p, idx) => fd.append("photos", p, `photo_${idx + 1}.jpg`));
    return apiFetch<PersonOut>("/api/persons/enroll", {
      method: "POST",
      body: fd,
    });
  },
  selfEnroll: (params: {
    consent: boolean;
    name: string;
    student_id: string;
    department: string;
    email?: string;
    photos: (Blob | File)[];
  }) => {
    const fd = new FormData();
    fd.append("consent", String(params.consent));
    fd.append("name", params.name.trim());
    fd.append("student_id", params.student_id.trim());
    fd.append("department", params.department.trim());
    if (params.email?.trim()) fd.append("email", params.email.trim());
    params.photos.forEach((p, idx) => fd.append("photos", p, `photo_${idx + 1}.jpg`));
    return apiFetch<PersonOut>("/api/persons/self-enroll", {
      method: "POST",
      body: fd,
    });
  },
  delete: (id: string) =>
    apiFetch<void>(`/api/persons/${id}`, {
      method: "DELETE",
    }),
  getDebugConfig: () => apiFetch<SystemConfigReport>("/api/persons/debug-config"),
  getDebugEncodings: () => apiFetch<MissingEncodingsReport>("/api/persons/debug-encodings"),
};

export const sessionsApi = {
  listAll: async (active?: boolean): Promise<SessionOut[]> => {
    const all: SessionOut[] = [];
    for (let offset = 0;; offset += 200) {
      const page = await sessionsApi.list(active, 200, offset); all.push(...page);
      if (page.length < 200) return all;
    }
  },
  list: (active?: boolean, limit = 50, offset = 0) => {
    const qs = new URLSearchParams();
    if (active !== undefined) qs.set("active", String(active));
    qs.set("limit", String(limit));
    qs.set("offset", String(offset));
    return apiFetch<SessionOut[]>(`/api/sessions?${qs.toString()}`);
  },
  get: (id: string) => apiFetch<SessionOut>(`/api/sessions/${id}`),
  create: (label: string, department?: string, lateAfterMinutes = 15, courseId?: string) =>
    apiFetch<SessionOut>("/api/sessions", {
      method: "POST",
      body: JSON.stringify({
        label: label.trim(),
        department: department?.trim() || undefined,
        late_after_minutes: lateAfterMinutes,
        course_id: courseId,
      }),
    }),
  end: (id: string) =>
    apiFetch<SessionOut>(`/api/sessions/${id}/end`, {
      method: "PATCH",
    }),
};

export const attendanceApi = {
  listAll: async (filters: { session_id?: string; date?: string; status?: string } = {}): Promise<AttendanceOut[]> => {
    const all: AttendanceOut[] = [];
    for (let offset = 0;; offset += 1000) {
      const page = await attendanceApi.list({ ...filters, limit: 1000, offset }); all.push(...page);
      if (page.length < 1000) return all;
    }
  },
  identify: (frameBlob: Blob | File, confidence = 0.4) => {
    const fd = new FormData();
    fd.append("frame", frameBlob, "frame.jpg");
    return apiFetch<IdentifyResult[]>(`/api/attendance/identify?confidence=${confidence}`, {
      method: "POST",
      body: fd,
    });
  },
  mark: (sessionId: string, frameBlob: Blob | File, confidence = 0.4, probeBlob?: Blob | File) => {
    const fd = new FormData();
    fd.append("frame", frameBlob, "frame.jpg");
    if (probeBlob) {
      fd.append("probe_frame", probeBlob, "probe_frame.jpg");
    }
    return apiFetch<MarkAttendanceResponse>(
      `/api/attendance/mark/${sessionId}?confidence=${confidence}`,
      {
        method: "POST",
        body: fd,
      }
    );
  },
  list: (filters?: {
    session_id?: string;
    person_id?: string;
    date?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) => {
    const qs = new URLSearchParams();
    if (filters?.session_id) qs.set("session_id", filters.session_id);
    if (filters?.person_id) qs.set("person_id", filters.person_id);
    if (filters?.date) qs.set("date", filters.date);
    if (filters?.status) qs.set("status", filters.status);
    if (filters?.limit) qs.set("limit", String(filters.limit));
    if (filters?.offset) qs.set("offset", String(filters.offset));
    const queryStr = qs.toString();
    return apiFetch<AttendanceOut[]>(`/api/attendance${queryStr ? `?${queryStr}` : ""}`);
  },
  setManual: (payload: {
    person_id: string;
    session_id: string;
    status: "present" | "late" | "excused" | "absent";
  }) =>
    apiFetch<AttendanceOut>("/api/attendance/manual", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  /**
   * Tải xuống CSV có đính kèm JWT Authorization header
   * (Sửa lỗi 401 khi mở tab mới bằng window.open của bản cũ)
   */
  downloadCsv: async (filters?: { session_id?: string; date?: string; department?: string }): Promise<void> => {
    if (import.meta.env.DEV && /^\/design-preview(?:\/|$)/.test(window.location.pathname)) {
      const { downloadPreviewCsv } = await import("@/preview/mockApi");
      return downloadPreviewCsv(filters);
    }
    const qs = new URLSearchParams();
    if (filters?.session_id) qs.set("session_id", filters.session_id);
    if (filters?.date) qs.set("date", filters.date);
    if (filters?.department) qs.set("department", filters.department);
    const queryStr = qs.toString();

    const response = await fetch(
      `${API_BASE_URL}/api/attendance/export/csv${queryStr ? `?${queryStr}` : ""}`,
      {
        method: "GET",
        headers: buildAuthHeaders(),
      }
    );

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new ApiClientError(response.status, err?.detail || "Export CSV failed", err);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const dateSuffix = filters?.date || new Date().toISOString().slice(0, 10);
    a.download = `attendance_${dateSuffix}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },
  getWebSocketUrl: (sessionId: string): string => {
    const wsBase = API_BASE_URL.replace(/^http/, "ws");
    return `${wsBase}/api/attendance/ws/${sessionId}`;
  },
};

export const reportsApi = {
  getDaily: (days = 30, department?: string) => {
    const qs = new URLSearchParams({ days: String(days) });
    if (department) qs.set("department", department);
    return apiFetch<DailyAttendanceStat[]>(`/api/reports/daily?${qs.toString()}`);
  },
  getPersons: (days = 30, department?: string) => {
    const qs = new URLSearchParams({ days: String(days) });
    if (department) qs.set("department", department);
    return apiFetch<PersonAttendanceStat[]>(`/api/reports/persons?${qs.toString()}`);
  },
  getHeatmap: (days = 14, department?: string) => {
    const qs = new URLSearchParams({ days: String(days) });
    if (department) qs.set("department", department);
    return apiFetch<HeatmapReport>(`/api/reports/heatmap?${qs.toString()}`);
  },
};

export const academicApi = {
  getTranscript: (personId?: string) => apiFetch<{ courses: StudentGradeRow[]; credits_graded: number; weighted_gpa: number | null }>(`/api/academic/my-transcript${personId ? `?person_id=${encodeURIComponent(personId)}` : ""}`),
  listCourses: (department?: string) => {
    const qs = new URLSearchParams();
    if (department) qs.set("department", department);
    return apiFetch<CourseOut[]>(`/api/academic/courses${qs.toString() ? `?${qs.toString()}` : ""}`);
  },
  createCourse: (payload: {
    code: string;
    name: string;
    department: string;
    credits: number;
    lecturer?: string;
    schedule?: string;
    room?: string;
    semester?: string;
  }) =>
    apiFetch<CourseOut>("/api/academic/courses", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  deleteCourse: (id: string) =>
    apiFetch<void>(`/api/academic/courses/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),
  listGrades: (department?: string, courseId?: string) => {
    const qs = new URLSearchParams();
    if (courseId) qs.set("course_id", courseId);
    if (department) qs.set("department", department);
    return apiFetch<StudentGradeRow[]>(`/api/academic/grades${qs.toString() ? `?${qs.toString()}` : ""}`);
  },
  getMyGrade: (personId?: string, courseId?: string) => {
    const qs = new URLSearchParams();
    if (courseId) qs.set("course_id", courseId);
    if (personId) qs.set("person_id", personId);
    return apiFetch<StudentGradeRow | null>(`/api/academic/my-grade${qs.toString() ? `?${qs.toString()}` : ""}`);
  },
  upsertGrade: (payload: {
    course_id: string;
    person_id: string;
    midterm_score?: number | null;
    final_score?: number | null;
    bonus_score?: number;
    note?: string | null;
  }) =>
    apiFetch<StudentGradeRow>("/api/academic/grades", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  listLeaves: (filters?: { department?: string; status?: string }) => {
    const qs = new URLSearchParams();
    if (filters?.department) qs.set("department", filters.department);
    if (filters?.status) qs.set("status", filters.status);
    return apiFetch<LeaveRequestOut[]>(`/api/academic/leaves${qs.toString() ? `?${qs.toString()}` : ""}`);
  },
  createLeave: (
    payload: {
      session_id?: string;
      leave_date: string;
      reason: string;
      evidence_url?: string;
    },
    personId?: string
  ) => {
    const qs = new URLSearchParams();
    if (personId) qs.set("person_id", personId);
    return apiFetch<LeaveRequestOut>(`/api/academic/leaves${qs.toString() ? `?${qs.toString()}` : ""}`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  reviewLeave: (id: string, payload: { status: "approved" | "rejected"; reviewer_note?: string }) =>
    apiFetch<LeaveRequestOut>(`/api/academic/leaves/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  listAnnouncements: (department?: string) => {
    const qs = new URLSearchParams();
    if (department) qs.set("department", department);
    return apiFetch<AnnouncementOut[]>(`/api/academic/announcements${qs.toString() ? `?${qs.toString()}` : ""}`);
  },
  createAnnouncement: (payload: {
    title: string;
    content: string;
    department?: string;
    priority: "normal" | "important" | "exam";
  }) =>
    apiFetch<AnnouncementOut>("/api/academic/announcements", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  deleteAnnouncement: (id: string) =>
    apiFetch<void>(`/api/academic/announcements/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }),
  importStudents: (payload: {
    students: Array<{
      student_id: string;
      name: string;
      department: string;
      email?: string;
      phone?: string;
      gender?: string;
      date_of_birth?: string;
      cohort?: string;
      major?: string;
    }>;
    create_login_accounts?: boolean;
    default_password?: string;
  }) =>
    apiFetch<{
      created: number;
      updated: number;
      accounts_created: number;
      total_processed: number;
      credentials: { username: string; password: string; student_id: string }[];
    }>("/api/academic/import-students", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
