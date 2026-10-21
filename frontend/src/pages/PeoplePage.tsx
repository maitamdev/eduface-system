import React, { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Trash2 } from "lucide-react";
import { personsApi, attendanceApi, reportsApi, type PersonOut, type AttendanceOut } from "@/api/client";
import { useLanguage } from "@/context/LanguageContext";
import { useToast } from "@/context/ToastContext";
import { useResource } from "@/hooks/useResource";
import { appPath, dateTime, errorMessage, matchesSearch } from "@/lib/format";
import { PageHeader, Section, RefreshButton, ErrorNotice, Field, EmptyState, Table, Pager, SearchField, Dialog } from "@/components/ProductUI";

export const PeoplePage: React.FC = () => {
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
  const [deleteTarget, setDeleteTarget] = useState<PersonOut | null>(null);
  const [deleting, setDeleting] = useState(false);
  const historyLoader = useCallback(() => selected ? attendanceApi.list({ person_id: selected.id, limit: 50 }) : Promise.resolve([]), [selected?.id]);
  const history = useResource<AttendanceOut[]>(historyLoader, []);
  const departments = [...new Set(people.map((person) => person.department).filter((item): item is string => !!item))].sort();
  const filtered = people.filter((person) => (!department || department === person.department) && matchesSearch(search, person.name, person.email, person.department));
  const pages = Math.max(1, Math.ceil(filtered.length / 20));
  const currentPage = Math.min(page, pages);
  const rows = filtered.slice((currentPage - 1) * 20, currentPage * 20);
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
    <PageHeader title={t("Danh bạ sinh viên / nhân sự", "People directory")} description={t("Hồ sơ đã đăng ký nhận diện khuôn mặt.", "People enrolled for facial recognition.")}><RefreshButton onClick={() => { void reload(); void stats.reload(); }} loading={loading} /><Link to={appPath("/enroll")} className="primary-button"><Plus size={14} />{t("Đăng ký khuôn mặt", "Enroll person")}</Link></PageHeader>
    <ErrorNotice message={error} retry={reload} /><ErrorNotice message={stats.error ? t("Chưa tải được tỷ lệ chuyên cần. Danh bạ vẫn sử dụng được.", "Attendance rates unavailable. The directory is still usable.") : null} retry={stats.reload} />
    <Section><div className="directory-filters"><SearchField label={t("Tìm tên, email hoặc lớp…", "Search name, email or department…")} value={search} onChange={(value) => { setSearch(value); setPage(1); }} /><Field id="people-department" label={t("Khoa / Lớp", "Department")}><select id="people-department" value={department} onChange={(event) => { setDepartment(event.target.value); setPage(1); }}><option value="">{t("Tất cả khoa / lớp", "All departments")}</option>{departments.map((item) => <option key={item}>{item}</option>)}</select></Field></div>
    <Table label={t("Danh bạ", "People")}><thead><tr><th>{t("Họ và tên", "Name")}</th><th>Email</th><th>{t("Khoa / Lớp", "Department")}</th><th>{t("Ngày đăng ký", "Enrolled")}</th><th>{t("Chuyên cần · 90 ngày", "Attendance · 90 days")}</th><th className="align-right">{t("Thao tác", "Actions")}</th></tr></thead><tbody>{rows.map((person) => {
      const stat = stats.error ? undefined : stats.data.find((item) => item.person_id === person.id);
      return <tr key={person.id}><td><button className="text-button cell-strong" onClick={() => setSelected(person)}>{person.name}</button></td><td>{person.email || "–"}</td><td>{person.department || "–"}</td><td>{dateTime(person.enrolled_at, lang)}</td><td><span className={stat?.is_defaulter ? "warning-text" : ""}>{stat ? `${stat.attendance_rate}%` : "–"}</span></td><td className="align-right"><div className="row-actions"><button className="text-button" onClick={() => setSelected(person)}>{t("Chi tiết", "Details")}</button><button className="icon-button danger-text" aria-label={t(`Xóa hồ sơ ${person.name}`, `Delete ${person.name}`)} onClick={() => setDeleteTarget(person)}><Trash2 size={14} /></button></div></td></tr>;
    })}</tbody></Table>{!rows.length && <EmptyState loading={loading}>{error ? t("Danh bạ chưa tải được.", "Directory unavailable.") : t("Không có hồ sơ phù hợp.", "No matching profiles.")}</EmptyState>}<Pager count={filtered.length} page={currentPage} pages={pages} onChange={setPage} /></Section>
    {selected && <Dialog title={selected.name} onClose={() => setSelected(null)}><dl className="profile-details"><div><dt>Email</dt><dd>{selected.email || "–"}</dd></div><div><dt>{t("Khoa / Lớp", "Department")}</dt><dd>{selected.department || "–"}</dd></div><div><dt>{t("Đăng ký lúc", "Enrolled at")}</dt><dd>{dateTime(selected.enrolled_at, lang)}</dd></div></dl><h3 className="dialog-subheading">{t("50 lượt điểm danh gần nhất", "Latest 50 check-ins")}</h3><ErrorNotice message={history.error} retry={history.reload} />{history.loading ? <EmptyState loading>{null}</EmptyState> : history.data.length ? <Table label={t("Lịch sử cá nhân", "Personal attendance")}><thead><tr><th>{t("Phiên", "Session")}</th><th>{t("Thời gian", "Time")}</th></tr></thead><tbody>{history.data.map((record) => <tr key={record.id}><td>{record.session_label}</td><td>{dateTime(record.marked_at, lang)}</td></tr>)}</tbody></Table> : <EmptyState>{history.error ? t("Lịch sử chưa tải được.", "History unavailable.") : t("Chưa có lượt điểm danh.", "No check-ins yet.")}</EmptyState>}</Dialog>}
    {deleteTarget && <Dialog title={t("Xóa hồ sơ?", "Delete profile?")} onClose={() => setDeleteTarget(null)} busy={deleting}><p>{t(`Xóa hồ sơ và dữ liệu nhận diện của ${deleteTarget.name}?`, `Delete ${deleteTarget.name}'s profile and facial recognition data?`)}</p><div className="dialog-actions"><button className="secondary-button" disabled={deleting} onClick={() => setDeleteTarget(null)}>{t("Hủy", "Cancel")}</button><button className="danger-button" disabled={deleting} onClick={remove}>{deleting ? t("Đang xóa…", "Deleting…") : t("Xóa hồ sơ", "Delete profile")}</button></div></Dialog>}
  </div>;
};
