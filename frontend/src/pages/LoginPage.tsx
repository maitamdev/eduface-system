import React, { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ScanFace, LockKeyhole, User, Eye, EyeOff, Loader2, Globe, Sun, Moon, Wifi, WifiOff, AlertCircle, ArrowRight, ArrowUpRight } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useTheme } from "@/context/ThemeContext";
import { healthApi, authApi } from "@/api/client";
import { requestGoogleAccessToken, type GoogleConfiguration } from "@/auth/google";
import { safeReturnPath } from "@/auth/microsoft";

const GoogleMark: React.FC = () => (
  <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true" className="shrink-0">
    <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
    <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
    <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
    <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
  </svg>
);

export const LoginPage: React.FC = () => {
  const { login, loginGoogle, isAuthenticated, user } = useAuth();
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
  const [google, setGoogle] = useState<GoogleConfiguration | null>(null);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [imageFailed, setImageFailed] = useState(false);
  const returnPath = safeReturnPath((location.state as { from?: { pathname?: string } } | null)?.from?.pathname);

  useEffect(() => {
    if (isAuthenticated) navigate(user?.role === "student" ? "/student" : returnPath, { replace: true });
  }, [isAuthenticated, user?.role, navigate, returnPath]);

  useEffect(() => {
    let active = true;
    healthApi.check().then(() => { if (active) setBackendState("online"); }).catch(() => { if (active) setBackendState("offline"); });
    void authApi.googleConfig().then((config) => {
      if (active) setGoogle(config);
    }).catch(() => {
      if (active) setGoogle({ enabled: false, client_id: "" });
    });
    return () => { active = false; };
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (submitting || googleLoading) return;
    if (!username.trim() || !password.trim()) { setError(t("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.", "Please enter both username and password.")); return; }
    setError(null); setSubmitting(true);
    try { await login(username.trim(), password); }
    catch (err) { setError(err instanceof Error ? err.message : t("Sai thông tin đăng nhập hoặc không kết nối được máy chủ.", "Invalid credentials or server unreachable.")); }
    finally { setSubmitting(false); }
  };

  const handleGoogle = async () => {
    if (!google?.enabled || googleLoading || submitting) return;
    setGoogleLoading(true); setError(null);
    try {
      const accessToken = await requestGoogleAccessToken(google.client_id);
      await loginGoogle(accessToken);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("Không thể đăng nhập bằng Google.", "Google sign-in failed."));
    } finally {
      setGoogleLoading(false);
    }
  };

  const busy = submitting || googleLoading;
  return <div className="login-page">
    <header className="login-header">
      <Link to="/login" className="brand-lockup" aria-label="EduFace"><span className="brand-symbol"><ScanFace size={25} strokeWidth={1.7} /></span><span className="brand-wordmark">Edu<span>Face</span></span></Link>
      <div className="login-utilities"><button className="icon-button language-button" onClick={toggleLang} aria-label={t("Chuyển sang Tiếng Anh", "Switch to Vietnamese")}><Globe size={16} /><span>{lang === "vi" ? "Tiếng Việt" : "English"}</span></button><button className="icon-button" onClick={toggleTheme} aria-label={t("Đổi giao diện Sáng / Tối", "Toggle Light / Dark mode")}>{theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}</button></div>
    </header>
    <main className="login-split">
      <section className={`login-visual ${imageFailed ? "image-unavailable" : ""}`} aria-label={t("Giới thiệu EduFace", "About EduFace")}>
        {!imageFailed && <img src="/images/eduface-campus.png" width="1152" height="1536" alt={t("Sinh viên bước vào lớp học trong khuôn viên đại học", "Students entering a university classroom")} onError={() => setImageFailed(true)} />}
        <div className="login-visual-caption"><p className="login-visual-label">EDUFACE / CAMPUS</p><h2>{t("Bắt đầu từ\nsự có mặt.", "It starts with\nshowing up.")}</h2><p>{t("Điểm danh, quản lý lớp và theo dõi chuyên cần trong cùng một không gian.", "Attendance, classes and participation. Together in one workspace.")}</p><span>{t("Ảnh minh họa được tạo bằng AI", "AI-generated illustration")}</span></div>
      </section>
      <section className="login-form-panel" aria-labelledby="login-heading"><div className="login-form-wrap">
        <p className="login-form-eyebrow">{t("CỔNG ĐIỂM DANH", "ATTENDANCE PORTAL")}</p><h1 id="login-heading">{t("Chào mừng trở lại", "Welcome back")}</h1><p className="login-intro">{t("Đăng nhập để tiếp tục với EduFace.", "Sign in to continue to EduFace.")}</p>
        <button className="microsoft-signin" type="button" disabled={!google?.enabled || busy} onClick={handleGoogle} aria-describedby="google-login-hint"><GoogleMark />{googleLoading ? t("Đang đăng nhập…", "Signing in…") : t("Tiếp tục với Google", "Continue with Google")}</button>
        <p id="google-login-hint" className="microsoft-login-hint">{google?.enabled ? t("Dùng tài khoản Google (@gmail.com hoặc @dhv.edu.vn) của bạn.", "Use your Google account (@gmail.com or @dhv.edu.vn).") : google ? t("Google chưa được cấu hình (thêm GOOGLE_CLIENT_ID).", "Google sign-in has not been configured yet.") : t("Đang kiểm tra đăng nhập Google…", "Checking Google sign-in…")}</p>
        <div className="login-method-divider"><span>{t("hoặc dùng tài khoản EduFace", "or use your EduFace account")}</span></div>
        {error && <div className="login-error" role="alert"><AlertCircle size={17} /><span>{error}</span></div>}
        <form onSubmit={handleSubmit} className="login-form">
          <div><label htmlFor="login-username">{t("Tên đăng nhập", "Username")}</label><div className="login-input-wrap"><User size={17} /><input id="login-username" name="username" autoComplete="username" type="text" value={username} onChange={(event) => setUsername(event.target.value)} placeholder={t("Nhập tên đăng nhập", "Enter your username")} disabled={busy} required /></div></div>
          <div><label htmlFor="login-password">{t("Mật khẩu", "Password")}</label><div className="login-input-wrap"><LockKeyhole size={17} /><input id="login-password" name="password" autoComplete="current-password" type={showPass ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} placeholder={t("Nhập mật khẩu", "Enter your password")} disabled={busy} required /><button type="button" className="icon-button" aria-label={showPass ? t("Ẩn mật khẩu", "Hide password") : t("Hiện mật khẩu", "Show password")} aria-pressed={showPass} onClick={() => setShowPass((previous) => !previous)}>{showPass ? <EyeOff size={17} /> : <Eye size={17} />}</button></div></div>
          <button type="submit" disabled={busy} className="primary-button login-submit">{submitting ? <><Loader2 size={17} className="animate-spin" />{t("Đang xác thực…", "Signing in…")}</> : <>{t("Đăng nhập", "Sign in")}<ArrowRight size={17} /></>}</button>
        </form>
        <p className={`login-connection connection-status is-${backendState}`} role="status">{backendState === "online" ? <><Wifi size={13} />{t("Máy chủ đã sẵn sàng", "Server is ready")}</> : backendState === "checking" ? <><Loader2 size={13} className="animate-spin" />{t("Đang kết nối máy chủ…", "Connecting to the server…")}</> : <><WifiOff size={13} />{t("Chưa kết nối máy chủ", "Server is unavailable")}</>}</p>
        {import.meta.env.DEV && <Link to="/design-preview" className="login-preview-link">{t("Xem thử giao diện", "Explore the demo")}<ArrowUpRight size={14} /></Link>}
      </div><p className="login-account-help">{t("Chưa có tài khoản? Liên hệ quản trị viên trường hoặc đơn vị của bạn.", "Need an account? Contact your school or organization administrator.")}</p></section>
    </main>
    <p className="login-bottom-note">EduFace · {t("Hệ thống quản lý điểm danh", "Attendance management system")}</p>
  </div>;
};
