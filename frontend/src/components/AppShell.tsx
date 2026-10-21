import React, { useEffect, useRef, useState } from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, ScanFace, CalendarClock, ClipboardList, Users, UserPlus,
  BarChart3, ShieldCheck, Sun, Moon, LogOut, Menu, X, Globe, Wifi,
  WifiOff, Loader2, ChevronRight,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useTheme } from "@/context/ThemeContext";
import { healthApi } from "@/api/client";
import { appPath } from "@/lib/format";

export const AppShell: React.FC<{ children: React.ReactNode; preview?: boolean; previewRole?: "admin" | "operator" }> = ({ children, preview = false, previewRole = "admin" }) => {
  const { user, role: authRole, logout } = useAuth();
  const role = preview ? previewRole : authRole;
  const { lang, toggleLang, t } = useLanguage();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">("checking");
  const drawerRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLButtonElement>(null);

  useEffect(() => { setMobileOpen(false); }, [location.pathname]);

  useEffect(() => {
    if (!mobileOpen) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    drawerRef.current?.querySelector<HTMLButtonElement>("button")?.focus();
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMobileOpen(false);
      if (event.key !== "Tab") return;
      const elements = drawerRef.current?.querySelectorAll<HTMLElement>('a[href], button:not([disabled])');
      if (!elements?.length) return;
      const first = elements[0];
      const last = elements[elements.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener("keydown", handleKey);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", handleKey);
      menuRef.current?.focus();
    };
  }, [mobileOpen]);

  useEffect(() => {
    if (preview) return;
    let mounted = true;
    const check = async () => {
      try { await healthApi.check(); if (mounted) setApiStatus("online"); }
      catch { if (mounted) setApiStatus("offline"); }
    };
    void check();
    const timer = setInterval(check, 30000);
    return () => { mounted = false; clearInterval(timer); };
  }, [preview]);

  const operationLinks = [
    { to: "/", icon: LayoutDashboard, label: t("Tổng quan", "Dashboard"), end: true },
    { to: "/scanner", icon: ScanFace, label: t("Máy quét AI trực tiếp", "Live AI Scanner"), badge: "LIVE" },
    { to: "/sessions", icon: CalendarClock, label: t("Phiên điểm danh", "Sessions") },
    { to: "/records", icon: ClipboardList, label: t("Sổ bản ghi điểm danh", "Attendance Logs") },
  ];
  const adminLinks = [
    { to: "/people", icon: Users, label: t("Danh bạ sinh viên / NS", "People Directory") },
    { to: "/enroll", icon: UserPlus, label: t("Đăng ký khuôn mặt", "Face Enrollment") },
    { to: "/reports", icon: BarChart3, label: t("Báo cáo & Chuyên cần", "Analytics & Reports") },
    { to: "/system", icon: ShieldCheck, label: t("Tài khoản & Hệ thống", "Users & Diagnostics") },
  ];
  const currentPath = preview ? location.pathname.replace(/^\/design-preview/, "") || "/" : location.pathname;
  const currentPage = [...operationLinks, ...adminLinks].find((item) => item.to === currentPath)?.label || t("Tổng quan", "Dashboard");
  const handleLogout = () => { if (!preview) logout(); navigate("/login"); };

  const renderLinks = (items: typeof operationLinks) => items.map((item) => {
    const Icon = item.icon;
    return <NavLink key={item.to} to={appPath(item.to)} end={item.end}
      className={({ isActive }) => `workspace-nav-link ${isActive ? "is-active" : ""}`}>
      <Icon size={18} strokeWidth={1.7} /><span>{item.label}</span>
      {item.badge && <span className="nav-live">{item.badge}</span>}
    </NavLink>;
  });

  const sidebar = (mobile = false) => <div className="workspace-sidebar-content">
    <div className="workspace-brand">
      <Link to={preview ? "/design-preview" : "/"} className="brand-lockup" aria-label="EduFace">
        <span className="brand-symbol"><ScanFace size={25} strokeWidth={1.7} /></span>
        <span className="brand-wordmark">Edu<span>Face</span></span>
      </Link>
      {mobile && <button className="icon-button" aria-label={t("Đóng menu", "Close menu")} onClick={() => setMobileOpen(false)}><X size={20} /></button>}
    </div>
    <p className="workspace-caption">{t("Quản lý điểm danh", "Attendance management")}</p>
    <div className="workspace-nav-scroll">
      <p className="nav-section-label">{t("Vận hành điểm danh", "Attendance Operations")}</p>
      <nav aria-label={t("Vận hành điểm danh", "Attendance Operations")}>{renderLinks(operationLinks)}</nav>
      {role === "admin" && <><p className="nav-section-label admin-section">{t("Quản trị & Học vụ", "Administration")}</p><nav aria-label={t("Quản trị & Học vụ", "Administration")}>{renderLinks(adminLinks)}</nav></>}
    </div>
    <div className="sidebar-bottom">
      <div className="sidebar-profile"><div><strong>{preview ? t("Bản xem thử", "Design preview") : user?.username || "User"}</strong><small>{role === "admin" ? t("Quản trị viên", "Administrator") : t("Vận hành viên", "Operator")}</small></div><button className="icon-button" onClick={handleLogout} aria-label={t("Đăng xuất", "Sign out")}><LogOut size={17} /></button></div>
    </div>
  </div>;

  return <div className="workspace">
    <a href="#main-content" className="skip-link">{t("Đến nội dung chính", "Skip to content")}</a>
    <aside className="workspace-sidebar">{sidebar()}</aside>
    {mobileOpen && <div className="mobile-drawer-backdrop" onClick={() => setMobileOpen(false)}><div ref={drawerRef} role="dialog" aria-modal="true" aria-label={t("Menu điều hướng", "Navigation menu")} className="mobile-drawer" onClick={(event) => event.stopPropagation()}>{sidebar(true)}</div></div>}
    <div className="workspace-body">
      <header className="workspace-topbar">
        <div className="topbar-breadcrumb"><button ref={menuRef} className="icon-button mobile-menu-button" aria-label={t("Mở menu", "Open menu")} aria-expanded={mobileOpen} onClick={() => setMobileOpen(true)}><Menu size={21} /></button><span className="breadcrumb-parent">{t("Điểm danh", "Attendance")}</span><ChevronRight size={14} className="breadcrumb-parent" /><strong>{currentPage}</strong></div>
        <div className="topbar-utilities">
          <span role="status" className={`connection-status ${preview ? "is-preview" : `is-${apiStatus}`}`}>
            {preview ? <><span className="status-dot" />{t("Dữ liệu mẫu", "Sample data")}</> : apiStatus === "online" ? <><Wifi size={14} /><span>{t("Đã kết nối", "Connected")}</span></> : apiStatus === "checking" ? <><Loader2 size={14} className="animate-spin" /><span>{t("Đang kết nối", "Connecting")}</span></> : <><WifiOff size={14} /><span>{t("Mất kết nối", "Disconnected")}</span></>}
          </span>
          <span className="toolbar-divider" />
          <button className="icon-button language-button" onClick={toggleLang} aria-label={t("Chuyển sang Tiếng Anh", "Switch to Vietnamese")}><Globe size={17} /><span>{lang.toUpperCase()}</span></button>
          <button className="icon-button" onClick={toggleTheme} aria-label={t("Đổi giao diện Sáng / Tối", "Toggle Light / Dark mode")}>{theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}</button>
        </div>
      </header>
      <main id="main-content" tabIndex={-1} className="workspace-main">{children}</main>
    </div>
  </div>;
};
