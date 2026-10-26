import React, { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Download, Plus } from "lucide-react";
import { attendanceApi, personsApi, sessionsApi, type AttendanceOut, type PersonOut } from "@/api/client";
import { useLanguage } from "@/context/LanguageContext";
import { useToast } from "@/context/ToastContext";
import { useResource } from "@/hooks/useResource";
import { dateTime, errorMessage, matchesSearch } from "@/lib/format";
import { PageHeader, Section, RefreshButton, ErrorNotice, Field, EmptyState, Table, Pager, SearchField, Dialog } from "@/components/ProductUI";

const PAGE_SIZE = 20;
export const RecordsPage: React.FC<{ previewRole?: "admin" | "operator" }> = () => {
  const [params, setParams] = useSearchParams();
  const { t, lang } = useLanguage();
  const toast = useToast();
  const sessionId = params.get("sessionId") || "";
  const [date, setDate] = useState("");
  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [exporting, setExporting] = useState(false);
  const [manualOpen, setManualOpen] = useState(false);
  const [manualSessionId, setManualSessionId] = useState("");
  const [manualPersonId, setManualPersonId] = useState("");
  const [manualStatus, setManualStatus] = useState<"present" | "late" | "excused" | "absent">("present");
  const [savingManual, setSavingManual] = useState(false);

  const loader = useCallback(() => attendanceApi.listAll({ session_id: sessionId || undefined, date: date || undefined, status: statusFilter || undefined }), [sessionId, date, statusFilter]);
  const { data: records, setData: setRecords, loading, error, reload } = useResource<AttendanceOut[]>(loader, []);
  const sessionLoader = useCallback(() => sessionsApi.listAll(), []);
  const sessionData = useResource(sessionLoader, []);
  const peopleLoader = useCallback(() => personsApi.list(), []);
  const peopleData = useResource<PersonOut[]>(peopleLoader, []);

  const departments = [...new Set([
    ...records.map((record) => record.department),
    ...peopleData.data.map((person) => person.department),
  ].filter((value): value is string => !!value && value.trim().length > 0))].sort();

  const filtered = records.filter((record) => (!department || record.department === department) && matchesSearch(search, record.person_name, record.student_id, record.session_label, record.department));
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, pages);
  const rows = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);
  useEffect(() => setPage(1), [search, department, sessionId, date, statusFilter]);

  const exportCsv = async () => {
    setExporting(true);
    try {
      await attendanceApi.downloadCsv({ session_id: sessionId || undefined, date: date || undefined, department: department || undefined });
      toast.success(t("Đã xuất file CSV điểm danh.", "CSV downloaded."));
    } catch (err) { toast.error(errorMessage(err)); } finally { setExporting(false); }
  };

  const updateRowStatus = async (record: AttendanceOut, nextStatus: "present" | "late" | "excused" | "absent") => {
    try {
      const updated = await attendanceApi.setManual({
        person_id: record.person_id,
        session_id: record.session_id,
        status: nextStatus,
      });
      setRecords((prev) => prev.map((item) => item.id === record.id ? updated : item));
      toast.success(t(`Đã đổi trạng thái của ${record.person_name}.`, `Updated status for ${record.person_name}.`));
    } catch (err) {
      toast.error(errorMessage(err));
    }
  };

  const submitManual = async (event: React.FormEvent) => {
    event.preventDefault();
    const targetSession = manualSessionId || sessionId;
    if (!targetSession || !manualPersonId || savingManual) return;
    setSavingManual(true);
    try {
      const updated = await attendanceApi.setManual({
        person_id: manualPersonId,
        session_id: targetSession,
        status: manualStatus,
      });
      setRecords((prev) => {
        const exists = prev.some((item) => item.id === updated.id);
        return exists ? prev.map((item) => item.id === updated.id ? updated : item) : [updated, ...prev];
      });
      setManualOpen(false);
      toast.success(t("Đã lưu điểm danh thủ công.", "Manual attendance saved."));
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setSavingManual(false);
    }
  };

  const selectedManualSession = sessionData.data.find((s) => s.id === (manualSessionId || sessionId));
  const eligiblePeople = peopleData.data.filter((p) => {
    if (!selectedManualSession?.department) return true;
    return (p.department || "").toLowerCase() === selectedManualSession.department.toLowerCase();
  });

  return <div className="product-page">
    <PageHeader title={t("Sổ điểm danh", "Attendance records")} description={t("Tra cứu theo phiên, lớp, ngày; điểm danh bổ sung và xuất CSV.", "Look up check-ins by session, class, date; record manual attendance and export CSV.")}>
      <RefreshButton onClick={reload} loading={loading} />
      <button className="secondary-button" onClick={() => { setManualSessionId(sessionId || sessionData.data[0]?.id || ""); setManualPersonId(""); setManualStatus("present"); setManualOpen(true); }}><Plus size={14} />{t("Điểm danh thủ công", "Manual mark")}</button>
      <button className="primary-button" onClick={exportCsv} disabled={exporting}><Download size={14} />{exporting ? t("Đang xuất…", "Exporting…") : t("Xuất CSV", "Export CSV")}</button>
    </PageHeader>
    <ErrorNotice message={error || sessionData.error} retry={() => { void reload(); void sessionData.reload(); }} />
    <Section><div className="filter-grid">
      <Field id="records-session" label={t("Phiên điểm danh", "Session")}><select id="records-session" value={sessionId} onChange={(event) => { const next = new URLSearchParams(params); if (event.target.value) next.set("sessionId", event.target.value); else next.delete("sessionId"); setParams(next); }}><option value="">{t("Tất cả phiên", "All sessions")}</option>{sessionData.data.map((session) => <option key={session.id} value={session.id}>{session.label} {session.department ? `(${session.department})` : ""}</option>)}</select></Field>
      <Field id="records-department" label={t("Khoa / Lớp", "Class / Department")}><select id="records-department" value={department} onChange={(event) => setDepartment(event.target.value)}><option value="">{t("Tất cả khoa / lớp", "All classes")}</option>{departments.map((item) => <option key={item} value={item}>{item}</option>)}</select></Field>
      <Field id="records-status" label={t("Trạng thái", "Status")}>
        <select id="records-status" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
          <option value="">{t("Tất cả trạng thái", "All statuses")}</option>
          <option value="present">{t("Có mặt (Đúng giờ)", "Present")}</option>
          <option value="late">{t("Đi muộn (Late)", "Late")}</option>
          <option value="excused">{t("Vắng có phép (Excused)", "Excused")}</option>
          <option value="absent">{t("Vắng mặt (Absent)", "Absent")}</option>
        </select>
      </Field>
      <Field id="records-date" label={t("Ngày điểm danh", "Date")}><input id="records-date" type="date" value={date} onChange={(event) => setDate(event.target.value)} /></Field>
    </div><div className="table-toolbar"><SearchField label={t("Tìm tên, MSSV, lớp hoặc phiên…", "Search name, student ID, class or session…")} value={search} onChange={setSearch} /><button className="text-button" onClick={() => { setSearch(""); setDepartment(""); setDate(""); setStatusFilter(""); setParams({}); }}>{t("Xóa bộ lọc", "Reset filters")}</button></div>
    <Table label={t("Bản ghi điểm danh", "Attendance records")}><thead><tr><th>{t("Họ và tên", "Name")}</th><th>MSSV</th><th>{t("Khoa / Lớp", "Class")}</th><th>{t("Phiên điểm danh", "Session")}</th><th>{t("Thời gian", "Time")}</th><th>{t("Trạng thái (Đổi nhanh)", "Status")}</th><th className="align-right">{t("Tương đồng cosine", "Cosine similarity")}</th></tr></thead><tbody>{rows.map((record) => <tr key={record.id}><td className="cell-strong">{record.person_name}</td><td className="numeric-cell">{record.student_id || "–"}</td><td>{record.department || "–"}</td><td>{record.session_label}</td><td className="numeric-cell">{dateTime(record.marked_at, lang)}</td><td>
      <select
        aria-label={t(`Trạng thái của ${record.person_name}`, `Status for ${record.person_name}`)}
        value={record.status}
        onChange={(event) => void updateRowStatus(record, event.target.value as "present" | "late" | "excused" | "absent")}
        className={record.status === "present" ? "attendance-status" : record.status === "absent" ? "warning-text" : ""}
      >
        <option value="present">{t("✓ Có mặt", "✓ Present")}</option>
        <option value="late">{t("⏰ Đi muộn", "⏰ Late")}</option>
        <option value="excused">{t("📋 Có phép", "📋 Excused")}</option>
        <option value="absent">{t("✕ Vắng mặt", "✕ Absent")}</option>
      </select>
    </td><td className="align-right numeric-cell">{record.confidence != null ? record.confidence.toFixed(3) : t("Thủ công / Hệ thống", "Manual / Auto")}</td></tr>)}</tbody></Table>
    {!rows.length && <EmptyState loading={loading}>{error ? t("Chưa tải được dữ liệu.", "Records unavailable.") : t("Không có bản ghi phù hợp.", "No matching records.")}</EmptyState>}
    <Pager page={currentPage} pages={pages} count={filtered.length} onChange={setPage} />
    <p className="field-hint">{t("Giảng viên và Admin có thể đổi trực tiếp trạng thái (Có mặt / Đi muộn / Có phép / Vắng mặt) hoặc xuất CSV theo Phiên, Ngày và Lớp.", "Instructors and Admins can update attendance status inline or export CSV filtered by session, date, and class.")}</p>
    </Section>
    {manualOpen && (
      <Dialog title={t("Điểm danh thủ công / Bổ sung", "Manual attendance entry")} busy={savingManual} onClose={() => setManualOpen(false)}>
        <form className="stack-form" onSubmit={submitManual}>
          <Field id="manual-session" label={t("Phiên điểm danh *", "Session *")}>
            <select id="manual-session" value={manualSessionId || sessionId} onChange={(e) => { setManualSessionId(e.target.value); setManualPersonId(""); }} required>
              <option value="">{t("— Chọn phiên điểm danh —", "— Select session —")}</option>
              {sessionData.data.map((s) => <option key={s.id} value={s.id}>{s.label} {s.department ? `(${s.department})` : ""}</option>)}
            </select>
          </Field>
          <Field id="manual-person" label={t("Sinh viên *", "Student *")}>
            <select id="manual-person" value={manualPersonId} onChange={(e) => setManualPersonId(e.target.value)} required>
              <option value="">{t("— Chọn sinh viên —", "— Select student —")}</option>
              {(eligiblePeople.length ? eligiblePeople : peopleData.data).map((p) => (
                <option key={p.id} value={p.id}>{p.name} {p.student_id ? `· ${p.student_id}` : ""} {p.department ? `(${p.department})` : ""}</option>
              ))}
            </select>
          </Field>
          <Field id="manual-status" label={t("Trạng thái điểm danh *", "Attendance status *")}>
            <select id="manual-status" value={manualStatus} onChange={(e) => setManualStatus(e.target.value as "present" | "late" | "excused" | "absent")}>
              <option value="present">{t("Có mặt (Đúng giờ)", "Present")}</option>
              <option value="late">{t("Đi muộn (Late)", "Late")}</option>
              <option value="excused">{t("Vắng có phép (Excused)", "Excused")}</option>
              <option value="absent">{t("Vắng không phép (Absent)", "Absent")}</option>
            </select>
          </Field>
          <div className="dialog-actions">
            <button type="button" className="secondary-button" disabled={savingManual} onClick={() => setManualOpen(false)}>{t("Hủy", "Cancel")}</button>
            <button type="submit" className="primary-button" disabled={savingManual || !(manualSessionId || sessionId) || !manualPersonId}>{savingManual ? t("Đang lưu…", "Saving…") : t("Lưu điểm danh", "Save record")}</button>
          </div>
        </form>
      </Dialog>
    )}
  </div>;
};
