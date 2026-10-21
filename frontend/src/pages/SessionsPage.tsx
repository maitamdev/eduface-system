import React, { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, ArrowRight } from "lucide-react";
import { sessionsApi, type SessionOut } from "@/api/client";
import { useLanguage } from "@/context/LanguageContext";
import { useToast } from "@/context/ToastContext";
import { useResource } from "@/hooks/useResource";
import { appPath, dateTime, errorMessage } from "@/lib/format";
import { PageHeader, Section, RefreshButton, ErrorNotice, Field, EmptyState, Table, Dialog } from "@/components/ProductUI";

export const SessionsPage: React.FC = () => {
  const { t, lang } = useLanguage();
  const toast = useToast();
  const loader = useCallback(() => sessionsApi.list(undefined, 100), []);
  const { data: sessions, setData, loading, error, reload } = useResource<SessionOut[]>(loader, []);
  const [label, setLabel] = useState("");
  const [department, setDepartment] = useState("");
  const [creating, setCreating] = useState(false);
  const [endTarget, setEndTarget] = useState<SessionOut | null>(null);
  const [ending, setEnding] = useState(false);
  const active = sessions.filter((session) => session.is_active);
  const closed = sessions.filter((session) => !session.is_active);
  const create = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!label.trim() || creating) return;
    setCreating(true);
    try {
      const session = await sessionsApi.create(label, department || undefined);
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
      setEndTarget(null); toast.success(t("Đã kết thúc phiên.", "Session closed."));
    } catch (err) { toast.error(errorMessage(err)); } finally { setEnding(false); }
  };
  return <div className="product-page">
    <PageHeader title={t("Phiên điểm danh", "Attendance sessions")} description={t("Mở phiên cho buổi học, ca làm hoặc sự kiện.", "Manage check-ins for classes, shifts and events.")}><RefreshButton onClick={reload} loading={loading} /></PageHeader>
    <ErrorNotice message={error} retry={reload} />
    <Section title={t("Tạo phiên mới", "New session")}><form onSubmit={create} className="inline-form">
      <Field id="session-label" label={t("Tên phiên *", "Session name *")}><input id="session-label" value={label} onChange={(event) => setLabel(event.target.value)} maxLength={200} placeholder={t("Ví dụ: Lập trình Web · Buổi 5", "e.g. Web development · Week 5")} required /></Field>
      <Field id="session-department" label={t("Khoa / Lớp", "Department / Class")}><input id="session-department" value={department} onChange={(event) => setDepartment(event.target.value)} maxLength={100} placeholder={t("Không bắt buộc", "Optional")} /></Field>
      <button className="primary-button" type="submit" disabled={creating}><Plus size={14} />{creating ? t("Đang mở…", "Opening…") : t("Mở phiên", "Open session")}</button>
    </form></Section>
    <Section title={t(`Phiên đang mở (${active.length})`, `Active sessions (${active.length})`)}>
      {active.length ? <div className="session-rows">{active.map((session) => <div className="session-row" key={session.id}><span className="session-start">{new Date(session.started_at).toLocaleTimeString(lang === "vi" ? "vi-VN" : "en-GB", { hour: "2-digit", minute: "2-digit" })}</span><div className="session-title"><h3>{session.label}</h3><p>{session.department || t("Tất cả khoa / lớp", "All departments")}</p></div><button className="text-button danger-text" onClick={() => setEndTarget(session)}>{t("Kết thúc", "End")}</button><Link className="secondary-button" to={appPath(`/scanner?sessionId=${session.id}`)}>{t("Điểm danh", "Check in")}<ArrowRight size={14} /></Link></div>)}</div> : <EmptyState loading={loading}>{error ? t("Chưa tải được danh sách phiên.", "Session list unavailable.") : t("Chưa có phiên đang mở.", "No active sessions.")}</EmptyState>}
    </Section>
    <Section title={t("Phiên đã kết thúc", "Closed sessions")}><Table label={t("Lịch sử phiên", "Session history")}><thead><tr><th>{t("Tên phiên", "Session")}</th><th>{t("Khoa / Lớp", "Department")}</th><th>{t("Bắt đầu", "Started")}</th><th>{t("Kết thúc", "Ended")}</th><th>{t("Bản ghi", "Records")}</th></tr></thead><tbody>{closed.map((session) => <tr key={session.id}><td className="cell-strong">{session.label}</td><td>{session.department || "–"}</td><td>{dateTime(session.started_at, lang)}</td><td>{dateTime(session.ended_at, lang)}</td><td><Link className="text-link" to={appPath(`/records?sessionId=${session.id}`)}>{t("Xem điểm danh", "View records")}<ArrowRight size={13} /></Link></td></tr>)}</tbody></Table>{!closed.length && <EmptyState loading={loading}>{error ? t("Chưa tải được lịch sử phiên.", "Session history unavailable.") : t("Chưa có phiên đã kết thúc.", "No closed sessions.")}</EmptyState>}</Section>
    {endTarget && <Dialog title={t("Kết thúc phiên điểm danh?", "End attendance session?")} onClose={() => setEndTarget(null)} busy={ending}><p>{endTarget.label}</p><p className="muted">{t("Sau khi kết thúc, máy quét sẽ không thể ghi thêm điểm danh vào phiên này.", "The scanner will no longer accept check-ins for this session.")}</p><div className="dialog-actions"><button className="secondary-button" disabled={ending} onClick={() => setEndTarget(null)}>{t("Hủy", "Cancel")}</button><button className="danger-button" disabled={ending} onClick={end}>{ending ? t("Đang kết thúc…", "Closing…") : t("Kết thúc phiên", "End session")}</button></div></Dialog>}
  </div>;
};
