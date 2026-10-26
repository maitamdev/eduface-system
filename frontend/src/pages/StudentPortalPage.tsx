import React, { useCallback, useEffect, useRef, useState } from "react";
import { Camera, CheckCircle2, SwitchCamera, Trash2, Upload, FileCheck2, Megaphone, BookOpen, Award, Send } from "lucide-react";
import {
  authApi,
  personsApi,
  academicApi,
  type EnrollmentAnalysisReport,
  type StudentGradeRow,
  type LeaveRequestOut,
  type AnnouncementOut,
  type CourseOut,
} from "@/api/client";
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

  const [consent, setConsent] = useState(false);
  const [courseId, setCourseId] = useState("");
  const gradeLoader = useCallback(
    () => academicApi.getMyGrade(selectedPersonId || undefined, courseId || undefined),
    [selectedPersonId, courseId]
  );
  const transcript = useResource(useCallback(() => academicApi.getTranscript(selectedPersonId || undefined), [selectedPersonId]), { courses: [], credits_graded: 0, weighted_gpa: null });
  const myGrade = useResource<StudentGradeRow | null>(gradeLoader, null);

  const leavesLoader = useCallback(() => academicApi.listLeaves(), []);
  const myLeaves = useResource<LeaveRequestOut[]>(leavesLoader, []);

  const announcementsLoader = useCallback(
    () => academicApi.listAnnouncements(portal.data.person?.department || undefined),
    [portal.data.person?.department]
  );
  const announcements = useResource<AnnouncementOut[]>(announcementsLoader, []);

  const coursesLoader = useCallback(
    () => academicApi.listCourses(portal.data.person?.department || undefined),
    [portal.data.person?.department]
  );
  const courses = useResource<CourseOut[]>(coursesLoader, []);

  // State cho biểu mẫu xin nghỉ phép trực tuyến
  const [leaveSessionId, setLeaveSessionId] = useState("");
  const [leaveDate, setLeaveDate] = useState(() => new Date(Date.now() + 7 * 60 * 60 * 1000).toISOString().slice(0, 10));
  const [leaveReason, setLeaveReason] = useState("");
  const [submittingLeave, setSubmittingLeave] = useState(false);

  const handleCreateLeave = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!leaveReason.trim() || submittingLeave) return;
    setSubmittingLeave(true);
    try {
      await academicApi.createLeave(
        {
          session_id: leaveSessionId || undefined,
          leave_date: leaveDate,
          reason: leaveReason.trim(),
        },
        selectedPersonId || portal.data.person?.id || undefined
      );
      setLeaveReason("");
      setLeaveSessionId("");
      toast.success(
        t(
          "Đã gửi đơn xin nghỉ phép cho Giảng viên. Khi được duyệt, buổi học sẽ tự động tính Vắng có phép.",
          "Leave request submitted. Once approved, your session will be marked Excused."
        )
      );
      await myLeaves.reload();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setSubmittingLeave(false);
    }
  };

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
        consent,
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
        <RefreshButton
          onClick={() => {
            void portal.reload();
            void myGrade.reload();
            void transcript.reload();
            void myLeaves.reload();
            void announcements.reload();
            void courses.reload();
          }}
          loading={portal.loading}
        />
      </PageHeader>

      <ErrorNotice message={portal.error} retry={portal.reload} />
      <ErrorNotice message={transcript.error} retry={transcript.reload} />
      <ErrorNotice message={myGrade.error} retry={myGrade.reload} />
      <ErrorNotice message={myLeaves.error} retry={myLeaves.reload} />
      <ErrorNotice message={announcements.error} retry={announcements.reload} />
      <ErrorNotice message={courses.error} retry={courses.reload} />

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

      {role === "student" && !portal.loading && (!person || showReenroll) && (
        <Section
          title={
            person
              ? t("Chụp lại khuôn mặt AI (giữ hồ sơ học vụ)", "Re-capture face (academic profile preserved)")
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
              <label className="checkbox-label"><input type="checkbox" checked={consent} required onChange={(e) => setConsent(e.target.checked)} />{t("Tôi xác nhận có sự đồng ý xử lý mẫu khuôn mặt cho mục đích điểm danh. Có thể yêu cầu quản trị viên xóa mẫu.", "I confirm consent to process face templates for attendance. Template deletion can be requested from an administrator.")}</label>
        <Field id="self-name" label={t("Họ và tên sinh viên *", "Full name *")}>
                <input
                  id="self-name"
                  readOnly={!!person}
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
                  readOnly={!!person}
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
                  readOnly={!!person}
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
                  readOnly={!!person}
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
          action={role === "student" ? (
            <button type="button" className="secondary-button" onClick={openReenrollForm}>
              <Camera size={14} />
              {showReenroll
                ? t("Ẩn khung chụp lại", "Hide re-capture")
                : t("Đăng ký / Chụp lại khuôn mặt", "Enroll / Re-capture face")}
            </button>
          ) : undefined}
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
              <dt>{t("Trạng thái hồ sơ", "Profile status")}</dt>
              <dd className="attendance-status">
                <CheckCircle2 size={13} />
                {t("Đã có hồ sơ sinh viên", "Student profile created")}
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
          <p>{t("có mặt, đi muộn hoặc có phép", "present, late or excused")}</p>
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
              ? t("Chưa có hồ sơ để tính chuyên cần", "Select or link a student profile to view attendance")
              : present_count + absent_count === 0
                ? t("Chưa có buổi được đánh giá", "No assessed sessions yet")
                : is_defaulter
                  ? t("Cảnh báo: Dưới 75% quy định", "Warning: Below 75% requirement")
                  : t("Đủ điều kiện chuyên cần (≥ 75%)", "Meets requirement (≥ 75%)")}
          </p>
        </div>
      </dl>

      {person && <Section title={t("Điểm theo học phần", "Course grades")}><p className="field-hint">{t("GPA theo tín chỉ đã có điểm", "Credit-weighted GPA")}: <strong>{transcript.loading ? "…" : transcript.data.weighted_gpa?.toFixed(2) ?? "–"}</strong> · {transcript.data.credits_graded} {t("tín chỉ", "credits")}</p><Field id="student-grade-course" label={t("Chọn học phần / Học kỳ", "Select course / semester")}><select id="student-grade-course" value={courseId} onChange={(e) => setCourseId(e.target.value)}><option value="">{t("Dữ liệu cũ chưa gắn học phần", "Legacy unassigned grades")}</option>{courses.data.map((c) => <option key={c.id} value={c.id}>{c.code} · {c.name} · {c.semester}</option>)}</select></Field></Section>}
      {person && myGrade.data && (
        <Section
          title={t("Bảng điểm Học vụ & Xét điều kiện dự thi cá nhân", "Personal Academic Gradebook & Exam Eligibility")}
          description={t(
            "Điểm chuyên cần (10%) được hệ thống AI tự động quy đổi từ tỷ lệ điểm danh khuôn mặt. Điểm Giữa kỳ (30%) và Cuối kỳ (60%) do Giảng viên cập nhật.",
            "Attendance score (10%) is automatically computed from AI facial check-ins. Midterm (30%) and Final (60%) scores are updated by your lecturer."
          )}
        >
          <dl className="metric-strip">
            <div>
              <dt>{t("Điểm chuyên cần AI (10%)", "AI Attendance (10%)")}</dt>
              <dd>{myGrade.data.attendance_score.toFixed(1)}</dd>
              <p>{t(`Tỷ lệ đi học: ${myGrade.data.attendance_rate}%`, `Attendance rate: ${myGrade.data.attendance_rate}%`)}</p>
            </div>
            <div>
              <dt>{t("Giữa kỳ (30%) · Cuối kỳ (60%)", "Midterm (30%) · Final (60%)")}</dt>
              <dd>
                {myGrade.data.midterm_score != null ? myGrade.data.midterm_score.toFixed(1) : "–"} /{" "}
                {myGrade.data.final_score != null ? myGrade.data.final_score.toFixed(1) : "–"}
              </dd>
              <p>
                {t(
                  `Điểm cộng thưởng: +${(myGrade.data.bonus_score || 0).toFixed(1)}`,
                  `Bonus score: +${(myGrade.data.bonus_score || 0).toFixed(1)}`
                )}
              </p>
            </div>
            <div>
              <dt>{t("Tổng kết Hệ 10 & Điểm chữ", "Total (10-pt) & Letter Grade")}</dt>
              <dd>
                {myGrade.data.total_10 != null ? `${myGrade.data.total_10.toFixed(2)} (${myGrade.data.letter_grade})` : "–"}
              </dd>
              <p>
                {myGrade.data.gpa_4 != null
                  ? t(`GPA Hệ 4.0: ${myGrade.data.gpa_4.toFixed(2)} / 4.0`, `4.0 GPA: ${myGrade.data.gpa_4.toFixed(2)} / 4.0`)
                  : t("Đang chờ nhập đủ cột điểm", "Awaiting exam scores")}
              </p>
            </div>
            <div>
              <dt>{t("Xét điều kiện dự thi", "Final Exam Eligibility")}</dt>
              <dd className={myGrade.data.exam_eligible ? "attendance-status" : "warning-text"}>
                <Award size={16} />{" "}
                {myGrade.data.exam_eligible
                  ? t("Đủ điều kiện dự thi", "Eligible for Final Exam")
                  : t("Cấm thi (< 75%)", "Ineligible (< 75%)")}
              </dd>
              <p>{myGrade.data.note || t("Chính sách điểm đang cấu hình", "Configured grading policy")}</p>
            </div>
          </dl>
        </Section>
      )}

      {(announcements.data.length > 0 || courses.data.length > 0) && (
        <div className="enrollment-grid">
          <Section
            title={t("Bảng tin & Thông báo Lớp học", "Class & Academic Announcements")}
            description={t("Thông báo mới nhất từ Khoa và Giảng viên phụ trách.", "Latest notices from your department and lecturer.")}
          >
            {announcements.data.length > 0 ? (
              <div className="stack-form">
                {announcements.data.slice(0, 5).map((ann) => (
                  <div
                    key={ann.id}
                    style={{
                      padding: "10px 12px",
                      border: "1px solid var(--ui-border)",
                      borderRadius: 6,
                      background: ann.priority !== "normal" ? "var(--ui-soft)" : undefined,
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center" }}>
                      <strong>
                        <Megaphone size={13} style={{ marginRight: 5, verticalAlign: "-2px" }} />
                        {ann.title}
                      </strong>
                      <span className={ann.priority !== "normal" ? "warning-text" : "muted"} style={{ fontSize: 12 }}>
                        {ann.department || t("Toàn trường", "All classes")} · {dateTime(ann.created_at, lang)}
                      </span>
                    </div>
                    <p style={{ margin: "6px 0 0", fontSize: 13 }}>{ann.content}</p>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState>{t("Chưa có thông báo mới.", "No announcements yet.")}</EmptyState>
            )}
          </Section>

          <Section
            title={t("Học phần & Thời khóa biểu", "Enrolled Courses & Schedule")}
            description={t("Lịch học, phòng học và giảng viên phụ trách.", "Class schedule, room and instructor.")}
          >
            {courses.data.length > 0 ? (
              <Table label={t("Thời khóa biểu học phần", "Course schedule")}>
                <thead>
                  <tr>
                    <th>{t("Mã HP", "Code")}</th>
                    <th>{t("Tên học phần", "Course")}</th>
                    <th>{t("Tín chỉ", "Credits")}</th>
                    <th>{t("Lịch học & Phòng", "Schedule & Room")}</th>
                  </tr>
                </thead>
                <tbody>
                  {courses.data.map((c) => (
                    <tr key={c.id}>
                      <td className="numeric-cell cell-strong">{c.code}</td>
                      <td>
                        <BookOpen size={12} style={{ marginRight: 4 }} />
                        {c.name}
                        {c.lecturer ? <div className="muted" style={{ fontSize: 11 }}>GV: {c.lecturer}</div> : null}
                      </td>
                      <td className="numeric-cell">{c.credits}</td>
                      <td>{[c.schedule, c.room].filter(Boolean).join(" · ") || "–"}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            ) : (
              <EmptyState>{t("Chưa có lịch học học phần.", "No course schedule published yet.")}</EmptyState>
            )}
          </Section>
        </div>
      )}

      {person && (
        <Section
          title={t("Xin nghỉ phép trực tuyến & Theo dõi duyệt đơn", "Online Leave Request & Approval Status")}
          description={t(
            "Gửi đơn xin phép vắng mặt có lý do chính đáng. Khi Giảng viên bấm Duyệt, buổi học tương ứng sẽ tự động chuyển thành 'Vắng có phép' để bảo toàn điểm chuyên cần.",
            "Submit an online leave request. When approved by your lecturer, the linked session is automatically marked Excused."
          )}
        >
          <div className="enrollment-grid">
            <form className="stack-form" onSubmit={handleCreateLeave}>
              <Field id="student-leave-session" label={t("Chọn buổi học xin phép (nếu đã mở phiên)", "Select class session (optional)")}>
                <select
                  id="student-leave-session"
                  value={leaveSessionId}
                  onChange={(e) => setLeaveSessionId(e.target.value)}
                >
                  <option value="">{t("— Xin phép theo ngày (chưa có phiên cụ thể) —", "— Request by date —")}</option>
                  {sessions.map((s) => (
                    <option key={s.session_id} value={s.session_id}>
                      {s.label} ({dateTime(s.started_at, lang)})
                    </option>
                  ))}
                </select>
              </Field>
              <Field id="student-leave-date" label={t("Ngày xin nghỉ phép *", "Leave date *")}>
                <input
                  id="student-leave-date"
                  type="date"
                  value={leaveDate}
                  onChange={(e) => setLeaveDate(e.target.value)}
                  required
                />
              </Field>
              <Field id="student-leave-reason" label={t("Lý do xin nghỉ phép & Minh chứng *", "Reason for leave *")}>
                <input
                  id="student-leave-reason"
                  value={leaveReason}
                  onChange={(e) => setLeaveReason(e.target.value)}
                  placeholder={t("VD: Khám bệnh tại BV / Công tác Đoàn trường…", "e.g. Medical appointment / University event…")}
                  minLength={3}
                  maxLength={500}
                  required
                />
              </Field>
              <button type="submit" className="primary-button" disabled={submittingLeave || !leaveReason.trim()}>
                <Send size={14} />
                {submittingLeave ? t("Đang gửi đơn…", "Submitting…") : t("Gửi đơn xin nghỉ phép", "Submit leave request")}
              </button>
            </form>

            <div>
              <Table label={t("Lịch sử đơn xin nghỉ phép", "Leave request history")}>
                <thead>
                  <tr>
                    <th>{t("Ngày / Buổi học", "Date / Session")}</th>
                    <th>{t("Lý do", "Reason")}</th>
                    <th>{t("Trạng thái duyệt", "Status")}</th>
                    <th>{t("Phản hồi GV", "Note")}</th>
                  </tr>
                </thead>
                <tbody>
                  {myLeaves.data.map((lv) => (
                    <tr key={lv.id}>
                      <td>
                        <div className="cell-strong">{lv.leave_date}</div>
                        {lv.session_label && <small className="muted">{lv.session_label}</small>}
                      </td>
                      <td>{lv.reason}</td>
                      <td>
                        {lv.status === "approved" ? (
                          <span className="attendance-status">
                            <FileCheck2 size={12} /> {t("Đã duyệt (Có phép)", "Approved (Excused)")}
                          </span>
                        ) : lv.status === "rejected" ? (
                          <span className="warning-text">{t("Từ chối", "Rejected")}</span>
                        ) : (
                          <span className="session-status">
                            <span className="status-dot" /> {t("Đang chờ duyệt", "Pending")}
                          </span>
                        )}
                      </td>
                      <td>{lv.reviewer_note || "–"}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              {!myLeaves.data.length && (
                <EmptyState loading={myLeaves.loading}>
                  {t("Bạn chưa gửi đơn xin nghỉ phép nào.", "You haven't submitted any leave requests yet.")}
                </EmptyState>
              )}
            </div>
          </div>
        </Section>
      )}

      <Section
        title={t("Chi tiết điểm danh theo từng buổi học", "Session-by-session attendance log")}
        description={t(
          "Lịch sử các buổi học thuộc hồ sơ. Tỷ lệ chuyên cần tính trên các buổi đã đánh giá, theo ngày bắt đầu buổi học.",
          "Shows the profile’s session history. Attendance totals include assessed sessions, grouped by session start date."
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
              <th className="align-right">{t("Tương đồng cosine", "Cosine similarity")}</th>
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
                  {session.confidence != null ? session.confidence.toFixed(3) : "–"}
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
