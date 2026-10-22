import React, { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Trash2, Pencil } from "lucide-react";
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
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<PersonOut | null>(null);
  const [editTarget, setEditTarget] = useState<PersonOut | null>(null);
  const [editName, setEditName] = useState("");
  const [editStudentId, setEditStudentId] = useState("");
  const [editDepartment, setEditDepartment] = useState("");
  const [editEmail, setEditEmail] = useState("");
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

  const filtered = people.filter((person) => (!department || department === person.department) && matchesSearch(search, person.name, person.student_id, person.email, person.department));
  const pages = Math.max(1, Math.ceil(filtered.length / 20));
  const currentPage = Math.min(page, pages);
  const rows = filtered.slice((currentPage - 1) * 20, currentPage * 20);

  const openEdit = (person: PersonOut) => {
    setEditTarget(person);
    setEditName(person.name);
    setEditStudentId(person.student_id || "");
    setEditDepartment(person.department || "");
    setEditEmail(person.email || "");
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
      });
      setData((prev) => prev.map((p) => p.id === updated.id ? updated : p));
      if (selected?.id === updated.id) setSelected(updated);
      setEditTarget(null);
      toast.success(t("Đã cập nhật hồ sơ sinh viên.", "Student profile updated."));
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

  return <div className="product-page">
    <PageHeader title={t("Danh sách Lớp & Sinh viên", "Class & student directory")} description={t("Quản lý hồ sơ sinh viên, phân lớp và theo dõi tỷ lệ chuyên cần.", "Manage student profiles, class rosters and attendance rates.")}>
      <RefreshButton onClick={() => { void reload(); void stats.reload(); }} loading={loading} />
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

    <Section><div className="directory-filters"><SearchField label={t("Tìm tên, MSSV, email hoặc lớp…", "Search name, student ID, email or class…")} value={search} onChange={(value) => { setSearch(value); setPage(1); }} /><Field id="people-department" label={t("Khoa / Lớp", "Class / Department")}><select id="people-department" value={department} onChange={(event) => { setDepartment(event.target.value); setPage(1); }}><option value="">{t("Tất cả khoa / lớp", "All classes")}</option>{departments.map((item) => <option key={item} value={item}>{item}</option>)}</select></Field></div>
    <Table label={t("Danh bạ sinh viên", "Student directory")}><thead><tr><th>{t("Họ và tên", "Name")}</th><th>MSSV</th><th>{t("Khoa / Lớp", "Class")}</th><th>Email</th><th>{t("Ngày đăng ký", "Enrolled")}</th><th>{t("Chuyên cần · 90 ngày", "Attendance · 90 days")}</th><th className="align-right">{t("Thao tác", "Actions")}</th></tr></thead><tbody>{rows.map((person) => {
      const stat = stats.error ? undefined : stats.data.find((item) => item.person_id === person.id);
      return <tr key={person.id}><td><button className="text-button cell-strong" onClick={() => setSelected(person)}>{person.name}</button></td><td className="numeric-cell">{person.student_id || "–"}</td><td>{person.department || "–"}</td><td>{person.email || "–"}</td><td>{dateTime(person.enrolled_at, lang)}</td><td><span className={stat?.is_defaulter ? "warning-text" : "attendance-status"}>{stat ? `${stat.attendance_rate}%` : "–"}</span></td><td className="align-right"><div className="row-actions"><button className="text-button" onClick={() => setSelected(person)}>{t("Lịch sử", "History")}</button><button className="text-button" onClick={() => openEdit(person)}><Pencil size={13} /> {t("Sửa", "Edit")}</button>{role === "admin" && <button className="icon-button danger-text" aria-label={t(`Xóa hồ sơ ${person.name}`, `Delete ${person.name}`)} onClick={() => setDeleteTarget(person)}><Trash2 size={14} /></button>}</div></td></tr>;
    })}</tbody></Table>{!rows.length && <EmptyState loading={loading}>{error ? t("Danh bạ chưa tải được.", "Directory unavailable.") : t("Không có hồ sơ phù hợp.", "No matching profiles.")}</EmptyState>}<Pager count={filtered.length} page={currentPage} pages={pages} onChange={setPage} /></Section>

    {selected && <Dialog title={selected.name} onClose={() => setSelected(null)}><dl className="profile-details"><div><dt>MSSV</dt><dd>{selected.student_id || "–"}</dd></div><div><dt>{t("Khoa / Lớp", "Class")}</dt><dd>{selected.department || "–"}</dd></div><div><dt>Email</dt><dd>{selected.email || "–"}</dd></div><div><dt>{t("Đăng ký lúc", "Enrolled at")}</dt><dd>{dateTime(selected.enrolled_at, lang)}</dd></div></dl><h3 className="dialog-subheading">{t("50 lượt điểm danh gần nhất", "Latest 50 check-ins")}</h3><ErrorNotice message={history.error} retry={history.reload} />{history.loading ? <EmptyState loading>{null}</EmptyState> : history.data.length ? <Table label={t("Lịch sử cá nhân", "Personal attendance")}><thead><tr><th>{t("Phiên", "Session")}</th><th>{t("Trạng thái", "Status")}</th><th>{t("Thời gian", "Time")}</th></tr></thead><tbody>{history.data.map((record) => <tr key={record.id}><td>{record.session_label}</td><td className={record.status === "absent" ? "warning-text" : "attendance-status"}>{record.status === "present" ? t("Có mặt", "Present") : record.status === "late" ? t("Đi muộn", "Late") : record.status === "excused" ? t("Có phép", "Excused") : t("Vắng mặt", "Absent")}</td><td>{dateTime(record.marked_at, lang)}</td></tr>)}</tbody></Table> : <EmptyState>{history.error ? t("Lịch sử chưa tải được.", "History unavailable.") : t("Chưa có lượt điểm danh.", "No check-ins yet.")}</EmptyState>}</Dialog>}

    {editTarget && (
      <Dialog title={t(`Cập nhật hồ sơ · ${editTarget.name}`, `Edit profile · ${editTarget.name}`)} busy={savingEdit} onClose={() => setEditTarget(null)}>
        <form className="stack-form" onSubmit={saveEdit}>
          <Field id="edit-person-name" label={t("Họ và tên *", "Full name *")}>
            <input id="edit-person-name" value={editName} onChange={(e) => setEditName(e.target.value)} minLength={2} maxLength={120} required />
          </Field>
          <Field id="edit-person-mssv" label={t("Mã số sinh viên (MSSV)", "Student ID (MSSV)")}>
            <input id="edit-person-mssv" value={editStudentId} onChange={(e) => setEditStudentId(e.target.value)} maxLength={60} placeholder="VD: 2305CT2070" />
          </Field>
          <Field id="edit-person-dept" label={t("Khoa / Lớp học phần", "Class / Department")}>
            <input id="edit-person-dept" list="people-classes-list" value={editDepartment} onChange={(e) => setEditDepartment(e.target.value)} maxLength={120} placeholder="VD: CNTT / 23CT2" />
            <datalist id="people-classes-list">{departments.map((cls) => <option key={cls} value={cls} />)}</datalist>
          </Field>
          <Field id="edit-person-email" label="Email">
            <input id="edit-person-email" type="email" value={editEmail} onChange={(e) => setEditEmail(e.target.value)} maxLength={120} />
          </Field>
          <div className="dialog-actions">
            <button type="button" className="secondary-button" disabled={savingEdit} onClick={() => setEditTarget(null)}>{t("Hủy", "Cancel")}</button>
            <button type="submit" className="primary-button" disabled={savingEdit}>{savingEdit ? t("Đang lưu…", "Saving…") : t("Lưu thay đổi", "Save changes")}</button>
          </div>
        </form>
      </Dialog>
    )}

    {deleteTarget && <Dialog title={t("Xóa hồ sơ?", "Delete profile?")} onClose={() => setDeleteTarget(null)} busy={deleting}><p>{t(`Xóa hồ sơ và dữ liệu nhận diện của ${deleteTarget.name}?`, `Delete ${deleteTarget.name}'s profile and facial recognition data?`)}</p><div className="dialog-actions"><button className="secondary-button" disabled={deleting} onClick={() => setDeleteTarget(null)}>{t("Hủy", "Cancel")}</button><button className="danger-button" disabled={deleting} onClick={remove}>{deleting ? t("Đang xóa…", "Deleting…") : t("Xóa hồ sơ", "Delete profile")}</button></div></Dialog>}
  </div>;
};
