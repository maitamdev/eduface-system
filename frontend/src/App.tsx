import React, { lazy, Suspense, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "@/context/ThemeContext";
import { LanguageProvider } from "@/context/LanguageContext";
import { AuthProvider } from "@/context/AuthContext";
import { ToastProvider } from "@/context/ToastContext";
import { AppShell } from "@/components/AppShell";
import { RequireAuth, RequireAdmin } from "@/components/RouteGuards";
import { healthApi } from "@/api/client";
import { PageErrorBoundary } from "@/components/PageErrorBoundary";

const LoginPage = lazy(() => import("@/pages/LoginPage").then((m) => ({ default: m.LoginPage })));
const DashboardPage = lazy(() => import("@/pages/DashboardPage").then((m) => ({ default: m.DashboardPage })));
const LiveScannerPage = lazy(() => import("@/pages/LiveScannerPage").then((m) => ({ default: m.LiveScannerPage })));
const SessionsPage = lazy(() => import("@/pages/SessionsPage").then((m) => ({ default: m.SessionsPage })));
const RecordsPage = lazy(() => import("@/pages/RecordsPage").then((m) => ({ default: m.RecordsPage })));
const PeoplePage = lazy(() => import("@/pages/PeoplePage").then((m) => ({ default: m.PeoplePage })));
const EnrollPage = lazy(() => import("@/pages/EnrollPage").then((m) => ({ default: m.EnrollPage })));
const ReportsPage = lazy(() => import("@/pages/ReportsPage").then((m) => ({ default: m.ReportsPage })));
const SystemAdminPage = lazy(() => import("@/pages/SystemAdminPage").then((m) => ({ default: m.SystemAdminPage })));
const StudentPortalPage = lazy(() => import("@/pages/StudentPortalPage").then((m) => ({ default: m.StudentPortalPage })));
const AcademicManagementPage = lazy(() => import("@/pages/AcademicManagementPage").then((m) => ({ default: m.AcademicManagementPage })));
const ToeicPage = lazy(() => import("@/features/toeic/ToeicPage").then((m) => ({ default: m.ToeicPage })));

const DesignPreviewPage = import.meta.env.DEV
  ? lazy(() => import("@/pages/DesignPreviewPage").then((module) => ({ default: module.DesignPreviewPage })))
  : null;

export const App: React.FC = () => {
  useEffect(() => {
    // Giữ kết nối Render luôn thức khi đang mở tab trình duyệt (ping mỗi 4 phút)
    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") healthApi.check().catch(() => {});
    }, 4 * 60 * 1000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <ThemeProvider>
      <LanguageProvider>
        <ToastProvider>
          <AuthProvider>
            <BrowserRouter>
              <PageErrorBoundary><Suspense fallback={<div role="status" className="panel-empty">EduFace…</div>}><Routes>
                <Route path="/login" element={<LoginPage />} />
                {DesignPreviewPage && <Route path="/design-preview/*" element={<Suspense fallback={<div role="status" className="panel-empty">EduFace…</div>}><DesignPreviewPage /></Suspense>} />}

                {/* Operator & Admin routes */}
                <Route path="/toeic" element={<RequireAuth><AppShell><ToeicPage /></AppShell></RequireAuth>} />
                <Route
                  path="/"
                  element={
                    <RequireAuth>
                      <AppShell>
                        <DashboardPage />
                      </AppShell>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/scanner"
                  element={
                    <RequireAuth>
                      <AppShell>
                        <LiveScannerPage />
                      </AppShell>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/sessions"
                  element={
                    <RequireAuth>
                      <AppShell>
                        <SessionsPage />
                      </AppShell>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/records"
                  element={
                    <RequireAuth>
                      <AppShell>
                        <RecordsPage />
                      </AppShell>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/student"
                  element={
                    <RequireAuth>
                      <AppShell>
                        <StudentPortalPage />
                      </AppShell>
                    </RequireAuth>
                  }
                />

                {/* Operator (Instructor) & Admin routes */}
                <Route
                  path="/people"
                  element={
                    <RequireAuth>
                      <AppShell>
                        <PeoplePage />
                      </AppShell>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/academic"
                  element={
                    <RequireAuth>
                      <AppShell>
                        <AcademicManagementPage />
                      </AppShell>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/reports"
                  element={
                    <RequireAuth>
                      <AppShell>
                        <ReportsPage />
                      </AppShell>
                    </RequireAuth>
                  }
                />

                {/* Admin-only routes */}
                <Route
                  path="/enroll"
                  element={
                    <RequireAuth>
                      <RequireAdmin>
                        <AppShell>
                          <EnrollPage />
                        </AppShell>
                      </RequireAdmin>
                    </RequireAuth>
                  }
                />
                <Route
                  path="/system"
                  element={
                    <RequireAuth>
                      <RequireAdmin>
                        <AppShell>
                          <SystemAdminPage />
                        </AppShell>
                      </RequireAdmin>
                    </RequireAuth>
                  }
                />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes></Suspense></PageErrorBoundary>
            </BrowserRouter>
          </AuthProvider>
        </ToastProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
};

export default App;
