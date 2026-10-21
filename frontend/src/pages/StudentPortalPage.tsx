import React, { useCallback, useState } from "react";
import { CheckCircle2 } from "lucide-react";
import { authApi, personsApi } from "@/api/client";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useResource } from "@/hooks/useResource";
import { dateTime, matchesSearch } from "@/lib/format";
import {
  PageHeader,
  Section,
  RefreshButton,
  ErrorNotice,
  Field,
  SearchField,
  EmptyState,
  Table,
} from "@/components/ProductUI";

export const StudentPortalPage: React.FC<{ previewRole?: "admin" | "operator" | "student" }> = ({ previewRole }) => {
  const { user, role: authRole } = useAuth();
  const role = previewRole || authRole || "student";
  const { t, lang } = useLanguage();
  const [selectedPersonId, setSelectedPersonId] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<"all" | "present" | "absent" | "open">("all");
  const [search, setSearch] = useState("");

  const peopleLoader = useCallback(
    () => (role === "admin" ? personsApi.list() : Promise.resolve([])),
    [role]
  );
  const people = useResource(peopleLoader, []);

  const portalLoader = useCallback(
    () => authApi.getStudentPortal(selectedPersonId || undefined),
    [selectedPersonId]
  );
  const portal = useResource(portalLoader, {
    person: null,
    total_sessions: 0,
    present_count: 0,
    absent_count: 0,
    attendance_rate: 0,
    is_defaulter: false,
    sessions: [],
  });

  const { person, total_sessions, present_count, absent_count, attendance_rate, is_defaulter, sessions } =
    portal.data;

  const filteredSessions = sessions.filter((item) => {
    if (statusFilter !== "all" && item.status !== statusFilter) return false;
    return matchesSearch(search, item.label, item.department);
  });

  return (
    <div className="product-page">
      <PageHeader
        title={t("Cổng thông tin sinh viên", "Student portal")}
        description={t(
          "Theo dõi học phần đang học, lịch sử điểm danh từng buổi và tỷ lệ chuyên cần cá nhân.",
          "Track enrolled classes, session-by-session check-ins and personal attendance standing."
        )}
      >
        <RefreshButton onClick={portal.reload} loading={portal.loading} />
      </PageHeader>

      <ErrorNotice message={portal.error} retry={portal.reload} />

      {role === "admin" && people.data.length > 0 && (
        <Section
          title={t("Xem góc nhìn sinh viên (Dành cho Quản trị viên)", "Preview student portal (Admin)")}
          description={t(
            "Chọn một hồ sơ sinh viên để kiểm tra dữ liệu chuyên cần hiển thị trên cổng sinh viên.",
            "Select an enrolled student profile to inspect their portal view."
          )}
        >
          <div className="scanner-setup">
            <Field id="student-preview-select" label={t("Sinh viên", "Student profile")}>
              <select
                id="student-preview-select"
                value={selectedPersonId || person?.id || ""}
                onChange={(event) => setSelectedPersonId(event.target.value)}
              >
                <option value="">{t("Hồ sơ liên kết với tài khoản", "Account-linked profile")}</option>
                {people.data.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name} {item.department ? `· ${item.department}` : ""}
                  </option>
                ))}
              </select>
            </Field>
          </div>
        </Section>
      )}

      <Section title={t("Hồ sơ học vụ & sinh trắc học", "Academic & biometric profile")}>
        {person ? (
          <dl className="config-grid">
            <div>
              <dt>{t("Họ và tên sinh viên", "Student name")}</dt>
              <dd className="font-medium">{person.name}</dd>
            </div>
            <div>
              <dt>{t("Lớp / Học phần", "Class / Course")}</dt>
              <dd>{person.department || t("Chưa phân lớp (Học phần chung)", "General course")}</dd>
            </div>
            <div>
              <dt>{t("Email / Mã định danh", "Email / Identifier")}</dt>
              <dd>{person.email || user?.username || "–"}</dd>
            </div>
            <div>
              <dt>{t("Trạng thái khuôn mặt AI", "Face recognition status")}</dt>
              <dd className="attendance-status">
                <CheckCircle2 size={13} />
                {t("Đã đăng ký · Sẵn sàng quét", "Enrolled · Ready for scan")}
              </dd>
            </div>
          </dl>
        ) : (
          <EmptyState loading={portal.loading}>
            {t(
              "Tài khoản này chưa được liên kết với hồ sơ khuôn mặt sinh viên nào. Vui lòng liên hệ Quản trị viên để đăng ký khuôn mặt.",
              "This account is not linked to an enrolled student face profile yet. Please contact the administrator."
            )}
          </EmptyState>
        )}
      </Section>

      <dl className="metric-strip">
        <div>
          <dt>{t("Tổng số buổi học", "Total sessions")}</dt>
          <dd>{portal.loading ? "…" : total_sessions}</dd>
          <p>{t("của lớp / học phần", "for your class / course")}</p>
        </div>
        <div>
          <dt>{t("Số buổi có mặt", "Sessions present")}</dt>
          <dd>{portal.loading ? "…" : present_count}</dd>
          <p>{t("đã xác thực khuôn mặt AI", "verified by AI camera")}</p>
        </div>
        <div>
          <dt>{t("Số buổi vắng mặt", "Sessions absent")}</dt>
          <dd>{portal.loading ? "…" : absent_count}</dd>
          <p>{t("phiên đã đóng không có bản ghi", "closed sessions without check-in")}</p>
        </div>
        <div>
          <dt>{t("Tỷ lệ chuyên cần", "Attendance rate")}</dt>
          <dd className={is_defaulter ? "warning-text" : ""}>
            {portal.loading ? "…" : person ? `${attendance_rate}%` : "–"}
          </dd>
          <p className={is_defaulter ? "warning-text" : "attendance-status"}>
            {!person ? t("Chưa liên kết hồ sơ", "Profile not linked") : present_count + absent_count === 0 ? t("Chưa có buổi được đánh giá", "No assessed sessions yet") : is_defaulter
              ? t("Cảnh báo: Dưới 75% quy định", "Warning: Below 75% requirement")
              : t("Đủ điều kiện chuyên cần (≥ 75%)", "Meets requirement (≥ 75%)")}
          </p>
        </div>
      </dl>

      <Section
        title={t("Chi tiết điểm danh theo từng buổi học", "Session-by-session attendance log")}
        description={t(
          "Danh sách toàn bộ các buổi học của lớp/học phần và thời gian camera ghi nhận bạn có mặt.",
          "All sessions for your class/course and the exact time the camera recorded your check-in."
        )}
        action={
          <div className="chart-range" aria-label={t("Lọc trạng thái", "Filter status")}>
            {(
              [
                ["all", t("Tất cả", "All")],
                ["present", t("Có mặt", "Present")],
                ["absent", t("Vắng mặt", "Absent")],
                ["open", t("Đang mở", "Open")],
              ] as const
            ).map(([val, label]) => (
              <button
                key={val}
                type="button"
                aria-pressed={statusFilter === val}
                onClick={() => setStatusFilter(val)}
              >
                {label}
              </button>
            ))}
          </div>
        }
      >
        <div className="table-toolbar">
          <SearchField
            label={t("Tìm tên buổi học hoặc học phần…", "Search session or course…")}
            value={search}
            onChange={setSearch}
          />
          <span className="record-count">
            {t(`${filteredSessions.length} buổi học`, `${filteredSessions.length} sessions`)}
          </span>
        </div>

        <Table label={t("Lịch sử buổi học của sinh viên", "Student session history")}>
          <thead>
            <tr>
              <th>{t("Buổi học / Học phần", "Session / Course")}</th>
              <th>{t("Lớp", "Class")}</th>
              <th>{t("Thời gian mở lớp", "Session time")}</th>
              <th>{t("Trạng thái điểm danh", "Attendance status")}</th>
              <th>{t("Giờ quét mặt", "Check-in time")}</th>
              <th className="align-right">{t("Độ khớp AI", "AI confidence")}</th>
            </tr>
          </thead>
          <tbody>
            {filteredSessions.map((session) => (
              <tr key={session.session_id}>
                <td className="cell-strong">{session.label}</td>
                <td>{session.department || t("Chung", "General")}</td>
                <td className="numeric-cell">{dateTime(session.started_at, lang)}</td>
                <td>
                  {session.status === "present" ? (
                    <span className="attendance-status">
                      <CheckCircle2 size={12} />
                      {t("Có mặt", "Present")}
                    </span>
                  ) : session.status === "open" ? (
                    <span className="session-status">
                      <span className="status-dot" />
                      {t("Đang mở lớp · Chưa quét", "Session open · Not checked in")}
                    </span>
                  ) : (
                    <span className="warning-text">{t("Vắng mặt", "Absent")}</span>
                  )}
                </td>
                <td className="numeric-cell">
                  {session.marked_at ? dateTime(session.marked_at, lang) : "–"}
                </td>
                <td className="align-right numeric-cell">
                  {session.confidence != null ? `${Math.round(session.confidence * 100)}%` : "–"}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>

        {!filteredSessions.length && (
          <EmptyState loading={portal.loading}>
            {t("Chưa có buổi học nào phù hợp.", "No matching sessions found.")}
          </EmptyState>
        )}
      </Section>
    </div>
  );
};
