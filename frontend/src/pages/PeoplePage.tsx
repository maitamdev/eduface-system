import { csvDocument } from "@/lib/csv";
import React, { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Trash2, Pencil, Camera, Download, BookOpen } from "lucide-react";
import { personsApi, attendanceApi, reportsApi, type PersonOut, type AttendanceOut } from "@/api/client";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useToast } from "@/context/ToastContext";
import { useResource } from "@/hooks/useResource";
import { appPath, dateTime, errorMessage, matchesSearch } from "@/lib/format";
import { PageHeader, Section, RefreshButton, ErrorNotice, Field, EmptyState, Table, Pager, SearchField, Dialog } from "@/components/ProductUI";

export const PeoplePage: React.FC = () => {
  const { role } = useAuth();
  const { t, lang } = useLanguage();
  const toast = useToast();
  const loader = useCallback(() => personsApi.list(), []);
  const { data: people, setData, loading, error, reload } = useResource<PersonOut[]>(loader, []);
  const statsLoader = useCallback(() => reportsApi.getPersons(90), []);
  const stats = useResource(statsLoader, []);
  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<PersonOut | null>(null);
  const [editTarget, setEditTarget] = useState<PersonOut | null>(null);
  const [editName, setEditName] = useState("");
  const [editStudentId, setEditStudentId] = useState("");
  const [editDepartment, setEditDepartment] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editPhone, setEditPhone] = useState("");
  const [editDob, setEditDob] = useState("");
  const [editGender, setEditGender] = useState("");
  const [editCohort, setEditCohort] = useState("");
  const [editMajor, setEditMajor] = useState("");
  const [editAdvisor, setEditAdvisor] = useState("");
  const [editAcademicStatus, setEditAcademicStatus] = useState("active");
  const [editNotes, setEditNotes] = useState("");
  const [savingEdit, setSavingEdit] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<PersonOut | null>(null);
  const [deleting, setDeleting] = useState(false);

  const historyLoader = useCallback(() => selected ? attendanceApi.list({ person_id: selected.id, limit: 50 }) : Promise.resolve([]), [selected?.id]);
  const history = useResource<AttendanceOut[]>(historyLoader, []);
  const departments = [...new Set(people.map((person) => person.department).filter((item): item is string => !!item && item.trim().length > 0))].sort();
  const classCounts = departments.map((dept) => ({
    name: dept,
    count: people.filter((p) => p.department === dept).length,
  }));

  const filtered = people.filter(
    (person) =>
      (!department || department === person.department) &&
      (!statusFilter || (person.academic_status || "active") === statusFilter) &&
      matchesSearch(search, person.name, person.student_id, person.email, person.department, person.phone, person.major, person.cohort)
  );
  const pages = Math.max(1, Math.ceil(filtered.length / 20));
  const currentPage = Math.min(page, pages);
  const rows = filtered.slice((currentPage - 1) * 20, currentPage * 20);

  const academicStatusLabel = (st?: string | null) => {
    switch (st) {
      case "warning":
        return t("Cảnh báo học vụ", "Academic Warning");
      case "leave":
        return t("Bảo lưu", "On Leave");
      case "graduated":
        return t("Đã tốt nghiệp", "Graduated");
      default:
        return t("Đang theo học", "Active");
    }
  };

  const openEdit = (person: PersonOut) => {
    setEditTarget(person);
    setEditName(person.name);
    setEditStudentId(person.student_id || "");
    setEditDepartment(person.department || "");
    setEditEmail(person.email || "");
    setEditPhone(person.phone || "");
    setEditDob(person.date_of_birth || "");
    setEditGender(person.gender || "");
    setEditCohort(person.cohort || "");
    setEditMajor(person.major || "");
    setEditAdvisor(person.advisor || "");
    setEditAcademicStatus(person.academic_status || "active");
    setEditNotes(person.notes || "");
  };

  const saveEdit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!editTarget || savingEdit || editName.trim().length < 2) return;
    setSavingEdit(true);
    try {
      const updated = await personsApi.update(editTarget.id, {
        name: editName.trim(),
        student_id: editStudentId.trim().toUpperCase(),
        department: editDepartment.trim(),
        email: editEmail.trim(),
        phone: editPhone.trim(),
        date_of_birth: editDob.trim(),
        gender: editGender.trim(),
        cohort: editCohort.trim(),
        major: editMajor.trim(),
        advisor: editAdvisor.trim(),
        academic_status: editAcademicStatus,
        notes: editNotes.trim(),
      });
      setData((prev) => prev.map((p) => p.id === updated.id ? updated : p));
      if (selected?.id === updated.id) setSelected(updated);
      setEditTarget(null);
      toast.success(t("Đã cập nhật hồ sơ sinh viên toàn diện.", "Comprehensive student profile updated."));
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setSavingEdit(false);
    }
  };

  const remove = async () => {
    if (!deleteTarget || deleting) return;
    setDeleting(true);
    try {
      await personsApi.delete(deleteTarget.id);
      setData((previous) => previous.filter((person) => person.id !== deleteTarget.id));
      if (selected?.id === deleteTarget.id) setSelected(null);
      setDeleteTarget(null); toast.success(t("Đã xóa hồ sơ.", "Profile deleted."));
    } catch (err) { toast.error(errorMessage(err)); } finally { setDeleting(false); }
  };

  const exportRosterCsv = () => {
    const header = ["Họ và tên", "MSSV", "Lớp / Khoa", "Chuyên ngành", "Khóa", "Giới tính", "Ngày sinh", "Số điện thoại", "Email", "Cố vấn học tập", "Trạng thái học vụ", "Tỷ lệ chuyên cần (90 ngày)"];
    const csvRows = [header, ...filtered.map((p) => {
      const stat = stats.error ? undefined : stats.data.find((item) => item.person_id === p.id);
      return [p.name, p.student_id, p.department, p.major, p.cohort, p.gender, p.date_of_birth,
        p.phone, p.email, p.advisor, academicStatusLabel(p.academic_status), stat ? `${stat.attendance_rate}%` : ""];
    })];
    const blob = new Blob([csvDocument(csvRows)], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ho-so-sinh-vien-${department || "tat-ca"}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return <div className="product-page">
    <PageHeader title={t("Hồ sơ Sinh viên & Quản lý Lớp", "Student profiles & class directory")} description={t("Quản lý hồ sơ sinh viên toàn diện (hành chính, học vụ, cố vấn học tập), phân lớp và theo dõi tỷ lệ chuyên cần.", "Manage comprehensive student profiles, academic status, advisors, class rosters and attendance rates.")}>
      <RefreshButton onClick={() => { void reload(); void stats.reload(); }} loading={loading} />
      <Link to={appPath("/academic")} className="secondary-button"><BookOpen size={14} />{t("Bảng điểm & Học vụ", "Gradebook & Academic")}</Link>
      <button type="button" className="secondary-button" disabled={!filtered.length} onClick={exportRosterCsv}><Download size={14} />{t("Xuất hồ sơ (CSV)", "Export profiles (CSV)")}</button>
      {role === "admin" && <Link to={appPath("/enroll")} className="primary-button"><Plus size={14} />{t("Đăng ký khuôn mặt", "Enroll person")}</Link>}
    </PageHeader>
    <ErrorNotice message={error} retry={reload} /><ErrorNotice message={stats.error ? t("Chưa tải được tỷ lệ chuyên cần. Danh bạ vẫn sử dụng được.", "Attendance rates unavailable. The directory is still usable.") : null} retry={stats.reload} />

    {classCounts.length > 0 && (
      <div className="chart-range" aria-label={t("Chọn nhanh Lớp / Khoa", "Quick class filter")} style={{ flexWrap: "wrap", marginBottom: 4 }}>
        <button type="button" aria-pressed={department === ""} onClick={() => { setDepartment(""); setPage(1); }}>
          {t(`Tất cả lớp (${people.length})`, `All classes (${people.length})`)}
        </button>
        {classCounts.map((cls) => (
          <button key={cls.name} type="button" aria-pressed={department === cls.name} onClick={() => { setDepartment(cls.name); setPage(1); }}>
            {cls.name} ({cls.count})
          </button>
        ))}
      </div>
    )}

    <Section><div className="directory-filters"><SearchField label={t("Tìm tên, MSSV, SĐT, email, chuyên ngành…", "Search name, student ID, phone, email, major…")} value={search} onChange={(value) => { setSearch(value); setPage(1); }} /><Field id="people-department" label={t("Khoa / Lớp", "Class / Department")}><select id="people-department" value={department} onChange={(event) => { setDepartment(event.target.value); setPage(1); }}><option value="">{t("Tất cả khoa / lớp", "All classes")}</option>{departments.map((item) => <option key={item} value={item}>{item}</option>)}</select></Field><Field id="people-status" label={t("Trạng thái học vụ", "Academic status")}><select id="people-status" value={statusFilter} onChange={(event) => { setStatusFilter(event.target.value); setPage(1); }}><option value="">{t("Tất cả trạng thái", "All statuses")}</option><option value="active">{t("Đang theo học", "Active")}</option><option value="warning">{t("Cảnh báo học vụ", "Academic Warning")}</option><option value="leave">{t("Bảo lưu", "On Leave")}</option><option value="graduated">{t("Đã tốt nghiệp", "Graduated")}</option></select></Field></div>
    <Table label={t("Danh bạ sinh viên", "Student directory")}><thead><tr><th>{t("Họ và tên", "Name")}</th><th>MSSV</th><th>{t("Khoa / Lớp", "Class")}</th><th>{t("Chuyên ngành / Khóa", "Major / Cohort")}</th><th>{t("Liên hệ (SĐT / Email)", "Contact")}</th><th>{t("Trạng thái học vụ", "Academic Status")}</th><th>{t("Chuyên cần · 90 ngày", "Attendance · 90d")}</th><th className="align-right">{t("Thao tác", "Actions")}</th></tr></thead><tbody>{rows.map((person) => {
      const stat = stats.error ? undefined : stats.data.find((item) => item.person_id === person.id);
      const reenrollQuery = new URLSearchParams({ personId: person.id,
        name: person.name,
        ...(person.student_id ? { studentId: person.student_id } : {}),
        ...(person.department ? { department: person.department } : {}),
        ...(person.email ? { email: person.email } : {}),
      }).toString();
      return <tr key={person.id}><td><button className="text-button cell-strong" onClick={() => setSelected(person)}>{person.name}</button></td><td className="numeric-cell">{person.student_id || "–"}</td><td>{person.department || "–"}</td><td>{[person.major, person.cohort].filter(Boolean).join(" · ") || "–"}</td><td>{[person.phone, person.email].filter(Boolean).join(" · ") || "–"}</td><td><span className={person.academic_status === "warning" ? "warning-text" : "attendance-status"}>{academicStatusLabel(person.academic_status)}</span></td><td><span className={stat?.is_defaulter ? "warning-text" : "attendance-status"}>{stat ? `${stat.attendance_rate}%` : "–"}</span></td><td className="align-right"><div className="row-actions"><button className="text-button" onClick={() => setSelected(person)}>{t("Hồ sơ", "Profile")}</button><button className="text-button" onClick={() => openEdit(person)}><Pencil size={13} /> {t("Sửa", "Edit")}</button>{role === "admin" && <Link className="text-button" to={appPath(`/enroll?${reenrollQuery}`)} title={t("Chụp lại bộ ảnh khuôn mặt AI cho sinh viên này", "Re-capture AI face photos")}><Camera size={13} /> {t("Chụp lại mặt", "Re-enroll face")}</Link>}{role === "admin" && <button className="icon-button danger-text" aria-label={t(`Xóa hồ sơ ${person.name}`, `Delete ${person.name}`)} onClick={() => setDeleteTarget(person)}><Trash2 size={14} /></button>}</div></td></tr>;
    })}</tbody></Table>{!rows.length && <EmptyState loading={loading}>{error ? t("Danh bạ chưa tải được.", "Directory unavailable.") : t("Không có hồ sơ phù hợp.", "No matching profiles.")}</EmptyState>}<Pager count={filtered.length} page={currentPage} pages={pages} onChange={setPage} /></Section>

    {selected && <Dialog title={`${selected.name}${selected.student_id ? ` · ${selected.student_id}` : ""}`} onClose={() => setSelected(null)}>
      <dl className="profile-details">
        <div><dt>MSSV</dt><dd>{selected.student_id || "–"}</dd></div>
        <div><dt>{t("Khoa / Lớp", "Class")}</dt><dd>{selected.department || "–"}</dd></div>
        <div><dt>{t("Chuyên ngành", "Major")}</dt><dd>{selected.major || "–"}</dd></div>
        <div><dt>{t("Niên khóa", "Cohort")}</dt><dd>{selected.cohort || "–"}</dd></div>
        <div><dt>{t("Giới tính & Ngày sinh", "Gender & DOB")}</dt><dd>{[selected.gender, selected.date_of_birth].filter(Boolean).join(" · ") || "–"}</dd></div>
        <div><dt>{t("Số điện thoại", "Phone")}</dt><dd>{selected.phone || "–"}</dd></div>
        <div><dt>Email</dt><dd>{selected.email || "–"}</dd></div>
        <div><dt>{t("Cố vấn học tập", "Academic Advisor")}</dt><dd>{selected.advisor || "–"}</dd></div>
        <div><dt>{t("Trạng thái học vụ", "Academic Status")}</dt><dd className={selected.academic_status === "warning" ? "warning-text" : "attendance-status"}>{academicStatusLabel(selected.academic_status)}</dd></div>
        <div><dt>{t("Đăng ký lúc", "Enrolled at")}</dt><dd>{dateTime(selected.enrolled_at, lang)}</dd></div>
      </dl>
      {selected.notes && <p className="field-hint" style={{ marginTop: 8 }}><strong>{t("Ghi chú học vụ:", "Academic notes:")}</strong> {selected.notes}</p>}
      <h3 className="dialog-subheading">{t("50 lượt điểm danh gần nhất", "Latest 50 check-ins")}</h3>
      <ErrorNotice message={history.error} retry={history.reload} />
      {history.loading ? <EmptyState loading>{null}</EmptyState> : history.data.length ? <Table label={t("Lịch sử cá nhân", "Personal attendance")}><thead><tr><th>{t("Phiên", "Session")}</th><th>{t("Trạng thái", "Status")}</th><th>{t("Thời gian", "Time")}</th></tr></thead><tbody>{history.data.map((record) => <tr key={record.id}><td>{record.session_label}</td><td className={record.status === "absent" ? "warning-text" : "attendance-status"}>{record.status === "present" ? t("Có mặt", "Present") : record.status === "late" ? t("Đi muộn", "Late") : record.status === "excused" ? t("Có phép", "Excused") : t("Vắng mặt", "Absent")}</td><td>{dateTime(record.marked_at, lang)}</td></tr>)}</tbody></Table> : <EmptyState>{history.error ? t("Lịch sử chưa tải được.", "History unavailable.") : t("Chưa có lượt điểm danh.", "No check-ins yet.")}</EmptyState>}
    </Dialog>}

    {editTarget && (
      <Dialog title={t(`Cập nhật hồ sơ học vụ · ${editTarget.name}`, `Edit student profile · ${editTarget.name}`)} busy={savingEdit} onClose={() => setEditTarget(null)}>
        <form className="stack-form" onSubmit={saveEdit}>
          <div className="scanner-setup">
            <Field id="edit-person-name" label={t("Họ và tên *", "Full name *")}>
              <input id="edit-person-name" value={editName} onChange={(e) => setEditName(e.target.value)} minLength={2} maxLength={120} required />
            </Field>
            <Field id="edit-person-mssv" label={t("Mã số sinh viên (MSSV)", "Student ID (MSSV)")}>
              <input id="edit-person-mssv" value={editStudentId} onChange={(e) => setEditStudentId(e.target.value)} maxLength={60} placeholder="VD: 2305CT2070" />
            </Field>
          </div>
          <div className="scanner-setup">
            <Field id="edit-person-dept" label={t("Khoa / Lớp học phần", "Class / Department")}>
              <input id="edit-person-dept" list="people-classes-list" value={editDepartment} onChange={(e) => setEditDepartment(e.target.value)} maxLength={120} placeholder="VD: KTCN / 23CT2" />
              <datalist id="people-classes-list">{departments.map((cls) => <option key={cls} value={cls} />)}</datalist>
            </Field>
            <Field id="edit-person-status" label={t("Trạng thái học vụ", "Academic status")}>
              <select id="edit-person-status" value={editAcademicStatus} onChange={(e) => setEditAcademicStatus(e.target.value)}>
                <option value="active">{t("Đang theo học (Active)", "Active")}</option>
                <option value="warning">{t("Cảnh báo học vụ (Warning)", "Academic Warning")}</option>
                <option value="leave">{t("Bảo lưu (On Leave)", "On Leave")}</option>
                <option value="graduated">{t("Đã tốt nghiệp (Graduated)", "Graduated")}</option>
              </select>
            </Field>
          </div>
          <div className="scanner-setup">
            <Field id="edit-person-major" label={t("Chuyên ngành đào tạo", "Major")}>
              <input id="edit-person-major" value={editMajor} onChange={(e) => setEditMajor(e.target.value)} maxLength={120} placeholder="VD: Công nghệ thông tin" />
            </Field>
            <Field id="edit-person-cohort" label={t("Niên khóa", "Cohort")}>
              <input id="edit-person-cohort" value={editCohort} onChange={(e) => setEditCohort(e.target.value)} maxLength={40} placeholder="VD: K23 (2023-2027)" />
            </Field>
          </div>
          <div className="scanner-setup">
            <Field id="edit-person-dob" label={t("Ngày sinh", "Date of birth")}>
              <input id="edit-person-dob" type="date" value={editDob} onChange={(e) => setEditDob(e.target.value)} />
            </Field>
            <Field id="edit-person-gender" label={t("Giới tính", "Gender")}>
              <select id="edit-person-gender" value={editGender} onChange={(e) => setEditGender(e.target.value)}>
                <option value="">{t("— Chọn —", "— Select —")}</option>
                <option value="Nam">{t("Nam", "Male")}</option>
                <option value="Nữ">{t("Nữ", "Female")}</option>
                <option value="Khác">{t("Khác", "Other")}</option>
              </select>
            </Field>
          </div>
          <div className="scanner-setup">
            <Field id="edit-person-phone" label={t("Số điện thoại", "Phone number")}>
              <input id="edit-person-phone" value={editPhone} onChange={(e) => setEditPhone(e.target.value)} maxLength={30} placeholder="VD: 0901234567" />
            </Field>
            <Field id="edit-person-email" label="Email">
              <input id="edit-person-email" type="email" value={editEmail} onChange={(e) => setEditEmail(e.target.value)} maxLength={120} />
            </Field>
          </div>
          <Field id="edit-person-advisor" label={t("Cố vấn học tập / Giảng viên chủ nhiệm", "Academic Advisor")}>
            <input id="edit-person-advisor" value={editAdvisor} onChange={(e) => setEditAdvisor(e.target.value)} maxLength={120} placeholder="VD: ThS. Mai Trần Thiên Tâm" />
          </Field>
          <Field id="edit-person-notes" label={t("Ghi chú học vụ / Khen thưởng / Kỷ luật", "Academic notes")}>
            <input id="edit-person-notes" value={editNotes} onChange={(e) => setEditNotes(e.target.value)} maxLength={400} placeholder={t("Ghi chú thêm về sinh viên…", "Additional notes…")} />
          </Field>
          <div className="dialog-actions">
            <button type="button" className="secondary-button" disabled={savingEdit} onClick={() => setEditTarget(null)}>{t("Hủy", "Cancel")}</button>
            <button type="submit" className="primary-button" disabled={savingEdit}>{savingEdit ? t("Đang lưu…", "Saving…") : t("Lưu hồ sơ", "Save profile")}</button>
          </div>
        </form>
      </Dialog>
    )}

    {deleteTarget && <Dialog title={t("Xóa hồ sơ?", "Delete profile?")} onClose={() => setDeleteTarget(null)} busy={deleting}><p>{t(`Xóa hồ sơ và dữ liệu nhận diện của ${deleteTarget.name}?`, `Delete ${deleteTarget.name}'s profile and facial recognition data?`)}</p><div className="dialog-actions"><button className="secondary-button" disabled={deleting} onClick={() => setDeleteTarget(null)}>{t("Hủy", "Cancel")}</button><button className="danger-button" disabled={deleting} onClick={remove}>{deleting ? t("Đang xóa…", "Deleting…") : t("Xóa hồ sơ", "Delete profile")}</button></div></Dialog>}
  </div>;
};
