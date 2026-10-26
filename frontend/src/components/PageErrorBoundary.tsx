import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { useLanguage } from "@/context/LanguageContext";

class ErrorBoundary extends React.Component<{ children: React.ReactNode; fallback: React.ReactNode; resetKey: string }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidUpdate(previous: Readonly<typeof this.props>) {
    if (previous.resetKey !== this.props.resetKey && this.state.failed) this.setState({ failed: false });
  }
  render() { return this.state.failed ? this.props.fallback : this.props.children; }
}

export function PageErrorBoundary({ children }: { children: React.ReactNode }) {
  const { t } = useLanguage();
  const location = useLocation();
  return <ErrorBoundary resetKey={location.pathname} fallback={<section className="page-recovery" role="alert">
    <AlertCircle size={26} aria-hidden="true" />
    <h1>{t("Không thể hiển thị trang này", "This page could not be displayed")}</h1>
    <p>{t("Hãy tải lại trang để thử lại. Bạn cũng có thể tiếp tục từ trang tổng quan.", "Reload to try again, or continue from the overview.")}</p>
    <div className="page-actions"><button type="button" className="primary-button" onClick={() => window.location.reload()}><RefreshCw size={15} />{t("Tải lại trang", "Reload page")}</button><Link className="secondary-button" to="/">{t("Về tổng quan", "Back to overview")}</Link></div>
  </section>}>{children}</ErrorBoundary>;
}
