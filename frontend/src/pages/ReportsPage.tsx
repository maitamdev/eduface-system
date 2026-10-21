import React, { useCallback, useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import { reportsApi } from "@/api/client";
import { useLanguage } from "@/context/LanguageContext";
import { useTheme } from "@/context/ThemeContext";
import { useResource } from "@/hooks/useResource";
import { matchesSearch } from "@/lib/format";
import { PageHeader, Section, RefreshButton, ErrorNotice, EmptyState, Table, SearchField, Pager } from "@/components/ProductUI";

export const ReportsPage: React.FC = () => {
  const { t, lang } = useLanguage();
  const { theme } = useTheme();
  const [days, setDays] = useState(30);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const dailyLoader = useCallback(() => reportsApi.getDaily(days), [days]);
  const peopleLoader = useCallback(() => reportsApi.getPersons(days), [days]);
  const heatmapLoader = useCallback(() => reportsApi.getHeatmap(Math.min(days, 14)), [days]);
  const daily = useResource(dailyLoader, []);
  const people = useResource(peopleLoader, []);
  const heatmap = useResource(heatmapLoader, null);
  const filtered = people.data.filter((person) => matchesSearch(search, person.name, person.department));
  const pages = Math.max(1, Math.ceil(filtered.length / 20));
  const currentPage = Math.min(page, pages);
  const rows = filtered.slice((currentPage - 1) * 20, currentPage * 20);
  const lowAttendance = people.data.filter((person) => person.is_defaulter).length;
  const checkins = daily.data.reduce((sum, day) => sum + day.total_present, 0);
  const chart = daily.data.map((day) => ({ ...day, label: new Date(`${day.date}T12:00:00`).toLocaleDateString(lang === "vi" ? "vi-VN" : "en-GB", { day: "2-digit", month: "2-digit" }) }));
  const reload = () => { void daily.reload(); void people.reload(); void heatmap.reload(); };
  return <div className="product-page">
    <PageHeader title={t("Báo cáo chuyên cần", "Attendance reports")} description={t("Theo dõi lượt có mặt và tỷ lệ tham gia theo người.", "Review daily activity and individual participation.")}><div className="chart-range" aria-label={t("Khoảng báo cáo", "Report range")}>{[7, 14, 30, 90].map((value) => <button key={value} aria-pressed={days === value} onClick={() => { setDays(value); setPage(1); }}>{value} {t("ngày", "days")}</button>)}</div><RefreshButton onClick={reload} loading={daily.loading || people.loading || heatmap.loading} /></PageHeader>
    <dl className="metric-strip three-metrics"><div><dt>{t("Lượt có mặt", "Check-ins")}</dt><dd>{daily.loading ? "…" : daily.error ? "–" : checkins.toLocaleString(lang === "vi" ? "vi-VN" : "en-GB")}</dd><p>{t(`Trong ${days} ngày`, `Over ${days} days`)}</p></div><div><dt>{t("Có thống kê cá nhân", "People with statistics")}</dt><dd>{people.loading ? "…" : people.error ? "–" : people.data.length}</dd><p>{t("Hồ sơ trong kỳ báo cáo", "Profiles in the reporting period")}</p></div><div><dt>{t("Chuyên cần dưới 75%", "Attendance below 75%")}</dt><dd>{people.loading ? "…" : people.error ? "–" : lowAttendance}</dd><p>{t("Cần theo dõi thêm", "Profiles to review")}</p></div></dl>
    <Section title={t("Lượt có mặt theo ngày", "Daily check-ins")}><ErrorNotice message={daily.error} retry={daily.reload} />{daily.data.length ? <div className="report-chart" role="img" aria-label={t("Biểu đồ lượt có mặt theo ngày", "Daily attendance bar chart")}><ResponsiveContainer width="100%" height="100%"><BarChart data={chart} margin={{ top: 10, right: 8, left: -15, bottom: 0 }}><CartesianGrid vertical={false} stroke={theme === "dark" ? "#363a3f" : "#e2e5e8"} /><XAxis dataKey="label" axisLine={false} tickLine={false} minTickGap={30} fontSize={10} /><YAxis axisLine={false} tickLine={false} allowDecimals={false} fontSize={10} /><Tooltip cursor={{ fill: "var(--ui-soft)" }} contentStyle={{ background: "var(--ui-surface)", color: "var(--ui-text)", border: "1px solid var(--ui-border)", borderRadius: 4, fontSize: 12 }} /><Bar dataKey="total_present" name={t("Có mặt", "Present")} fill={theme === "dark" ? "#a3a9b1" : "#77818e"} maxBarSize={26} isAnimationActive={false} /></BarChart></ResponsiveContainer></div> : <EmptyState loading={daily.loading}>{daily.error ? t("Thống kê chưa tải được.", "Statistics unavailable.") : t("Chưa có dữ liệu trong kỳ này.", "No data in this period.")}</EmptyState>}</Section>
    <Section title={t("Chuyên cần theo người", "Individual attendance")} action={<SearchField label={t("Tìm tên hoặc lớp…", "Search name or department…")} value={search} onChange={(value) => { setSearch(value); setPage(1); }} />}><ErrorNotice message={people.error} retry={people.reload} /><Table label={t("Thống kê cá nhân", "Individual statistics")}><thead><tr><th>{t("Họ và tên", "Name")}</th><th>{t("Khoa / Lớp", "Department")}</th><th className="align-right">{t("Có mặt", "Present")}</th><th className="align-right">{t("Tổng phiên", "Sessions")}</th><th className="align-right">{t("Tỷ lệ", "Rate")}</th><th>{t("Đánh giá", "Standing")}</th></tr></thead><tbody>{rows.map((person) => <tr key={person.person_id}><td className="cell-strong">{person.name}</td><td>{person.department || "–"}</td><td className="align-right numeric-cell">{person.present_count}</td><td className="align-right numeric-cell">{person.total_sessions}</td><td className="align-right numeric-cell">{person.attendance_rate}%</td><td className={person.is_defaulter ? "warning-text" : "attendance-status"}>{person.is_defaulter ? t("Dưới 75%", "Below 75%") : t("Đạt", "On track")}</td></tr>)}</tbody></Table>{!rows.length && <EmptyState loading={people.loading}>{people.error ? t("Thống kê cá nhân chưa tải được.", "Individual statistics unavailable.") : t("Không có kết quả phù hợp.", "No matching results.")}</EmptyState>}<Pager page={currentPage} pages={pages} count={filtered.length} onChange={setPage} /></Section>
    <Section title={t("Lịch có mặt", "Attendance calendar")} description={t(`Hiển thị tối đa ${Math.min(days, 14)} ngày gần nhất và 50 người đầu tiên. Có mặt: ✓ · Không có bản ghi: × · Không áp dụng: –`, `Latest ${Math.min(days, 14)} days, first 50 people. Present: ✓ · No record: × · Not applicable: –`)}><ErrorNotice message={heatmap.error} retry={heatmap.reload} />{heatmap.data?.persons.length ? <Table label={t("Lịch có mặt theo người", "Attendance calendar by person")}><thead><tr><th>{t("Họ và tên", "Name")}</th>{heatmap.data.dates.map((date) => <th key={date} className="align-center">{date.slice(5)}</th>)}</tr></thead><tbody>{heatmap.data.persons.slice(0, 50).map((person) => <tr key={person.person_id}><td className="cell-strong">{person.name}</td>{person.data.map((value, index) => <td key={index} className={`align-center ${value === 1 ? "attendance-status" : value === 0 ? "warning-text" : "muted"}`} title={`${person.name} · ${heatmap.data!.dates[index]}`}>{value === 1 ? "✓" : value === 0 ? "×" : "–"}</td>)}</tr>)}</tbody></Table> : <EmptyState loading={heatmap.loading}>{heatmap.error ? t("Lịch chưa tải được.", "Calendar unavailable.") : t("Chưa có dữ liệu.", "No data available.")}</EmptyState>}</Section>
  </div>;
};
