import React, { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ScanFace, LockKeyhole, User, Eye, EyeOff, Loader2, Globe, Sun, Moon, Wifi, WifiOff, AlertCircle, ArrowRight, ArrowUpRight } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useTheme } from "@/context/ThemeContext";
import { healthApi } from "@/api/client";

export const LoginPage: React.FC = () => {
  const { login, isAuthenticated, user } = useAuth();
  const { lang, toggleLang, t } = useLanguage();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendState, setBackendState] = useState<"checking" | "online" | "offline">("checking");
  const fromPath = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname || "/";

  useEffect(() => {
    if (isAuthenticated) {
      navigate(user?.role === "student" ? "/student" : fromPath, { replace: true });
    }
  }, [isAuthenticated, user?.role, navigate, fromPath]);
  useEffect(() => {
    let active = true;
    healthApi.check().then(() => { if (active) setBackendState("online"); }).catch(() => { if (active) setBackendState("offline"); });
    return () => { active = false; };
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!username.trim() || !password.trim()) { setError(t("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.", "Please enter both username and password.")); return; }
    setError(null);
    setSubmitting(true);
    try { await login(username.trim(), password); navigate(fromPath, { replace: true }); }
    catch (err: unknown) { setError(err instanceof Error ? err.message : t("Sai thông tin đăng nhập hoặc không kết nối được máy chủ.", "Invalid credentials or server unreachable.")); }
    finally { setSubmitting(false); }
  };
  return <div className="login-page">
    <header className="login-header">
      <Link to="/login" className="brand-lockup" aria-label="EduFace"><span className="brand-symbol"><ScanFace size={25} strokeWidth={1.7} /></span><span className="brand-wordmark">Edu<span>Face</span></span></Link>
      <div className="login-utilities"><button className="icon-button language-button" onClick={toggleLang} aria-label={t("Chuyển sang Tiếng Anh", "Switch to Vietnamese")}><Globe size={16} /><span>{lang === "vi" ? "Tiếng Việt" : "English"}</span></button><button className="icon-button" onClick={toggleTheme} aria-label={t("Đổi giao diện Sáng / Tối", "Toggle Light / Dark mode")}>{theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}</button></div>
    </header>
      <main className="login-form-wrap"><h1>{t("Đăng nhập", "Sign in")}</h1><p className="login-intro">{t("Sử dụng tài khoản được quản trị viên cung cấp để truy cập hệ thống điểm danh.", "Use the account provided by your administrator to access attendance management.")}</p>
        {error && <div className="login-error" role="alert"><AlertCircle size={17} /><span>{error}</span></div>}
        <form onSubmit={handleSubmit} className="login-form">
          <div><label htmlFor="login-username">{t("Tên đăng nhập", "Username")}</label><div className="login-input-wrap"><User size={17} /><input id="login-username" name="username" autoComplete="username" type="text" value={username} onChange={(event) => setUsername(event.target.value)} placeholder={t("Nhập tên đăng nhập", "Enter your username")} required /></div></div>
          <div><label htmlFor="login-password">{t("Mật khẩu", "Password")}</label><div className="login-input-wrap"><LockKeyhole size={17} /><input id="login-password" name="password" autoComplete="current-password" type={showPass ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} placeholder={t("Nhập mật khẩu", "Enter your password")} required /><button type="button" className="icon-button" aria-label={showPass ? t("Ẩn mật khẩu", "Hide password") : t("Hiện mật khẩu", "Show password")} aria-pressed={showPass} onClick={() => setShowPass((previous) => !previous)}>{showPass ? <EyeOff size={17} /> : <Eye size={17} />}</button></div></div>
          <button type="submit" disabled={submitting} className="primary-button login-submit">{submitting ? <><Loader2 size={17} className="animate-spin" />{t("Đang xác thực…", "Signing in…")}</> : <>{t("Đăng nhập vào hệ thống", "Sign in")}<ArrowRight size={17} /></>}</button>
        </form>
        <p className={`login-connection connection-status is-${backendState}`} role="status">{backendState === "online" ? <><Wifi size={13} />{t("Máy chủ đã sẵn sàng", "Server is ready")}</> : backendState === "checking" ? <><Loader2 size={13} className="animate-spin" />{t("Đang kết nối máy chủ…", "Connecting to the server…")}</> : <><WifiOff size={13} />{t("Chưa kết nối máy chủ", "Server is unavailable")}</>}</p>
        {import.meta.env.DEV && <Link to="/design-preview" className="login-preview-link">{t("Xem thử giao diện với dữ liệu mẫu", "Explore the design with sample data")}<ArrowUpRight size={14} /></Link>}
      </main>
      <p className="login-bottom-note">EduFace · {t("Hệ thống quản lý điểm danh", "Attendance management system")}</p>
  </div>;
};

