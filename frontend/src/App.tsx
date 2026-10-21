import React, { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "@/context/ThemeContext";
import { LanguageProvider } from "@/context/LanguageContext";
import { AuthProvider } from "@/context/AuthContext";
import { ToastProvider } from "@/context/ToastContext";
import { AppShell } from "@/components/AppShell";
import { RequireAuth, RequireAdmin } from "@/components/RouteGuards";

import { LoginPage } from "@/pages/LoginPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { LiveScannerPage } from "@/pages/LiveScannerPage";
import { SessionsPage } from "@/pages/SessionsPage";
import { RecordsPage } from "@/pages/RecordsPage";
import { PeoplePage } from "@/pages/PeoplePage";
import { EnrollPage } from "@/pages/EnrollPage";
import { ReportsPage } from "@/pages/ReportsPage";
import { SystemAdminPage } from "@/pages/SystemAdminPage";
import { StudentPortalPage } from "@/pages/StudentPortalPage";

const DesignPreviewPage = import.meta.env.DEV
  ? lazy(() => import("@/pages/DesignPreviewPage").then((module) => ({ default: module.DesignPreviewPage })))
  : null;

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <ToastProvider>
          <AuthProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                {DesignPreviewPage && <Route path="/design-preview/*" element={<Suspense fallback={<div role="status" className="panel-empty">EduFace…</div>}><DesignPreviewPage /></Suspense>} />}

                {/* Operator & Admin routes */}
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

                {/* Admin-only routes */}
                <Route
                  path="/people"
                  element={
                    <RequireAuth>
                      <RequireAdmin>
                        <AppShell>
                          <PeoplePage />
                        </AppShell>
                      </RequireAdmin>
                    </RequireAuth>
                  }
                />
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
                  path="/reports"
                  element={
                    <RequireAuth>
                      <RequireAdmin>
                        <AppShell>
                          <ReportsPage />
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
              </Routes>
            </BrowserRouter>
          </AuthProvider>
        </ToastProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
};

export default App;
