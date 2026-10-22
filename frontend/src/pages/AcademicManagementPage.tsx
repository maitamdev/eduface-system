import React, { useCallback, useState } from "react";
import {
  BookOpen,
  CheckCircle2,
  Download,
  FileSpreadsheet,
  FileText,
  Megaphone,
  Plus,
  Save,
  Trash2,
  XCircle,
} from "lucide-react";
import {
  academicApi,
  personsApi,
  type AnnouncementOut,
  type CourseOut,
  type LeaveRequestOut,
  type StudentGradeRow,
} from "@/api/client";
import { useLanguage } from "@/context/LanguageContext";
import { useToast } from "@/context/ToastContext";
import { useResource } from "@/hooks/useResource";
import { dateTime, errorMessage, matchesSearch } from "@/lib/format";
import {
  EmptyState,
  ErrorNotice,
  Field,
  PageHeader,
  RefreshButton,
  SearchField,
  Section,
  Table,
} from "@/components/ProductUI";

type TabKey = "grades" | "leaves" | "courses" | "announcements" | "import";

export const AcademicManagementPage: React.FC = () => {
  const { t, lang } = useLanguage();
  const toast = useToast();
  const [activeTab, setActiveTab] = useState<TabKey>("grades");
  const [departmentFilter, setDepartmentFilter] = useState("");
  const [search, setSearch] = useState("");

  const peopleLoader = useCallback(() => personsApi.list(), []);
  const people = useResource(peopleLoader, []);

  const gradesLoader = useCallback(
    () => academicApi.listGrades(departmentFilter || undefined),
    [departmentFilter]
  );
  const grades = useResource<StudentGradeRow[]>(gradesLoader, []);

  const leavesLoader = useCallback(
    () => academicApi.listLeaves({ department: departmentFilter || undefined }),
    [departmentFilter]
  );
  const leaves = useResource<LeaveRequestOut[]>(leavesLoader, []);

  const coursesLoader = useCallback(
    () => academicApi.listCourses(departmentFilter || undefined),
    [departmentFilter]
  );
  const courses = useResource<CourseOut[]>(coursesLoader, []);

  const announcementsLoader = useCallback(
    () => academicApi.listAnnouncements(departmentFilter || undefined),
    [departmentFilter]
  );
  const announcements = useResource<AnnouncementOut[]>(announcementsLoader, []);

  // State chỉnh sửa điểm từng dòng
  const [gradeDrafts, setGradeDrafts] = useState<
    Record<string, { midterm: string; final: string; bonus: string }>
  >({});
  const [savingGradeId, setSavingGradeId] = useState<string | null>(null);

  // State tạo Học phần
  const [courseCode, setCourseCode] = useState("");
  const [courseName, setCourseName] = useState("");
  const [courseDept, setCourseDept] = useState("");
  const [courseCredits, setCourseCredits] = useState(3);
  const [courseLecturer, setCourseLecturer] = useState("");
  const [courseSchedule, setCourseSchedule] = useState("");
  const [courseRoom, setCourseRoom] = useState("");
  const [courseSemester, setCourseSemester] = useState("HK1 2026-2027");
  const [creatingCourse, setCreatingCourse] = useState(false);

  // State tạo Thông báo
  const [annTitle, setAnnTitle] = useState("");
  const [annContent, setAnnContent] = useState("");
  const [annDept, setAnnDept] = useState("");
  const [annPriority, setAnnPriority] = useState<"normal" | "important" | "exam">("normal");
  const [creatingAnn, setCreatingAnn] = useState(false);

  // State nhập danh sách sinh viên hàng loạt
  const [csvText, setCsvText] = useState(
    "2305CT2070, Mai Trần Thiên Tâm, KTCN, tam@dhv.edu.vn, 0901234567, Nam, K23, Công nghệ Thông tin\n2305CT2071, Nguyễn Văn An, KTCN, an@dhv.edu.vn, 0902345678, Nam, K23, Công nghệ Thông tin"
  );
  const [createAccounts, setCreateAccounts] = useState(true);
  const [defaultPw, setDefaultPw] = useState("123456");
  const [importing, setImporting] = useState(false);

  const departments = [
    ...new Set(
      [
        ...people.data.map((p) => p.department),
        ...courses.data.map((c) => c.department),
      ].filter((item): item is string => !!item && item.trim().length > 0)
    ),
  ].sort();

  const reloadAll = () => {
    void grades.reload();
    void leaves.reload();
    void courses.reload();
    void announcements.reload();
    void people.reload();
  };

  const getDraft = (row: StudentGradeRow) => {
    return (
      gradeDrafts[row.person_id] || {
        midterm: row.midterm_score != null ? String(row.midterm_score) : "",
        final: row.final_score != null ? String(row.final_score) : "",
        bonus: row.bonus_score != null ? String(row.bonus_score) : "0",
      }
    );
  };

  const updateDraft = (
    personId: string,
    row: StudentGradeRow,
    field: "midterm" | "final" | "bonus",
    value: string
  ) => {
    const current = getDraft(row);
    setGradeDrafts((prev) => ({
      ...prev,
      [personId]: { ...current, [field]: value },
    }));
  };

  const handleSaveGrade = async (row: StudentGradeRow) => {
    const draft = getDraft(row);
    const midterm = draft.midterm.trim() === "" ? null : Number(draft.midterm);
    const final = draft.final.trim() === "" ? null : Number(draft.final);
    const bonus = draft.bonus.trim() === "" ? 0 : Number(draft.bonus);

    if (
      (midterm !== null && (isNaN(midterm) || midterm < 0 || midterm > 10)) ||
      (final !== null && (isNaN(final) || final < 0 || final > 10)) ||
      isNaN(bonus) ||
      bonus < 0 ||
      bonus > 2
    ) {
      toast.error(t("Điểm số phải từ 0 đến 10 (điểm cộng tối đa 2.0).", "Scores must be 0–10 (bonus max 2.0)."));
      return;
    }

    setSavingGradeId(row.person_id);
    try {
      const updated = await academicApi.upsertGrade({
        person_id: row.person_id,
        midterm_score: midterm,
        final_score: final,
        bonus_score: bonus,
      });
      grades.setData((prev) =>
        prev.map((item) => (item.person_id === updated.person_id ? updated : item))
      );
      toast.success(t(`Đã lưu bảng điểm cho ${row.name}.`, `Saved grade for ${row.name}.`));
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setSavingGradeId(null);
    }
  };

  const exportGradesCsv = () => {
    const header = [
      "Họ và tên",
      "MSSV",
      "Lớp / Khoa",
      "Số buổi có mặt",
      "Tổng số buổi",
      "Chuyên cần (%)",
      "Điểm chuyên cần (10%)",
      "Điểm giữa kỳ (30%)",
      "Điểm cuối kỳ (60%)",
      "Điểm cộng",
      "Tổng kết (Hệ 10)",
      "GPA (Hệ 4)",
      "Điểm chữ",
      "Điều kiện dự thi",
    ];
    const rows = [header.join(",")];
    filteredGrades.forEach((g) => {
      rows.push(
        [
          `"${(g.name || "").replace(/"/g, '""')}"`,
          `"${(g.student_id || "").replace(/"/g, '""')}"`,
          `"${(g.department || "").replace(/"/g, '""')}"`,
          g.present_count,
          g.total_sessions,
          `${g.attendance_rate}%`,
          g.attendance_score,
          g.midterm_score ?? "",
          g.final_score ?? "",
          g.bonus_score ?? 0,
          g.total_10 ?? "",
          g.gpa_4 ?? "",
          g.letter_grade ?? "",
          `"${g.exam_eligible ? "Đủ điều kiện" : "Cấm thi (< 75%)"}"`,
        ].join(",")
      );
    });
    const blob = new Blob(["\uFEFF" + rows.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `bang-diem-hoc-vu-${departmentFilter || "tat-ca"}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleReviewLeave = async (leaveId: string, status: "approved" | "rejected") => {
    try {
      const updated = await academicApi.reviewLeave(leaveId, {
        status,
        reviewer_note:
          status === "approved"
            ? "Giảng viên đã duyệt đơn & cập nhật Vắng có phép."
            : "Không đủ điều kiện nghỉ phép.",
      });
      leaves.setData((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      toast.success(
        status === "approved"
          ? t("Đã duyệt đơn xin phép và đồng bộ trạng thái Vắng có phép!", "Leave approved & attendance marked Excused!")
          : t("Đã từ chối đơn xin phép.", "Leave request rejected.")
      );
    } catch (err) {
      toast.error(errorMessage(err));
    }
  };

  const handleCreateCourse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!courseCode.trim() || !courseName.trim() || !courseDept.trim() || creatingCourse) return;
    setCreatingCourse(true);
    try {
      const created = await academicApi.createCourse({
        code: courseCode.trim().toUpperCase(),
        name: courseName.trim(),
        department: courseDept.trim(),
        credits: courseCredits,
        lecturer: courseLecturer.trim() || undefined,
        schedule: courseSchedule.trim() || undefined,
        room: courseRoom.trim() || undefined,
        semester: courseSemester.trim() || undefined,
      });
      courses.setData((prev) => [created, ...prev]);
      setCourseCode("");
      setCourseName("");
      setCourseSchedule("");
      setCourseRoom("");
      toast.success(t("Đã thêm học phần mới.", "Course created."));
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setCreatingCourse(false);
    }
  };

  const handleDeleteCourse = async (id: string) => {
    try {
      await academicApi.deleteCourse(id);
      courses.setData((prev) => prev.filter((c) => c.id !== id));
      toast.success(t("Đã xóa học phần.", "Course removed."));
    } catch (err) {
      toast.error(errorMessage(err));
    }
  };

  const handleCreateAnnouncement = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!annTitle.trim() || !annContent.trim() || creatingAnn) return;
    setCreatingAnn(true);
    try {
      const created = await academicApi.createAnnouncement({
        title: annTitle.trim(),
        content: annContent.trim(),
        department: annDept.trim() || undefined,
        priority: annPriority,
      });
      announcements.setData((prev) => [created, ...prev]);
      setAnnTitle("");
      setAnnContent("");
      toast.success(t("Đã đăng thông báo học vụ lên Cổng sinh viên.", "Announcement published."));
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setCreatingAnn(false);
    }
  };

  const handleDeleteAnnouncement = async (id: string) => {
    try {
      await academicApi.deleteAnnouncement(id);
      announcements.setData((prev) => prev.filter((a) => a.id !== id));
      toast.success(t("Đã xóa thông báo.", "Announcement deleted."));
    } catch (err) {
      toast.error(errorMessage(err));
    }
  };

  const handleBulkImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!csvText.trim() || importing) return;
    const lines = csvText
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter((l) => l.length > 0);

    const parsed = lines
      .map((line) => {
        const parts = line.split(",").map((p) => p.trim());
        if (parts.length < 3) return null;
        if (parts[0].toLowerCase() === "mssv" || parts[0].toLowerCase() === "student_id") return null;
        return {
          student_id: parts[0],
          name: parts[1],
          department: parts[2],
          email: parts[3] || undefined,
          phone: parts[4] || undefined,
          gender: parts[5] || undefined,
          cohort: parts[6] || undefined,
          major: parts[7] || undefined,
        };
      })
      .filter((item): item is NonNullable<typeof item> => item !== null);

    if (!parsed.length) {
      toast.error(
        t(
          "Không tìm thấy dòng hợp lệ. Định dạng: MSSV, Họ tên, Lớp, Email, SĐT, Giới tính, Khóa, Ngành",
          "No valid rows found. Format: StudentID, Name, Class, Email, Phone, Gender, Cohort, Major"
        )
      );
      return;
    }

    setImporting(true);
    try {
      const res = await academicApi.importStudents({
        students: parsed,
        create_login_accounts: createAccounts,
        default_password: defaultPw.trim() || "123456",
      });
      toast.success(
        t(
          `Nhập thành công ${res.total_processed} SV (Tạo mới: ${res.created}, Cập nhật: ${res.updated}, Cấp TK đăng nhập: ${res.accounts_created})!`,
          `Processed ${res.total_processed} students (${res.created} created, ${res.updated} updated, ${res.accounts_created} logins)!`
        )
      );
      reloadAll();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setImporting(false);
    }
  };

  const filteredGrades = grades.data.filter((row) =>
    matchesSearch(search, row.name, row.student_id, row.department, row.letter_grade)
  );
  const pendingLeavesCount = leaves.data.filter((l) => l.status === "pending").length;
  const ineligibleCount = grades.data.filter((g) => !g.exam_eligible).length;
  const gradedRows = grades.data.filter((g) => g.gpa_4 != null);
  const avgGpa =
    gradedRows.length > 0
      ? (gradedRows.reduce((acc, r) => acc + (r.gpa_4 || 0), 0) / gradedRows.length).toFixed(2)
      : "–";

  return (
    <div className="product-page">
      <PageHeader
        title={t("Quản trị Học vụ & Sinh viên", "Academic & Student Management")}
        description={t(
          "Quản lý bảng điểm học phần, tự động quy đổi điểm chuyên cần AI, xét điều kiện dự thi, duyệt đơn xin phép và quản lý thông báo lớp học.",
          "Manage course grades, automated AI attendance scoring, exam eligibility, leave approvals and class announcements."
        )}
      >
        <select
          aria-label={t("Lọc theo Lớp / Khoa", "Filter by class")}
          value={departmentFilter}
          onChange={(e) => setDepartmentFilter(e.target.value)}
          style={{ minWidth: 165 }}
        >
          <option value="">{t("Tất cả các lớp", "All classes")}</option>
          {departments.map((cls) => (
            <option key={cls} value={cls}>
              {t(`Lớp: ${cls}`, `Class: ${cls}`)}
            </option>
          ))}
        </select>
        <RefreshButton
          onClick={reloadAll}
          loading={grades.loading || leaves.loading || courses.loading}
        />
      </PageHeader>

      <dl className="metric-strip">
        <div>
          <dt>{t("Tổng số sinh viên", "Total students")}</dt>
          <dd>{grades.loading ? "…" : grades.data.length}</dd>
          <p>{t("đang theo dõi học vụ", "active academic profiles")}</p>
        </div>
        <div>
          <dt>{t("GPA trung bình (Hệ 4)", "Average GPA (4.0)")}</dt>
          <dd>{avgGpa}</dd>
          <p>{t(`trên ${gradedRows.length} SV đã nhập điểm`, `across ${gradedRows.length} graded students`)}</p>
        </div>
        <div>
          <dt>{t("Đơn xin phép chờ duyệt", "Pending leave requests")}</dt>
          <dd className={pendingLeavesCount > 0 ? "warning-text" : ""}>{pendingLeavesCount}</dd>
          <p>{t("tự động đồng bộ Vắng có phép", "auto-syncs Excused status")}</p>
        </div>
        <div>
          <dt>{t("Cảnh báo Cấm thi (< 75%)", "Exam ineligible (< 75%)")}</dt>
          <dd className={ineligibleCount > 0 ? "warning-text" : "attendance-status"}>
            {ineligibleCount}
          </dd>
          <p>{t("sinh viên không đủ chuyên cần", "below attendance threshold")}</p>
        </div>
      </dl>

      <div className="source-tabs" aria-label={t("Phân hệ quản trị sinh viên", "Academic modules")}>
        <button
          type="button"
          aria-pressed={activeTab === "grades"}
          onClick={() => setActiveTab("grades")}
        >
          <FileSpreadsheet size={14} />
          {t("Bảng điểm & Xét dự thi", "Grades & GPA")} ({grades.data.length})
        </button>
        <button
          type="button"
          aria-pressed={activeTab === "leaves"}
          onClick={() => setActiveTab("leaves")}
        >
          <FileText size={14} />
          {t("Đơn xin nghỉ phép", "Leave Requests")}{" "}
          {pendingLeavesCount > 0 ? `(${pendingLeavesCount} mới)` : `(${leaves.data.length})`}
        </button>
        <button
          type="button"
          aria-pressed={activeTab === "courses"}
          onClick={() => setActiveTab("courses")}
        >
          <BookOpen size={14} />
          {t("Học phần & Lịch học", "Courses & Schedule")} ({courses.data.length})
        </button>
        <button
          type="button"
          aria-pressed={activeTab === "announcements"}
          onClick={() => setActiveTab("announcements")}
        >
          <Megaphone size={14} />
          {t("Thông báo lớp học", "Announcements")} ({announcements.data.length})
        </button>
        <button
          type="button"
          aria-pressed={activeTab === "import"}
          onClick={() => setActiveTab("import")}
        >
          <Plus size={14} />
          {t("Nhập danh sách SV (CSV)", "Bulk Import CSV")}
        </button>
      </div>

      {activeTab === "grades" && (
        <Section
          title={t(
            "Bảng điểm Học phần & Quy đổi Điểm Chuyên cần AI tự động",
            "Course Gradebook & Automated AI Attendance Scoring"
          )}
          description={t(
            "Công thức tính tự động: Điểm tổng kết (Hệ 10) = 10% Điểm chuyên cần AI + 30% Giữa kỳ + 60% Cuối kỳ + Điểm cộng. Sinh viên dưới 75% chuyên cần sẽ bị đánh dấu Cấm thi.",
            "Formula: Total (10) = 10% AI Attendance + 30% Midterm + 60% Final + Bonus. Students under 75% attendance are marked Exam Ineligible."
          )}
          action={
            <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
              <SearchField
                label={t("Tìm tên, MSSV hoặc lớp…", "Search name, ID or class…")}
                value={search}
                onChange={setSearch}
              />
              <button
                type="button"
                className="secondary-button"
                disabled={!filteredGrades.length}
                onClick={exportGradesCsv}
              >
                <Download size={14} />
                {t("Xuất bảng điểm (CSV)", "Export grades (CSV)")}
              </button>
            </div>
          }
        >
          <ErrorNotice message={grades.error} retry={grades.reload} />
          <Table label={t("Bảng điểm sinh viên", "Student gradebook")}>
            <thead>
              <tr>
                <th>{t("Sinh viên", "Student")}</th>
                <th>MSSV</th>
                <th>{t("Lớp", "Class")}</th>
                <th className="align-right">{t("Chuyên cần AI", "AI Attendance")}</th>
                <th className="align-right">{t("Điểm CC (10%)", "Att. Score")}</th>
                <th>{t("Giữa kỳ (30%)", "Midterm (30%)")}</th>
                <th>{t("Cuối kỳ (60%)", "Final (60%)")}</th>
                <th>{t("Điểm +", "Bonus")}</th>
                <th className="align-right">{t("Tổng (10)", "Total (10)")}</th>
                <th className="align-right">GPA (4)</th>
                <th>{t("Chữ", "Grade")}</th>
                <th>{t("Điều kiện thi", "Exam Status")}</th>
                <th className="align-right">{t("Lưu", "Save")}</th>
              </tr>
            </thead>
            <tbody>
              {filteredGrades.map((row) => {
                const draft = getDraft(row);
                return (
                  <tr key={row.person_id}>
                    <td className="cell-strong">{row.name}</td>
                    <td className="numeric-cell">{row.student_id || "–"}</td>
                    <td>{row.department || "–"}</td>
                    <td className="align-right numeric-cell">
                      {row.present_count}/{row.total_sessions} ({row.attendance_rate}%)
                    </td>
                    <td className="align-right numeric-cell cell-strong">
                      {row.attendance_score.toFixed(1)}
                    </td>
                    <td>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="10"
                        value={draft.midterm}
                        onChange={(e) =>
                          updateDraft(row.person_id, row, "midterm", e.target.value)
                        }
                        placeholder="0–10"
                        style={{ width: 68, padding: "4px 6px", fontSize: 12 }}
                      />
                    </td>
                    <td>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="10"
                        value={draft.final}
                        onChange={(e) => updateDraft(row.person_id, row, "final", e.target.value)}
                        placeholder="0–10"
                        style={{ width: 68, padding: "4px 6px", fontSize: 12 }}
                      />
                    </td>
                    <td>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="2"
                        value={draft.bonus}
                        onChange={(e) => updateDraft(row.person_id, row, "bonus", e.target.value)}
                        style={{ width: 56, padding: "4px 6px", fontSize: 12 }}
                      />
                    </td>
                    <td className="align-right numeric-cell cell-strong">
                      {row.total_10 != null ? row.total_10.toFixed(2) : "–"}
                    </td>
                    <td className="align-right numeric-cell">
                      {row.gpa_4 != null ? row.gpa_4.toFixed(1) : "–"}
                    </td>
                    <td>
                      <strong
                        className={
                          row.letter_grade === "F"
                            ? "warning-text"
                            : row.letter_grade
                              ? "attendance-status"
                              : "muted"
                        }
                      >
                        {row.letter_grade || "–"}
                      </strong>
                    </td>
                    <td>
                      <span className={row.exam_eligible ? "attendance-status" : "warning-text"}>
                        {row.exam_eligible ? t("Đủ ĐK thi", "Eligible") : t("Cấm thi", "Ineligible")}
                      </span>
                    </td>
                    <td className="align-right">
                      <button
                        type="button"
                        className="secondary-button"
                        disabled={savingGradeId === row.person_id}
                        onClick={() => void handleSaveGrade(row)}
                        style={{ padding: "4px 10px", fontSize: 11 }}
                      >
                        <Save size={12} />
                        {savingGradeId === row.person_id ? "…" : t("Lưu", "Save")}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
          {!filteredGrades.length && (
            <EmptyState loading={grades.loading}>
              {t("Chưa có sinh viên nào trong danh sách.", "No students found.")}
            </EmptyState>
          )}
        </Section>
      )}

      {activeTab === "leaves" && (
        <Section
          title={t("Quản lý & Phê duyệt Đơn xin nghỉ phép", "Student Leave Requests & Approvals")}
          description={t(
            "Khi Giảng viên bấm 'Duyệt', nếu đơn gắn với một buổi điểm danh cụ thể, hệ thống sẽ tự động chuyển trạng thái sinh viên trong buổi đó sang 'Vắng có phép (Excused)'.",
            "Approving a leave request linked to a session automatically marks the student as Excused for that session."
          )}
        >
          <ErrorNotice message={leaves.error} retry={leaves.reload} />
          <Table label={t("Danh sách đơn xin phép", "Leave requests")}>
            <thead>
              <tr>
                <th>{t("Sinh viên", "Student")}</th>
                <th>MSSV</th>
                <th>{t("Lớp", "Class")}</th>
                <th>{t("Ngày / Buổi xin nghỉ", "Date / Session")}</th>
                <th>{t("Lý do xin phép", "Reason")}</th>
                <th>{t("Trạng thái", "Status")}</th>
                <th className="align-right">{t("Phê duyệt", "Action")}</th>
              </tr>
            </thead>
            <tbody>
              {leaves.data.map((leave) => (
                <tr key={leave.id}>
                  <td className="cell-strong">{leave.person_name}</td>
                  <td className="numeric-cell">{leave.student_id || "–"}</td>
                  <td>{leave.department || "–"}</td>
                  <td>
                    <div>{leave.leave_date}</div>
                    {leave.session_label && <small className="muted">{leave.session_label}</small>}
                  </td>
                  <td>
                    <div>{leave.reason}</div>
                    {leave.evidence_url && (
                      <a
                        href={leave.evidence_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-link"
                        style={{ fontSize: 11 }}
                      >
                        {t("Xem minh chứng", "View evidence")}
                      </a>
                    )}
                  </td>
                  <td>
                    <span
                      className={
                        leave.status === "approved"
                          ? "attendance-status"
                          : leave.status === "rejected"
                            ? "warning-text"
                            : "muted"
                      }
                    >
                      {leave.status === "approved"
                        ? t("✓ Đã duyệt (Có phép)", "✓ Approved")
                        : leave.status === "rejected"
                          ? t("× Từ chối", "× Rejected")
                          : t("⏳ Chờ duyệt", "⏳ Pending")}
                    </span>
                  </td>
                  <td className="align-right">
                    <div className="row-actions">
                      <button
                        type="button"
                        className="text-button attendance-status"
                        onClick={() => void handleReviewLeave(leave.id, "approved")}
                      >
                        <CheckCircle2 size={13} /> {t("Duyệt", "Approve")}
                      </button>
                      <button
                        type="button"
                        className="text-button danger-text"
                        onClick={() => void handleReviewLeave(leave.id, "rejected")}
                      >
                        <XCircle size={13} /> {t("Từ chối", "Reject")}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
          {!leaves.data.length && (
            <EmptyState loading={leaves.loading}>
              {t("Chưa có đơn xin nghỉ phép nào.", "No leave requests submitted yet.")}
            </EmptyState>
          )}
        </Section>
      )}

      {activeTab === "courses" && (
        <>
          <Section
            title={t("Thêm Học phần & Lịch giảng dạy mới", "Add Course & Class Schedule")}
            description={t(
              "Khai báo mã học phần, số tín chỉ, giảng viên phụ trách, lịch học và phòng học cho từng lớp.",
              "Register course code, credits, lecturer, weekly schedule and classroom."
            )}
          >
            <form onSubmit={handleCreateCourse} className="enrollment-grid">
              <div className="stack-form">
                <Field id="course-code" label={t("Mã học phần *", "Course code *")}>
                  <input
                    id="course-code"
                    value={courseCode}
                    onChange={(e) => setCourseCode(e.target.value)}
                    placeholder="VD: IT3040"
                    required
                  />
                </Field>
                <Field id="course-name" label={t("Tên môn học / Học phần *", "Course title *")}>
                  <input
                    id="course-name"
                    value={courseName}
                    onChange={(e) => setCourseName(e.target.value)}
                    placeholder="VD: Trí tuệ Nhân tạo & Thị giác Máy tính"
                    required
                  />
                </Field>
                <Field id="course-dept" label={t("Lớp áp dụng *", "Target class *")}>
                  <input
                    id="course-dept"
                    list="academic-dept-list"
                    value={courseDept}
                    onChange={(e) => setCourseDept(e.target.value)}
                    placeholder="VD: KTCN"
                    required
                  />
                  <datalist id="academic-dept-list">
                    {departments.map((d) => (
                      <option key={d} value={d} />
                    ))}
                  </datalist>
                </Field>
                <Field id="course-credits" label={t("Số tín chỉ", "Credits")}>
                  <input
                    id="course-credits"
                    type="number"
                    min={1}
                    max={10}
                    value={courseCredits}
                    onChange={(e) => setCourseCredits(Number(e.target.value))}
                  />
                </Field>
              </div>
              <div className="stack-form">
                <Field id="course-lecturer" label={t("Giảng viên phụ trách", "Lecturer")}>
                  <input
                    id="course-lecturer"
                    value={courseLecturer}
                    onChange={(e) => setCourseLecturer(e.target.value)}
                    placeholder="VD: ThS. Mai Trần Thiên Tâm"
                  />
                </Field>
                <Field id="course-schedule" label={t("Thời khóa biểu / Ca học", "Schedule")}>
                  <input
                    id="course-schedule"
                    value={courseSchedule}
                    onChange={(e) => setCourseSchedule(e.target.value)}
                    placeholder="VD: Thứ 5 · Tiết 1–3 (07:30 – 10:00)"
                  />
                </Field>
                <Field id="course-room" label={t("Phòng học", "Room")}>
                  <input
                    id="course-room"
                    value={courseRoom}
                    onChange={(e) => setCourseRoom(e.target.value)}
                    placeholder="VD: Phòng Lab A302"
                  />
                </Field>
                <Field id="course-sem" label={t("Học kỳ", "Semester")}>
                  <input
                    id="course-sem"
                    value={courseSemester}
                    onChange={(e) => setCourseSemester(e.target.value)}
                  />
                </Field>
                <button type="submit" className="primary-button" disabled={creatingCourse}>
                  <Plus size={14} />
                  {creatingCourse ? t("Đang lưu…", "Saving…") : t("Thêm học phần", "Add course")}
                </button>
              </div>
            </form>
          </Section>

          <Section title={t("Danh mục Học phần & Thời khóa biểu", "Course Catalog & Schedule")}>
            <Table label={t("Danh sách học phần", "Courses")}>
              <thead>
                <tr>
                  <th>{t("Mã HP", "Code")}</th>
                  <th>{t("Tên học phần", "Course name")}</th>
                  <th>{t("Lớp", "Class")}</th>
                  <th>{t("Tín chỉ", "Credits")}</th>
                  <th>{t("Giảng viên", "Lecturer")}</th>
                  <th>{t("Lịch học & Phòng", "Schedule & Room")}</th>
                  <th>{t("Học kỳ", "Semester")}</th>
                  <th className="align-right">{t("Xóa", "Delete")}</th>
                </tr>
              </thead>
              <tbody>
                {courses.data.map((c) => (
                  <tr key={c.id}>
                    <td className="numeric-cell cell-strong">{c.code}</td>
                    <td className="cell-strong">{c.name}</td>
                    <td>{c.department}</td>
                    <td className="numeric-cell">{c.credits} TC</td>
                    <td>{c.lecturer || "–"}</td>
                    <td>
                      {[c.schedule, c.room].filter(Boolean).join(" · ") || "–"}
                    </td>
                    <td>{c.semester || "–"}</td>
                    <td className="align-right">
                      <button
                        type="button"
                        className="icon-button danger-text"
                        onClick={() => void handleDeleteCourse(c.id)}
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
            {!courses.data.length && (
              <EmptyState loading={courses.loading}>
                {t("Chưa có học phần nào được tạo.", "No courses created yet.")}
              </EmptyState>
            )}
          </Section>
        </>
      )}

      {activeTab === "announcements" && (
        <>
          <Section
            title={t("Đăng Thông báo Học vụ / Lớp học", "Post Class & Academic Announcement")}
            description={t(
              "Thông báo sẽ xuất hiện ngay lập tức trên Cổng thông tin Sinh viên của lớp tương ứng.",
              "Announcements appear immediately on the Student Portal for the target class."
            )}
          >
            <form onSubmit={handleCreateAnnouncement} className="stack-form">
              <div className="scanner-setup">
                <Field id="ann-title" label={t("Tiêu đề thông báo *", "Announcement title *")}>
                  <input
                    id="ann-title"
                    value={annTitle}
                    onChange={(e) => setAnnTitle(e.target.value)}
                    placeholder={t("VD: Lịch thi cuối kỳ & Quy định điểm chuyên cần", "e.g. Final exam schedule")}
                    required
                  />
                </Field>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                  <Field id="ann-dept" label={t("Lớp nhận (Để trống = Toàn trường)", "Target class (Blank = All)")}>
                    <input
                      id="ann-dept"
                      list="academic-dept-list"
                      value={annDept}
                      onChange={(e) => setAnnDept(e.target.value)}
                      placeholder="VD: KTCN"
                    />
                  </Field>
                  <Field id="ann-priority" label={t("Mức độ", "Priority")}>
                    <select
                      id="ann-priority"
                      value={annPriority}
                      onChange={(e) =>
                        setAnnPriority(e.target.value as "normal" | "important" | "exam")
                      }
                    >
                      <option value="normal">{t("Thông báo thường", "Normal")}</option>
                      <option value="important">{t("Quan trọng", "Important")}</option>
                      <option value="exam">{t("Lịch thi / Kiểm tra", "Exam / Assessment")}</option>
                    </select>
                  </Field>
                </div>
              </div>
              <Field id="ann-content" label={t("Nội dung chi tiết *", "Content *")}>
                <textarea
                  id="ann-content"
                  rows={3}
                  value={annContent}
                  onChange={(e) => setAnnContent(e.target.value)}
                  placeholder={t(
                    "Nhập nội dung thông báo gửi tới sinh viên…",
                    "Enter announcement details for students…"
                  )}
                  style={{
                    width: "100%",
                    padding: 10,
                    background: "var(--ui-surface)",
                    color: "var(--ui-text)",
                    border: "1px solid var(--ui-border)",
                    borderRadius: 4,
                    fontFamily: "inherit",
                  }}
                  required
                />
              </Field>
              <div>
                <button type="submit" className="primary-button" disabled={creatingAnn}>
                  <Megaphone size={14} />
                  {creatingAnn ? t("Đang đăng…", "Posting…") : t("Đăng thông báo", "Publish announcement")}
                </button>
              </div>
            </form>
          </Section>

          <Section title={t("Các thông báo đã đăng", "Published Announcements")}>
            <Table label={t("Danh sách thông báo", "Announcements")}>
              <thead>
                <tr>
                  <th>{t("Mức độ", "Type")}</th>
                  <th>{t("Tiêu đề & Nội dung", "Title & Content")}</th>
                  <th>{t("Phạm vi", "Scope")}</th>
                  <th>{t("Người đăng", "Author")}</th>
                  <th>{t("Thời gian", "Posted at")}</th>
                  <th className="align-right">{t("Xóa", "Delete")}</th>
                </tr>
              </thead>
              <tbody>
                {announcements.data.map((a) => (
                  <tr key={a.id}>
                    <td>
                      <span
                        className={
                          a.priority === "exam" || a.priority === "important"
                            ? "warning-text"
                            : "attendance-status"
                        }
                      >
                        {a.priority === "exam"
                          ? t("Lịch thi", "Exam")
                          : a.priority === "important"
                            ? t("Quan trọng", "Important")
                            : t("Thông tin", "Info")}
                      </span>
                    </td>
                    <td>
                      <strong className="cell-strong">{a.title}</strong>
                      <p className="muted" style={{ marginTop: 3 }}>
                        {a.content}
                      </p>
                    </td>
                    <td>{a.department || t("Toàn trường", "All classes")}</td>
                    <td>{a.author}</td>
                    <td className="numeric-cell">{dateTime(a.created_at, lang)}</td>
                    <td className="align-right">
                      <button
                        type="button"
                        className="icon-button danger-text"
                        onClick={() => void handleDeleteAnnouncement(a.id)}
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
            {!announcements.data.length && (
              <EmptyState loading={announcements.loading}>
                {t("Chưa có thông báo học vụ nào.", "No announcements yet.")}
              </EmptyState>
            )}
          </Section>
        </>
      )}

      {activeTab === "import" && (
        <Section
          title={t(
            "Nhập danh sách Sinh viên hàng loạt & Tự động cấp Tài khoản (CSV)",
            "Bulk Student Roster Import & Account Provisioning (CSV)"
          )}
          description={t(
            "Mỗi dòng 1 sinh viên theo định dạng: MSSV, Họ và tên, Lớp, Email, SĐT, Giới tính, Khóa, Ngành. Sinh viên sau khi được tạo tài khoản có thể đăng nhập vào Cổng Sinh viên để tự chụp khuôn mặt AI.",
            "One student per line: StudentID, Full Name, Class, Email, Phone, Gender, Cohort, Major."
          )}
        >
          <form onSubmit={handleBulkImport} className="stack-form">
            <Field
              id="bulk-csv-text"
              label={t(
                "Dữ liệu CSV (MSSV, Họ và tên, Lớp, Email, SĐT, Giới tính, Khóa, Ngành)",
                "CSV Lines (StudentID, Name, Class, Email, Phone, Gender, Cohort, Major)"
              )}
            >
              <textarea
                id="bulk-csv-text"
                rows={8}
                value={csvText}
                onChange={(e) => setCsvText(e.target.value)}
                style={{
                  width: "100%",
                  padding: 10,
                  background: "var(--ui-surface)",
                  color: "var(--ui-text)",
                  border: "1px solid var(--ui-border)",
                  borderRadius: 4,
                  fontFamily: "monospace",
                  fontSize: 12,
                }}
              />
            </Field>
            <div className="scan-options">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={createAccounts}
                  onChange={(e) => setCreateAccounts(e.target.checked)}
                />
                {t(
                  "Tự động tạo tài khoản đăng nhập Cổng Sinh viên (Username = MSSV)",
                  "Auto-create Student Portal login accounts (Username = Student ID)"
                )}
              </label>
              {createAccounts && (
                <Field id="bulk-default-pw" label={t("Mật khẩu mặc định", "Default password")}>
                  <input
                    id="bulk-default-pw"
                    value={defaultPw}
                    onChange={(e) => setDefaultPw(e.target.value)}
                    minLength={6}
                    style={{ maxWidth: 180 }}
                  />
                </Field>
              )}
            </div>
            <div>
              <button type="submit" className="primary-button" disabled={importing}>
                <Plus size={14} />
                {importing
                  ? t("Đang nhập danh sách…", "Importing…")
                  : t("Nhập danh sách sinh viên & Tạo tài khoản", "Import students & Create accounts")}
              </button>
            </div>
          </form>
        </Section>
      )}
    </div>
  );
};
