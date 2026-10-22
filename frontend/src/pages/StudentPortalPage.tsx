import React, { useCallback, useEffect, useRef, useState } from "react";
import { Camera, CheckCircle2, SwitchCamera, Trash2, Upload } from "lucide-react";
import { authApi, personsApi, type EnrollmentAnalysisReport } from "@/api/client";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useToast } from "@/context/ToastContext";
import { useCamera, captureVideoFrame } from "@/hooks/useCamera";
import { useResource } from "@/hooks/useResource";
import { dateTime, errorMessage, isDesignPreview, matchesSearch } from "@/lib/format";
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

type Photo = { blob: Blob; url: string };

export const StudentPortalPage: React.FC<{ previewRole?: "admin" | "operator" | "student" }> = ({ previewRole }) => {
  const { user, role: authRole, refreshProfile } = useAuth();
  const role = previewRole || authRole || "student";
  const { t, lang } = useLanguage();
  const toast = useToast();
  const camera = useCamera();
  const [selectedPersonId, setSelectedPersonId] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<"all" | "present" | "absent" | "open">("all");
  const [search, setSearch] = useState("");

  // State cho biểu mẫu tự khai báo thông tin & khuôn mặt lần đầu
  const [fullName, setFullName] = useState("");
  const [studentId, setStudentId] = useState("");
  const [department, setDepartment] = useState("KTCN");
  const [email, setEmail] = useState("");
  const [source, setSource] = useState<"camera" | "upload">("camera");
  const [photos, setPhotos] = useState<Photo[]>([]);
  const photosRef = useRef(photos);
  const [analysis, setAnalysis] = useState<EnrollmentAnalysisReport | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [capturing, setCapturing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [enrollError, setEnrollError] = useState<string | null>(null);
  const [showReenroll, setShowReenroll] = useState(false);

  useEffect(() => {
    if (user) {
      if (!fullName && user.display_name) setFullName(user.display_name);
      const userEmail = user.google_email || (user.username?.includes("@") ? user.username : "");
      if (!email && userEmail) setEmail(userEmail);
    }
  }, [user, fullName, email]);

  useEffect(() => {
    if (source !== "camera") camera.stop();
  }, [source, camera.stop]);

  useEffect(
    () => () => {
      photosRef.current.forEach((photo) => URL.revokeObjectURL(photo.url));
    },
    []
  );

  const changePhotos = (next: Photo[]) => {
    photosRef.current
      .filter((photo) => !next.includes(photo))
      .forEach((photo) => URL.revokeObjectURL(photo.url));
    photosRef.current = next;
    setPhotos(next);
    setAnalysis(null);
  };

  const analyzePhotos = async () => {
    if (!photos.length || analyzing || submitting || capturing) return;
    setAnalyzing(true);
    setEnrollError(null);
    try {
      const report = await personsApi.analyzePhotos(photos.map((p) => p.blob));
      setAnalysis(report);
    } catch (err) {
      setEnrollError(errorMessage(err));
    } finally {
      setAnalyzing(false);
    }
  };

  const addFiles = (files: FileList | null) => {
    if (!files) return;
    const incoming = Array.from(files);
    if (incoming.length + photosRef.current.length > 5) {
      setEnrollError(t("Tối đa 5 ảnh khuôn mặt.", "Maximum 5 face photos."));
      return;
    }
    if (incoming.some((file) => !file.type.startsWith("image/") || file.size > 10 * 1024 * 1024)) {
      setEnrollError(t("Chỉ chọn file ảnh, tối đa 10 MB mỗi ảnh.", "Choose image files up to 10 MB each."));
      return;
    }
    setEnrollError(null);
    changePhotos([...photosRef.current, ...incoming.map((blob) => ({ blob, url: URL.createObjectURL(blob) }))]);
  };

  const capturePhoto = async () => {
    if (capturing || submitting || photosRef.current.length >= 5) return;
    setCapturing(true);
    try {
      const blob = await captureVideoFrame(camera.videoRef.current);
      if (photosRef.current.length < 5) {
        changePhotos([...photosRef.current, { blob, url: URL.createObjectURL(blob) }]);
      }
    } catch (err) {
      setEnrollError(errorMessage(err));
    } finally {
      setCapturing(false);
    }
  };

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

  const handleSelfEnroll = async (event: React.FormEvent) => {
    event.preventDefault();
    if (submitting || capturing) return;
    if (!fullName.trim() || !studentId.trim() || !department.trim()) {
      setEnrollError(t("Vui lòng nhập đầy đủ Họ tên, MSSV và Lớp học phần.", "Please enter your Full name, Student ID, and Class/Course."));
      return;
    }
    if (!photos.length) {
      setEnrollError(t("Vui lòng chụp hoặc tải lên ít nhất 1 ảnh khuôn mặt rõ nét.", "Please capture or upload at least 1 clear face photo."));
      return;
    }
    setSubmitting(true);
    setEnrollError(null);
    try {
      await personsApi.selfEnroll({
        name: fullName.trim(),
        student_id: studentId.trim().toUpperCase(),
        department: department.trim(),
        email: email.trim() || undefined,
        photos: photos.map((p) => p.blob),
      });
      camera.stop();
      changePhotos([]);
      setShowReenroll(false);
      toast.success(t("Đã lưu hồ sơ & mẫu khuôn mặt AI thành công!", "Student profile & face saved!"));
      await refreshProfile();
      await portal.reload();
    } catch (err) {
      setEnrollError(errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  const { person, total_sessions, present_count, absent_count, attendance_rate, is_defaulter, sessions } =
    portal.data;

  const filteredSessions = sessions.filter((item) => {
    if (statusFilter !== "all" && item.status !== statusFilter) return false;
    return matchesSearch(search, item.label, item.department);
  });

  const poseGuides = [
    t("1. Chính diện (0°)", "1. Frontal (0°)"),
    t("2. Nghiêng nhẹ trái (~15°)", "2. Slight left (~15°)"),
    t("3. Nghiêng nhẹ phải (~15°)", "3. Slight right (~15°)"),
    t("4. Hơi nâng nhẹ cằm", "4. Slight chin up"),
    t("5. Biểu cảm tự nhiên / Có kính", "5. Natural / Glasses"),
  ];

  const openReenrollForm = () => {
    if (person) {
      setFullName(person.name || "");
      setStudentId(person.student_id || "");
      setDepartment(person.department || "KTCN");
      setEmail(person.email || user?.google_email || "");
    }
    setEnrollError(null);
    setShowReenroll((prev) => {
      if (prev) camera.stop();
      return !prev;
    });
  };

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
                    {item.name} {item.student_id ? `(${item.student_id})` : ""} {item.department ? `· ${item.department}` : ""}
                  </option>
                ))}
              </select>
            </Field>
          </div>
        </Section>
      )}

      {!portal.loading && (!person || showReenroll) && (
        <Section
          title={
            person
              ? t("Cập nhật thông tin & Chụp lại khuôn mặt AI", "Update student profile & re-capture AI face")
              : t("Khai báo thông tin sinh viên & Đăng ký khuôn mặt lần đầu", "First-time student profile & face registration")
          }
          description={t(
            "Vui lòng điền Họ tên, Mã số sinh viên (MSSV), Lớp học phần và chụp 1–5 góc mặt (lộ rõ 2 mắt, mũi, miệng) để AI nhận diện chính xác nhất.",
            "Please provide your Full name, Student ID, Class/Course, and 1–5 clear face photos so the classroom AI camera can recognize you."
          )}
          action={
            person ? (
              <button type="button" className="secondary-button" onClick={openReenrollForm}>
                {t("Đóng", "Close")}
              </button>
            ) : undefined
          }
        >
          <ErrorNotice message={enrollError || camera.error} />
          <form onSubmit={handleSelfEnroll} className="enrollment-grid">
            <div className="stack-form">
              <Field id="self-name" label={t("Họ và tên sinh viên *", "Full name *")}>
                <input
                  id="self-name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder={t("VD: Nguyễn Văn A", "e.g. Nguyen Van A")}
                  maxLength={120}
                  required
                />
              </Field>
              <Field id="self-mssv" label={t("Mã số sinh viên (MSSV) *", "Student ID (MSSV) *")}>
                <input
                  id="self-mssv"
                  value={studentId}
                  onChange={(e) => setStudentId(e.target.value)}
                  placeholder={t("VD: 2305CT2070", "e.g. 2305CT2070")}
                  maxLength={40}
                  required
                />
              </Field>
              <Field id="self-dept" label={t("Lớp / Học phần *", "Class / Course *")}>
                <input
                  id="self-dept"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  placeholder={t("VD: KTCN", "e.g. KTCN")}
                  maxLength={80}
                  required
                />
              </Field>
              <Field id="self-email" label="Email">
                <input
                  id="self-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="mssv@dhv.edu.vn"
                />
              </Field>
              <p className="field-hint">
                {t(
                  "Sau khi hoàn tất, mỗi sáng đến lớp bạn chỉ cần nhìn vào Camera của giảng viên là hệ thống tự động ghi nhận điểm danh.",
                  "Once enrolled, simply look at the instructor's camera in class to be automatically marked present."
                )}
              </p>
              <button className="primary-button" type="submit" disabled={submitting || capturing || analyzing || !photos.length || (analysis != null && analysis.invalid > 0)}>
                {submitting
                  ? t("Đang trích xuất khuôn mặt AI…", "Enrolling AI face profile…")
                  : t("Hoàn tất đăng ký hồ sơ & khuôn mặt", "Complete registration")}
              </button>
            </div>

            <div>
              <div className="source-tabs" aria-label={t("Nguồn ảnh", "Photo source")}>
                <button type="button" aria-pressed={source === "camera"} onClick={() => setSource("camera")}>
                  <Camera size={14} />
                  Camera ({photos.length}/5)
                </button>
                <button type="button" aria-pressed={source === "upload"} onClick={() => setSource("upload")}>
                  <Upload size={14} />
                  {t("Tải ảnh từ máy", "Upload photos")}
                </button>
              </div>

              {source === "camera" ? (
                <>
                  <div className="camera-stage">
                    <video
                      ref={camera.videoRef}
                      autoPlay
                      muted
                      playsInline
                      className={camera.facing === "user" ? "mirror-video" : ""}
                    />
                    {!camera.streaming && (
                      <div className="camera-placeholder">
                        <Camera size={28} />
                        <p>{t("Bấm 'Bật camera' bên dưới để chụp khuôn mặt", "Click 'Start camera' below to capture your face")}</p>
                      </div>
                    )}
                  </div>
                  <div className="camera-controls">
                    <button
                      className="secondary-button"
                      type="button"
                      disabled={camera.starting || isDesignPreview()}
                      onClick={() => (camera.streaming ? camera.stop() : void camera.start())}
                    >
                      {camera.starting
                        ? t("Đang mở…", "Starting…")
                        : camera.streaming
                          ? t("Tắt camera", "Stop camera")
                          : t("Bật camera", "Start camera")}
                    </button>
                    <button
                      className="icon-button"
                      type="button"
                      disabled={camera.starting}
                      onClick={() => void camera.flip()}
                      aria-label={t("Đổi camera", "Switch camera")}
                    >
                      <SwitchCamera size={17} />
                    </button>
                    <button
                      className="primary-button"
                      type="button"
                      onClick={capturePhoto}
                      disabled={!camera.streaming || submitting || capturing || photos.length >= 5}
                    >
                      {t("Chụp ảnh khuôn mặt", "Capture photo")}
                    </button>
                  </div>
                </>
              ) : (
                <div className="upload-zone">
                  <label htmlFor="self-enroll-photos">{t("Chọn từ 1 đến 5 ảnh rõ khuôn mặt", "Choose 1 to 5 clear face photos")}</label>
                  <input
                    id="self-enroll-photos"
                    type="file"
                    accept="image/*"
                    multiple
                    disabled={submitting}
                    onChange={(event) => {
                      addFiles(event.target.files);
                      event.target.value = "";
                    }}
                  />
                  <p>{t("Nhìn thẳng, đủ sáng, không đeo khẩu trang · Tối đa 10 MB/ảnh", "Frontal face, well-lit, no mask · Up to 10 MB per photo")}</p>
                </div>
              )}

              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 10 }}>
                {poseGuides.map((guide, idx) => (
                  <span
                    key={idx}
                    className={idx < photos.length ? "attendance-status" : "muted"}
                    style={{
                      fontSize: 11,
                      padding: "3px 8px",
                      border: "1px solid var(--ui-border)",
                      borderRadius: 4,
                      background: idx === photos.length ? "var(--ui-soft)" : undefined,
                      fontWeight: idx === photos.length ? 600 : 400,
                    }}
                  >
                    {idx < photos.length ? "✓ " : idx === photos.length ? "👉 " : ""}{guide}
                  </span>
                ))}
              </div>

              {photos.length > 0 && (
                <div className="photo-previews">
                  {photos.map((photo, index) => (
                    <figure key={photo.url}>
                      <img src={photo.url} alt={t(`Ảnh khuôn mặt ${index + 1}`, `Face photo ${index + 1}`)} />
                      <button
                        className="icon-button"
                        type="button"
                        disabled={submitting || analyzing}
                        aria-label={t(`Xóa ảnh ${index + 1}`, `Remove photo ${index + 1}`)}
                        onClick={() => changePhotos(photos.filter((_, item) => item !== index))}
                      >
                        <Trash2 size={14} />
                      </button>
                    </figure>
                  ))}
                </div>
              )}

              <button
                className="secondary-button quality-button"
                type="button"
                disabled={!photos.length || submitting || capturing || analyzing}
                onClick={analyzePhotos}
              >
                {analyzing ? t("Đang kiểm tra…", "Checking…") : t("Kiểm tra chất lượng ảnh", "Check photo quality")}
              </button>

              {analysis && (
                <div className="quality-results">
                  <p>{t(`${analysis.valid}/${analysis.total} ảnh đạt chất lượng`, `${analysis.valid}/${analysis.total} photos passed`)}</p>
                  {analysis.results.map((item) => (
                    <div key={item.photo} className={item.ok ? "attendance-status" : "warning-text"}>
                      {t("Ảnh", "Photo")} {item.photo}: {item.ok ? t("Đạt", "Passed") : item.reason}
                    </div>
                  ))}
                  {analysis.invalid > 0 && (
                    <p className="warning-text">
                      {t("Vui lòng xóa ảnh không đạt chất lượng trước khi lưu hồ sơ.", "Please remove photos that failed the quality check before saving.")}
                    </p>
                  )}
                </div>
              )}
            </div>
          </form>
        </Section>
      )}

      {person && (
        <Section
          title={t("Hồ sơ học vụ & sinh trắc học", "Academic & biometric profile")}
          action={
            <button type="button" className="secondary-button" onClick={openReenrollForm}>
              <Camera size={14} />
              {showReenroll
                ? t("Ẩn khung chụp lại", "Hide re-capture")
                : t("Chụp lại khuôn mặt / Sửa hồ sơ", "Re-capture face / Edit profile")}
            </button>
          }
        >
          <dl className="config-grid">
            <div>
              <dt>{t("Họ và tên sinh viên", "Student name")}</dt>
              <dd className="font-medium">
                {person.name} {person.student_id ? `(${person.student_id})` : ""}
              </dd>
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
        </Section>
      )}

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
            {!person
              ? t("Hoàn tất đăng ký khuôn mặt ở trên để kích hoạt", "Complete face registration above to activate")
              : present_count + absent_count === 0
                ? t("Chưa có buổi được đánh giá", "No assessed sessions yet")
                : is_defaulter
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
                  ) : session.status === "late" ? (
                    <span className="attendance-status">
                      <CheckCircle2 size={12} />
                      {t("Đi muộn (Late)", "Late")}
                    </span>
                  ) : session.status === "excused" ? (
                    <span className="attendance-status">
                      <CheckCircle2 size={12} />
                      {t("Vắng có phép", "Excused")}
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
