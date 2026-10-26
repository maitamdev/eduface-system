import React, { useState } from "react";
import { useLocation, Navigate } from "react-router-dom";
import { AppShell } from "@/components/AppShell";
import { DashboardPage } from "@/pages/DashboardPage";
import { SessionsPage } from "@/pages/SessionsPage";
import { RecordsPage } from "@/pages/RecordsPage";
import { PeoplePage } from "@/pages/PeoplePage";
import { EnrollPage } from "@/pages/EnrollPage";
import { LiveScannerPage } from "@/pages/LiveScannerPage";
import { ReportsPage } from "@/pages/ReportsPage";
import { SystemAdminPage } from "@/pages/SystemAdminPage";
import { StudentPortalPage } from "@/pages/StudentPortalPage";
import { AcademicManagementPage } from "@/pages/AcademicManagementPage";
import { ToeicPage } from "@/features/toeic/ToeicPage";
import { useLanguage } from "@/context/LanguageContext";
import { resetPreviewData, previewSnapshot } from "@/preview/mockApi";

export const DesignPreviewPage: React.FC = () => {
  const { t } = useLanguage();
  const { pathname } = useLocation();
  const [role, setRole] = useState<"admin" | "operator" | "student">("admin");
  const [empty, setEmpty] = useState(false);
  const [revision, setRevision] = useState(0);
  const path = pathname.replace(/^\/design-preview/, "") || "/";
  const pages: Record<string, React.ReactNode> = {
    "/toeic": <ToeicPage preview />,
    "/": <DashboardPage previewRole={role === "student" ? "operator" : role} previewData={previewSnapshot()} />,
    "/scanner": <LiveScannerPage />,
    "/sessions": <SessionsPage />,
    "/records": <RecordsPage previewRole={role === "student" ? "operator" : role} />,
    "/student": <StudentPortalPage previewRole={role} />,
    "/people": <PeoplePage />,
    "/enroll": <EnrollPage />,
    "/reports": <ReportsPage />,
    "/academic": <AcademicManagementPage />,
    "/system": <SystemAdminPage />,
  };
  if (!pages[path]) return <Navigate to="/design-preview" replace />;
  const allowed = path === "/toeic" || role === "admin" || (role === "operator" && ["/", "/scanner", "/sessions", "/records", "/student", "/people", "/reports", "/academic"].includes(path)) || (role === "student" && path === "/student");
  return <AppShell preview previewRole={role}>
    <div key={`${path}-${role}-${revision}`}>{allowed ? pages[path] : <p>{t("Màn hình này không dành cho vai trò đang chọn.", "This page is not available for the selected role.")}</p>}</div>
    <details className="preview-controls"><summary>{t("Tùy chọn xem thử · Dữ liệu mẫu", "Preview options · Sample data")}</summary><div className="preview-toolbar"><span>{t("Các màn hình dùng dữ liệu giả lập trong bộ nhớ. Không kết nối cơ sở dữ liệu, không mở camera hoặc gửi ảnh.", "Pages use fictional data in memory. No database connection, camera access or photo uploads.")}</span><div><label htmlFor="preview-role">{t("Vai trò", "Role")}</label><select id="preview-role" value={role} onChange={(event) => setRole(event.target.value as "admin" | "operator" | "student")}><option value="admin">Admin</option><option value="operator">Operator</option><option value="student">Student</option></select><label htmlFor="preview-data">{t("Dữ liệu", "Data")}</label><select id="preview-data" value={empty ? "empty" : "sample"} onChange={(event) => { const value = event.target.value === "empty"; resetPreviewData(value); setEmpty(value); setRevision((previous) => previous + 1); }}><option value="sample">{t("Mẫu", "Sample")}</option><option value="empty">{t("Trống", "Empty")}</option></select></div></div></details>
  </AppShell>;
};
