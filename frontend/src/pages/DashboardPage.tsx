import React, { useCallback, useEffect, useRef, useState } from "react";
import { Link as RouterLink } from "react-router-dom";
import { appPath } from "@/lib/format";
import { Plus, ArrowRight, RefreshCw, CheckCircle2, AlertCircle, Search, X } from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import {
  dashboardApi, sessionsApi, reportsApi, type DashboardMetrics, type ActivityItem,
  type SessionOut, type DailyAttendanceStat,
} from "@/api/client";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useTheme } from "@/context/ThemeContext";

export interface DashboardSnapshot {
  metrics: DashboardMetrics | null;
  activity: ActivityItem[];
  sessions: SessionOut[];
  trend: DailyAttendanceStat[];
}
type Panel = "metrics" | "activity" | "sessions" | "trend";
const emptySnapshot: DashboardSnapshot = { metrics: null, activity: [], sessions: [], trend: [] };
const Link = (props: React.ComponentProps<typeof RouterLink>) => <RouterLink {...props} to={typeof props.to === "string" ? appPath(props.to) : props.to} />;
const normalize = (value: string) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d").replace(/Đ/g, "D").toLowerCase();

export const DashboardPage: React.FC<{ previewData?: DashboardSnapshot; previewRole?: "admin" | "operator" }> = ({ previewData, previewRole = "admin" }) => {
  const { role: authRole } = useAuth();
  const role = previewData ? previewRole : authRole;
  const { t, lang } = useLanguage();
  const { theme } = useTheme();
  const [data, setData] = useState<DashboardSnapshot>(previewData || emptySnapshot);
  const [errors, setErrors] = useState<Panel[]>([]);
  const [loading, setLoading] = useState(!previewData);
  const [refreshing, setRefreshing] = useState(false);
  const [days, setDays] = useState(7);
  const [search, setSearch] = useState("");
  const [updatedAt, setUpdatedAt] = useState<Date | null>(previewData ? new Date() : null);
  const requestRef = useRef(0);
  const locale = lang === "vi" ? "vi-VN" : "en-GB";
  const time = (value: string | Date) => new Date(value).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" });

  const fetchDashboard = useCallback(async (silent = false) => {
    if (previewData) { setData(previewData); setUpdatedAt(new Date()); return; }
    const requestId = ++requestRef.current;
    if (silent) setRefreshing(true); else setLoading(true);
    const results = await Promise.allSettled([
      dashboardApi.getMetrics(), dashboardApi.getActivity(), sessionsApi.list(true),
      role === "admin" ? reportsApi.getDaily(days) : Promise.resolve([] as DailyAttendanceStat[]),
    ] as const);
    if (requestId !== requestRef.current) return;
    const failed: Panel[] = [];
    const [metrics, activity, sessions, trend] = results;
    if (metrics.status === "rejected") failed.push("metrics");
    if (activity.status === "rejected") failed.push("activity");
    if (sessions.status === "rejected") failed.push("sessions");
    if (trend.status === "rejected") failed.push("trend");
    setData((previous) => ({
      metrics: metrics.status === "fulfilled" ? metrics.value : previous.metrics,
      activity: activity.status === "fulfilled" ? activity.value : previous.activity,
      sessions: sessions.status === "fulfilled" ? sessions.value : previous.sessions,
      trend: trend.status === "fulfilled" ? trend.value : previous.trend,
    }));
    setErrors(failed);
    if (!failed.length) setUpdatedAt(new Date());
    setLoading(false);
    setRefreshing(false);
  }, [role, days, previewData]);

  useEffect(() => {
    void fetchDashboard();
    if (previewData) return;
    const timer = setInterval(() => void fetchDashboard(true), 15000);
    return () => { clearInterval(timer); requestRef.current++; };
  }, [fetchDashboard, previewData]);

  const { metrics, activity, sessions, trend } = data;
  const chartData = trend.slice(-days).map((item) => ({
    day: new Date(`${item.date}T12:00:00`).toLocaleDateString(locale, { day: "2-digit", month: "2-digit" }),
    present: item.total_present,
  }));
  const totalCheckins = chartData.reduce((sum, item) => sum + item.present, 0);
  const metricValue = (value: number | undefined, percent = false) => loading ? "..." : value == null ? "–" : `${value.toLocaleString(locale)}${percent ? "%" : ""}`;
  const filteredActivity = activity.filter((item) => normalize(`${item.person_name} ${item.department || ""} ${item.session_label}`).includes(normalize(search.trim())));
  const kpis = [
    { label: t("Đã đăng ký", "Enrolled"), value: metricValue(metrics?.total_enrolled), detail: t("hồ sơ khuôn mặt", "face profiles") },
    { label: t("Có mặt hôm nay", "Present today"), value: metricValue(metrics?.present_today), detail: t("lượt xác nhận", "verified check-ins") },
    { label: t("Phiên hôm nay", "Sessions today"), value: metricValue(metrics?.sessions_today), detail: t("phiên điểm danh", "attendance sessions") },
    { label: t("Tỷ lệ có mặt", "Attendance rate"), value: metricValue(metrics?.attendance_rate, true), detail: t("trên tổng số đã đăng ký", "of enrolled profiles") },
  ];

  const panelState = (panel: Panel, emptyText: string) => <div className="panel-empty" role="status">
    {errors.includes(panel) && <AlertCircle size={20} />}
    {loading && <RefreshCw size={20} className="animate-spin" />}
    <p>{errors.includes(panel) ? t("Không tải được dữ liệu. Vui lòng thử lại.", "Could not load data. Please try again.") : loading ? t("Đang tải…", "Loading…") : emptyText}</p>
    {errors.includes(panel) && <button className="text-link" onClick={() => void fetchDashboard(true)} disabled={refreshing}>{t("Thử lại", "Try again")}</button>}
  </div>;

  return <div className="dashboard-page" aria-busy={loading}>
    <div className="dashboard-heading">
      <div><h1>{t("Tổng quan điểm danh", "Attendance overview")}</h1><p className="dashboard-date">{new Date().toLocaleDateString(locale, { weekday: "long", day: "2-digit", month: "long", year: "numeric" })}</p></div>
      <div className="dashboard-heading-actions">
        <button className="secondary-button" onClick={() => void fetchDashboard(true)} disabled={refreshing}><RefreshCw size={14} className={refreshing ? "animate-spin" : ""} />{t("Làm mới", "Refresh")}</button>
        <Link to={sessions.length ? `/scanner?sessionId=${encodeURIComponent(sessions[0].id)}` : "/scanner"} className="primary-button">{t("Mở máy quét", "Open scanner")}<ArrowRight size={15} /></Link>
      </div>
    </div>

    {errors.length > 0 && <div className="dashboard-error" role="alert"><AlertCircle size={16} /><span>{t("Một số dữ liệu chưa được cập nhật. Kiểm tra kết nối máy chủ rồi thử lại.", "Some data could not be updated. Check the server connection and retry.")}</span><button onClick={() => void fetchDashboard(true)} disabled={refreshing}>{t("Thử lại", "Retry")}</button></div>}

    <dl className="metric-strip">{kpis.map((item) => <div key={item.label}><dt>{item.label}</dt><dd>{item.value}</dd><p>{item.detail}</p></div>)}</dl>

    <section className="session-section">
      <div className="section-heading"><h2>{t("Phiên đang mở", "Active sessions")}<span className="section-count">{sessions.length}</span></h2><Link to="/sessions" className="text-link"><Plus size={14} />{t("Tạo phiên", "New session")}</Link></div>
      {sessions.length ? <div className="session-rows">{sessions.slice(0, 3).map((session) => <div className="session-row" key={session.id}>
        <span className="session-start">{time(session.started_at)}</span>
        <div className="session-title"><h3>{session.label}</h3><p>{session.department || t("Tất cả khoa / lớp", "All departments")}</p></div>
        <span className="session-status"><span className="status-dot" />{t("Đang mở", "Open")}</span>
        <Link to={`/scanner?sessionId=${encodeURIComponent(session.id)}`} className="secondary-button" aria-label={t(`Điểm danh: ${session.label}`, `Check in: ${session.label}`)}>{t("Điểm danh", "Check in")}<ArrowRight size={14} /></Link>
      </div>)}</div> : panelState("sessions", t("Chưa có phiên đang mở. Tạo phiên để bắt đầu điểm danh.", "No sessions open. Create a session to start checking in."))}
      {sessions.length > 3 && <Link to="/sessions" className="text-link session-view-all">{t(`Xem tất cả ${sessions.length} phiên`, `View all ${sessions.length} sessions`)}<ArrowRight size={14} /></Link>}
    </section>

    <section className="activity-section">
      <div className="section-heading"><div><h2>{t("Bản ghi mới nhất", "Latest records")}</h2><p>{t("Các lượt điểm danh vừa được ghi nhận", "The most recent attendance check-ins")}</p></div><Link to="/records" className="text-link">{t("Mở sổ điểm danh", "View all records")}<ArrowRight size={14} /></Link></div>
      <div className="activity-tools"><div className="record-search"><Search size={15} /><input aria-label={t("Tìm trong bản ghi mới nhất", "Search latest records")} value={search} onChange={(event) => setSearch(event.target.value)} placeholder={t("Tìm theo tên, lớp hoặc phiên…", "Search name, department or session…")} />{search && <button className="icon-button" onClick={() => setSearch("")} aria-label={t("Xóa tìm kiếm", "Clear search")}><X size={14} /></button>}</div><span className="record-count" role="status">{loading ? t("Đang tải…", "Loading…") : t(`${filteredActivity.length} bản ghi${search ? " phù hợp" : " gần nhất"}`, `${filteredActivity.length} ${search ? "matching" : "latest"} records`)}</span></div>
      {activity.length ? <div className="activity-table-scroll"><table className="activity-table"><thead><tr><th scope="col">{t("Họ và tên", "Name")}</th><th scope="col">{t("Khoa / Lớp", "Department")}</th><th scope="col">{t("Phiên điểm danh", "Session")}</th><th scope="col">{t("Giờ vào", "Check-in")}</th><th scope="col">{t("Trạng thái", "Status")}</th><th scope="col">{t("Độ tin cậy", "Confidence")}</th></tr></thead><tbody>{filteredActivity.map((item) => <tr key={item.id}>
        <td className="person-name">{item.person_name}</td><td>{item.department || "–"}</td><td>{item.session_label}</td><td className="numeric-cell">{time(item.marked_at)}</td><td><span className={item.status === "present" ? "attendance-status" : "attendance-status status-neutral"}>{item.status === "present" && <CheckCircle2 size={12} />}{item.status === "present" ? t("Có mặt", "Present") : item.status}</span></td><td className="numeric-cell">{item.confidence != null ? `${Math.round(item.confidence * 100)}%` : "–"}</td>
      </tr>)}{!filteredActivity.length && <tr><td colSpan={6} className="no-search-results">{t("Không có bản ghi phù hợp.", "No matching records.")}</td></tr>}</tbody></table></div> : panelState("activity", t("Chưa ghi nhận lượt điểm danh nào.", "No attendance check-ins recorded yet."))}
      <div className="records-footer"><span>{previewData ? t("Dữ liệu mẫu", "Sample data") : errors.length ? t("Dữ liệu có thể chưa cập nhật", "Data may be out of date") : t("Cập nhật mỗi 15 giây", "Updates every 15 seconds")}</span><span>{updatedAt && `${t("Cập nhật lúc", "Updated at")} ${time(updatedAt)}`}</span></div>
    </section>

    {role === "admin" && <section className="trend-section">
      <div className="section-heading"><div><h2>{t("Lượt có mặt theo ngày", "Daily attendance")}</h2><p>{t(`${totalCheckins.toLocaleString(locale)} lượt trong ${days} ngày`, `${totalCheckins.toLocaleString(locale)} check-ins over ${days} days`)}</p></div><div className="chart-range" aria-label={t("Khoảng thời gian biểu đồ", "Chart date range")}>{[7, 14].map((range) => <button key={range} aria-pressed={days === range} onClick={() => setDays(range)}>{range} {t("ngày", "days")}</button>)}</div></div>
      <div className="attendance-chart" role="img" aria-label={t(`Biểu đồ điểm danh ${days} ngày, tổng ${totalCheckins} lượt có mặt`, `${days}-day attendance chart, ${totalCheckins} total check-ins`)}>
        {chartData.length ? <ResponsiveContainer width="100%" height="100%"><BarChart data={chartData} barSize={24} margin={{ top: 8, right: 4, left: -15, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={theme === "dark" ? "#343638" : "#ebebeb"} />
          <XAxis dataKey="day" tick={{ fill: theme === "dark" ? "#a5a5a5" : "#717171", fontSize: 11 }} axisLine={false} tickLine={false} tickMargin={10} minTickGap={22} />
          <YAxis allowDecimals={false} tick={{ fill: theme === "dark" ? "#a5a5a5" : "#717171", fontSize: 11 }} axisLine={false} tickLine={false} tickCount={3} />
          <Tooltip cursor={{ fill: theme === "dark" ? "#252729" : "#f5f5f5" }} contentStyle={{ background: "var(--ui-surface)", color: "var(--ui-text)", border: "1px solid var(--ui-border)", borderRadius: 4, fontSize: 12 }} />
          <Bar dataKey="present" name={t("Có mặt", "Present")} fill={theme === "dark" ? "#a3a9b1" : "#77818e"} radius={[2, 2, 0, 0]} isAnimationActive={false} />
        </BarChart></ResponsiveContainer> : panelState("trend", t("Chưa có dữ liệu thống kê.", "No statistics available."))}
      </div><Link to="/reports" className="text-link">{t("Xem báo cáo chi tiết", "View detailed report")}<ArrowRight size={14} /></Link>
    </section>}
  </div>;
};
