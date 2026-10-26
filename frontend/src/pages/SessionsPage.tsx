import React, { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, ArrowRight } from "lucide-react";
import { academicApi, personsApi, sessionsApi, type PersonOut, type SessionOut } from "@/api/client";
import { useLanguage } from "@/context/LanguageContext";
import { useToast } from "@/context/ToastContext";
import { useResource } from "@/hooks/useResource";
import { appPath, dateTime, errorMessage, timeOnly } from "@/lib/format";
import { PageHeader, Section, RefreshButton, ErrorNotice, Field, EmptyState, Table, Dialog } from "@/components/ProductUI";

export const SessionsPage: React.FC = () => {
  const { t, lang } = useLanguage();
  const toast = useToast();
  const loader = useCallback(() => sessionsApi.listAll(), []);
  const { data: sessions, setData, loading, error, reload } = useResource<SessionOut[]>(loader, []);
  const peopleLoader = useCallback(() => personsApi.list(), []);
  const people = useResource<PersonOut[]>(peopleLoader, []);
  const courses = useResource(useCallback(() => academicApi.listCourses(), []), []);
  const [courseId, setCourseId] = useState("");
  const [label, setLabel] = useState("");
  const [department, setDepartment] = useState("");
  const [lateMinutes, setLateMinutes] = useState<number>(15);
  const [creating, setCreating] = useState(false);
  const [endTarget, setEndTarget] = useState<SessionOut | null>(null);
  const [ending, setEnding] = useState(false);
  const active = sessions.filter((session) => session.is_active);
  const closed = sessions.filter((session) => !session.is_active);
  const knownClasses = [...new Set([
    ...people.data.map((p) => p.department),
    ...sessions.map((s) => s.department),
  ].filter((item): item is string => !!item && item.trim().length > 0))].sort();

  const create = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!label.trim() || creating) return;
    setCreating(true);
    try {
      const session = await sessionsApi.create(label, department || undefined, lateMinutes, courseId || undefined);
      setData((previous) => [session, ...previous]); setLabel(""); setDepartment("");
      toast.success(t("Đã mở phiên điểm danh.", "Session opened."));
    } catch (err) { toast.error(errorMessage(err)); } finally { setCreating(false); }
  };
  const end = async () => {
    if (!endTarget || ending) return;
    setEnding(true);
    try {
      const result = await sessionsApi.end(endTarget.id);
      setData((previous) => previous.map((session) => session.id === result.id ? result : session));
      setEndTarget(null); toast.success(t("Đã kết thúc phiên và chốt danh sách vắng mặt.", "Session closed and absences recorded."));
    } catch (err) { toast.error(errorMessage(err)); } finally { setEnding(false); }
  };
  return <div className="product-page">
    <PageHeader title={t("Phiên điểm danh", "Attendance sessions")} description={t("Mở phiên theo từng Lớp / Học phần và cài đặt mốc thời gian tính đi muộn.", "Manage check-ins by class/department and configure late thresholds.")}><RefreshButton onClick={reload} loading={loading} /></PageHeader>
    <ErrorNotice message={error} retry={reload} /><ErrorNotice message={courses.error} retry={courses.reload} />
    <Section title={t("Tạo phiên mới theo Lớp / Học phần", "Open new class session")}><form onSubmit={create} className="inline-form">
      <Field id="session-course" label={t("Học phần / Học kỳ", "Course / Semester")}><select id="session-course" value={courseId} onChange={(e) => { setCourseId(e.target.value); setDepartment(courses.data.find((c) => c.id === e.target.value)?.department || ""); }}><option value="">{t("Phiên chung (không tính điểm môn)", "General session (no course grade)")}</option>{courses.data.map((c) => <option key={c.id} value={c.id}>{c.code} · {c.name} · {c.semester} · {c.department}</option>)}</select></Field>
      <Field id="session-label" label={t("Tên học phần / Buổi học *", "Session name *")}><input id="session-label" value={label} onChange={(event) => setLabel(event.target.value)} maxLength={200} placeholder={t("Ví dụ: Lập trình Web · Buổi 5", "e.g. Web development · Week 5")} required /></Field>
      <Field id="session-department" label={t("Khoa / Lớp áp dụng", "Target Class / Department")}>
        <input id="session-department" list="known-classes-list" value={department} onChange={(event) => setDepartment(event.target.value)} maxLength={100} placeholder={t("Chọn hoặc nhập mã lớp (VD: CNTT)", "Select or type class (e.g. CNTT)")} />
        <datalist id="known-classes-list">{knownClasses.map((cls) => <option key={cls} value={cls} />)}</datalist>
      </Field>
      <Field id="session-late" label={t("Mốc tính Đi muộn", "Late threshold")}>
        <select id="session-late" value={lateMinutes} onChange={(event) => setLateMinutes(Number(event.target.value))}>
          <option value={10}>{t("Sau 10 phút", "After 10 mins")}</option>
          <option value={15}>{t("Sau 15 phút (Mặc định)", "After 15 mins (Default)")}</option>
          <option value={20}>{t("Sau 20 phút", "After 20 mins")}</option>
          <option value={30}>{t("Sau 30 phút", "After 30 mins")}</option>
          <option value={0}>{t("Không giới hạn giờ muộn", "No late cutoff")}</option>
        </select>
      </Field>
      <button className="primary-button" type="submit" disabled={creating}><Plus size={14} />{creating ? t("Đang mở…", "Opening…") : t("Mở phiên", "Open session")}</button>
    </form></Section>
    <Section title={t(`Phiên đang mở (${active.length})`, `Active sessions (${active.length})`)}>
      {active.length ? <div className="session-rows">{active.map((session) => <div className="session-row" key={session.id}><span className="session-start">{timeOnly(session.started_at, lang)}</span><div className="session-title"><h3>{session.label}</h3><p>{session.department ? t(`Lớp: ${session.department}`, `Class: ${session.department}`) : t("Tất cả khoa / lớp", "All departments")} · {session.late_after_minutes ? t(`Tính muộn sau ${session.late_after_minutes} phút`, `Late after ${session.late_after_minutes}m`) : t("Không tính muộn", "No late cutoff")}</p></div><Link className="text-link" to={appPath(`/records?sessionId=${session.id}`)}>{t("Sổ lớp", "Roster")}</Link><button className="text-button danger-text" onClick={() => setEndTarget(session)}>{t("Kết thúc", "End")}</button><Link className="secondary-button" to={appPath(`/scanner?sessionId=${session.id}`)}>{t("Điểm danh", "Check in")}<ArrowRight size={14} /></Link></div>)}</div> : <EmptyState loading={loading}>{error ? t("Chưa tải được danh sách phiên.", "Session list unavailable.") : t("Chưa có phiên đang mở.", "No active sessions.")}</EmptyState>}
    </Section>
    <Section title={t("Phiên đã kết thúc", "Closed sessions")}><Table label={t("Lịch sử phiên", "Session history")}><thead><tr><th>{t("Tên phiên", "Session")}</th><th>{t("Khoa / Lớp", "Class / Dept")}</th><th>{t("Quy tắc muộn", "Late rule")}</th><th>{t("Bắt đầu", "Started")}</th><th>{t("Kết thúc", "Ended")}</th><th>{t("Bản ghi", "Records")}</th></tr></thead><tbody>{closed.map((session) => <tr key={session.id}><td className="cell-strong">{session.label}</td><td>{session.department || t("Tất cả lớp", "All")}</td><td className="muted">{session.late_after_minutes ? `${session.late_after_minutes}p` : "–"}</td><td>{dateTime(session.started_at, lang)}</td><td>{dateTime(session.ended_at, lang)}</td><td><Link className="text-link" to={appPath(`/records?sessionId=${session.id}`)}>{t("Xem điểm danh", "View records")}<ArrowRight size={13} /></Link></td></tr>)}</tbody></Table>{!closed.length && <EmptyState loading={loading}>{error ? t("Chưa tải được lịch sử phiên.", "Session history unavailable.") : t("Chưa có phiên đã kết thúc.", "No closed sessions.")}</EmptyState>}</Section>
    {endTarget && <Dialog title={t("Kết thúc phiên & chốt danh sách lớp?", "End session & finalize class roster?")} onClose={() => setEndTarget(null)} busy={ending}><p><strong>{endTarget.label}</strong> {endTarget.department ? `(${endTarget.department})` : ""}</p><p className="muted">{t("Sau khi kết thúc, máy quét sẽ ngừng nhận diện và những sinh viên thuộc lớp chưa quét mặt sẽ tự động được ghi nhận trạng thái Vắng mặt (Absent) trong sổ điểm danh.", "Closing this session stops the scanner and automatically marks remaining un-scanned students in the class as Absent.")}</p><div className="dialog-actions"><button className="secondary-button" disabled={ending} onClick={() => setEndTarget(null)}>{t("Hủy", "Cancel")}</button><button className="danger-button" disabled={ending} onClick={end}>{ending ? t("Đang kết thúc…", "Closing…") : t("Kết thúc & Chốt sổ", "End & Finalize")}</button></div></Dialog>}
  </div>;
};
