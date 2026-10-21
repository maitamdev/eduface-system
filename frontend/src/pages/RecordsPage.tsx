import React, { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Download } from "lucide-react";
import { attendanceApi, sessionsApi, type AttendanceOut } from "@/api/client";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useToast } from "@/context/ToastContext";
import { useResource } from "@/hooks/useResource";
import { dateTime, errorMessage, matchesSearch } from "@/lib/format";
import { PageHeader, Section, RefreshButton, ErrorNotice, Field, EmptyState, Table, Pager, SearchField } from "@/components/ProductUI";

const PAGE_SIZE = 20;
export const RecordsPage: React.FC<{ previewRole?: "admin" | "operator" }> = ({ previewRole }) => {
  const [params, setParams] = useSearchParams();
  const { role } = useAuth();
  const { t, lang } = useLanguage();
  const toast = useToast();
  const sessionId = params.get("sessionId") || "";
  const [date, setDate] = useState("");
  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("");
  const [page, setPage] = useState(1);
  const [exporting, setExporting] = useState(false);
  const loader = useCallback(() => attendanceApi.list({ session_id: sessionId || undefined, date: date || undefined, limit: 500 }), [sessionId, date]);
  const { data: records, loading, error, reload } = useResource<AttendanceOut[]>(loader, []);
  const sessionLoader = useCallback(() => sessionsApi.list(undefined, 100), []);
  const sessionData = useResource(sessionLoader, []);
  const departments = [...new Set(records.map((record) => record.department).filter((value): value is string => !!value))].sort();
  const filtered = records.filter((record) => (!department || record.department === department) && matchesSearch(search, record.person_name, record.session_label, record.department));
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, pages);
  const rows = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);
  useEffect(() => setPage(1), [search, department, sessionId, date]);
  const exportCsv = async () => {
    setExporting(true);
    try { await attendanceApi.downloadCsv({ session_id: sessionId || undefined, date: date || undefined }); toast.success(t("Đã xuất CSV.", "CSV downloaded.")); }
    catch (err) { toast.error(errorMessage(err)); } finally { setExporting(false); }
  };
  return <div className="product-page">
    <PageHeader title={t("Sổ điểm danh", "Attendance records")} description={t("Tra cứu theo phiên, ngày và người đã điểm danh.", "Look up check-ins by session, date and person.")}><RefreshButton onClick={reload} loading={loading} />{(previewRole || role) === "admin" && <button className="primary-button" onClick={exportCsv} disabled={exporting}><Download size={14} />{exporting ? t("Đang xuất…", "Exporting…") : t("Xuất CSV theo phiên / ngày", "Export session / date CSV")}</button>}</PageHeader>
    <ErrorNotice message={error || sessionData.error} retry={() => { void reload(); void sessionData.reload(); }} />
    <Section><div className="filter-grid">
      <Field id="records-session" label={t("Phiên điểm danh", "Session")}><select id="records-session" value={sessionId} onChange={(event) => { const next = new URLSearchParams(params); if (event.target.value) next.set("sessionId", event.target.value); else next.delete("sessionId"); setParams(next); }}><option value="">{t("Tất cả phiên", "All sessions")}</option>{sessionData.data.map((session) => <option key={session.id} value={session.id}>{session.label}</option>)}</select></Field>
      <Field id="records-date" label={t("Ngày điểm danh", "Date")}><input id="records-date" type="date" value={date} onChange={(event) => setDate(event.target.value)} /></Field>
      <Field id="records-department" label={t("Khoa / Lớp", "Department")}><select id="records-department" value={department} onChange={(event) => setDepartment(event.target.value)}><option value="">{t("Tất cả khoa / lớp", "All departments")}</option>{departments.map((item) => <option key={item}>{item}</option>)}</select></Field>
    </div><div className="table-toolbar"><SearchField label={t("Tìm tên, lớp hoặc phiên…", "Search name, department or session…")} value={search} onChange={setSearch} /><button className="text-button" onClick={() => { setSearch(""); setDepartment(""); setDate(""); setParams({}); }}>{t("Xóa bộ lọc", "Reset filters")}</button></div>
    <Table label={t("Bản ghi điểm danh", "Attendance records")}><thead><tr><th>{t("Họ và tên", "Name")}</th><th>{t("Khoa / Lớp", "Department")}</th><th>{t("Phiên điểm danh", "Session")}</th><th>{t("Thời gian", "Time")}</th><th>{t("Trạng thái", "Status")}</th><th className="align-right">{t("Độ tin cậy", "Confidence")}</th></tr></thead><tbody>{rows.map((record) => <tr key={record.id}><td className="cell-strong">{record.person_name}</td><td>{record.department || "–"}</td><td>{record.session_label}</td><td className="numeric-cell">{dateTime(record.marked_at, lang)}</td><td><span className={record.status === "present" ? "attendance-status" : "muted"}>{record.status === "present" ? t("Có mặt", "Present") : record.status}</span></td><td className="align-right numeric-cell">{record.confidence != null ? `${Math.round(record.confidence * 100)}%` : "–"}</td></tr>)}</tbody></Table>
    {!rows.length && <EmptyState loading={loading}>{error ? t("Chưa tải được dữ liệu.", "Records unavailable.") : t("Không có bản ghi phù hợp.", "No matching records.")}</EmptyState>}
    <Pager page={currentPage} pages={pages} count={filtered.length} onChange={setPage} />
    <p className="field-hint">{t("Tìm kiếm và lọc khoa áp dụng trên tối đa 500 bản ghi mới nhất. CSV gồm toàn bộ bản ghi theo phiên / ngày, không áp dụng hai bộ lọc này.", "Search and department filters apply to the latest 500 loaded records. CSV includes all records for the selected session / date and does not apply those two filters.")}</p>
    </Section>
  </div>;
};
