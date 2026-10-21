/**
 * src/api/client.ts
 * Tầng giao tiếp API chuẩn hóa 100% theo backend/core/schemas.py và backend/routers/*.py
 */

const RAW_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const API_BASE_URL = RAW_BASE_URL.replace(/\/+$/, "");
const FALLBACK_API_KEY = import.meta.env.VITE_API_KEY || "";

const TOKEN_STORAGE_KEY = "aura_attend_jwt_token";

let inMemoryToken: string | null =
  typeof window !== "undefined" ? window.localStorage.getItem(TOKEN_STORAGE_KEY) : null;

export function getStoredToken(): string | null {
  return inMemoryToken;
}

export function setStoredToken(token: string | null): void {
  inMemoryToken = token;
  if (typeof window !== "undefined") {
    if (token) {
      window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
    } else {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY);
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

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
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
  role: "admin" | "operator" | "student";
  is_active: boolean;
  created_at: string;
  person_id?: string | null;
}

export interface UserCreatePayload {
  username: string;
  password: string;
  role: "admin" | "operator" | "student";
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
  status: "present" | "absent" | "open";
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
  email: string | null;
  department: string | null;
  photo_url: string | null;
  enrolled_at: string;
  is_active: boolean;
  enrolled_by?: string | null;
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
  id: string;
  label: string;
  department: string | null;
  started_at: string;
  ended_at: string | null;
  is_active: boolean;
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
  liveness_score?: number;
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
  list: () => apiFetch<PersonOut[]>("/api/persons"),
  get: (id: string) => apiFetch<PersonOut>(`/api/persons/${id}`),
  analyzePhotos: (photos: (Blob | File)[]) => {
    const fd = new FormData();
    photos.forEach((p, idx) => fd.append("photos", p, `photo_${idx + 1}.jpg`));
    return apiFetch<EnrollmentAnalysisReport>("/api/persons/enroll/analyze", {
      method: "POST",
      body: fd,
    });
  },
  enroll: (params: {
    name: string;
    email?: string;
    department?: string;
    student_username?: string;
    student_password?: string;
    photos: (Blob | File)[];
  }) => {
    const fd = new FormData();
    fd.append("name", params.name.trim());
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
  delete: (id: string) =>
    apiFetch<void>(`/api/persons/${id}`, {
      method: "DELETE",
    }),
  getDebugConfig: () => apiFetch<SystemConfigReport>("/api/persons/debug-config"),
  getDebugEncodings: () => apiFetch<MissingEncodingsReport>("/api/persons/debug-encodings"),
};

export const sessionsApi = {
  list: (active?: boolean, limit = 50) => {
    const qs = new URLSearchParams();
    if (active !== undefined) qs.set("active", String(active));
    qs.set("limit", String(limit));
    return apiFetch<SessionOut[]>(`/api/sessions?${qs.toString()}`);
  },
  get: (id: string) => apiFetch<SessionOut>(`/api/sessions/${id}`),
  create: (label: string, department?: string) =>
    apiFetch<SessionOut>("/api/sessions", {
      method: "POST",
      body: JSON.stringify({
        label: label.trim(),
        department: department?.trim() || undefined,
      }),
    }),
  end: (id: string) =>
    apiFetch<SessionOut>(`/api/sessions/${id}/end`, {
      method: "PATCH",
    }),
};

export const attendanceApi = {
  identify: (frameBlob: Blob | File, confidence = 0.4) => {
    const fd = new FormData();
    fd.append("frame", frameBlob, "frame.jpg");
    return apiFetch<IdentifyResult[]>(`/api/attendance/identify?confidence=${confidence}`, {
      method: "POST",
      body: fd,
    });
  },
  mark: (sessionId: string, frameBlob: Blob | File, confidence = 0.4) => {
    const fd = new FormData();
    fd.append("frame", frameBlob, "frame.jpg");
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
  }) => {
    const qs = new URLSearchParams();
    if (filters?.session_id) qs.set("session_id", filters.session_id);
    if (filters?.person_id) qs.set("person_id", filters.person_id);
    if (filters?.date) qs.set("date", filters.date);
    if (filters?.status) qs.set("status", filters.status);
    if (filters?.limit) qs.set("limit", String(filters.limit));
    const queryStr = qs.toString();
    return apiFetch<AttendanceOut[]>(`/api/attendance${queryStr ? `?${queryStr}` : ""}`);
  },
  /**
   * Tải xuống CSV có đính kèm JWT Authorization header
   * (Sửa lỗi 401 khi mở tab mới bằng window.open của bản cũ)
   */
  downloadCsv: async (filters?: { session_id?: string; date?: string }): Promise<void> => {
    if (import.meta.env.DEV && /^\/design-preview(?:\/|$)/.test(window.location.pathname)) {
      const { downloadPreviewCsv } = await import("@/preview/mockApi");
      return downloadPreviewCsv(filters);
    }
    const qs = new URLSearchParams();
    if (filters?.session_id) qs.set("session_id", filters.session_id);
    if (filters?.date) qs.set("date", filters.date);
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
  getDaily: (days = 30) => apiFetch<DailyAttendanceStat[]>(`/api/reports/daily?days=${days}`),
  getPersons: (days = 30) => apiFetch<PersonAttendanceStat[]>(`/api/reports/persons?days=${days}`),
  getHeatmap: (days = 14) => apiFetch<HeatmapReport>(`/api/reports/heatmap?days=${days}`),
};
