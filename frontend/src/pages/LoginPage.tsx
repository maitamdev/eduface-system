import React, { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ScanFace, LockKeyhole, User, Eye, EyeOff, Loader2, Globe, Sun, Moon, Wifi, WifiOff, AlertCircle, ArrowRight, ArrowUpRight } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useTheme } from "@/context/ThemeContext";
import { healthApi, authApi } from "@/api/client";
import { microsoftClient, handleMicrosoftRedirect, safeReturnPath, MICROSOFT_PENDING, type MicrosoftConfiguration } from "@/auth/microsoft";

export const LoginPage: React.FC = () => {
  const { login, loginMicrosoft, isAuthenticated, user } = useAuth();
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
  const [microsoft, setMicrosoft] = useState<MicrosoftConfiguration | null>(null);
  const [microsoftLoading, setMicrosoftLoading] = useState(false);
  const [imageFailed, setImageFailed] = useState(false);
  const [returnPath, setReturnPath] = useState(() => safeReturnPath((location.state as { from?: { pathname?: string } } | null)?.from?.pathname));
  const completed = useRef(false);
  const completeMicrosoft = useRef(loginMicrosoft);
  completeMicrosoft.current = loginMicrosoft;

  useEffect(() => {
    if (isAuthenticated) navigate(user?.role === "student" ? "/student" : returnPath, { replace: true });
  }, [isAuthenticated, user?.role, navigate, returnPath]);
  useEffect(() => {
    let active = true;
    healthApi.check().then(() => { if (active) setBackendState("online"); }).catch(() => { if (active) setBackendState("offline"); });
    void authApi.microsoftConfig().then(async (config) => {
      if (!active) return;
      setMicrosoft(config);
      if (!config.enabled) return;
      const result = await handleMicrosoftRedirect(config);
      if (!result || !active || completed.current) return;
      completed.current = true; setMicrosoftLoading(true);
      const pending = JSON.parse(sessionStorage.getItem(MICROSOFT_PENDING) || "null");
      sessionStorage.removeItem(MICROSOFT_PENDING);
      if (!pending || pending.challengeId !== result.state) throw new Error("Yêu cầu đăng nhập đã hết hạn. Vui lòng thử lại. / Sign-in request expired. Please try again.");
      setReturnPath(safeReturnPath(pending.returnPath));
      await completeMicrosoft.current(pending.challengeId, result.idToken);
    }).catch((err: unknown) => {
      if (!active) return;
      const pending = sessionStorage.getItem(MICROSOFT_PENDING);
      sessionStorage.removeItem(MICROSOFT_PENDING);
      if (pending || completed.current) setError(err instanceof Error ? err.message : "Microsoft sign-in failed.");
      setMicrosoft((previous) => previous || { enabled: false, client_id: "", tenant_id: "" });
    }).finally(() => { if (active) setMicrosoftLoading(false); });
    return () => { active = false; };
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (submitting || microsoftLoading) return;
    if (!username.trim() || !password.trim()) { setError(t("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.", "Please enter both username and password.")); return; }
    setError(null); setSubmitting(true);
    try { await login(username.trim(), password); }
    catch (err) { setError(err instanceof Error ? err.message : t("Sai thông tin đăng nhập hoặc không kết nối được máy chủ.", "Invalid credentials or server unreachable.")); }
    finally { setSubmitting(false); }
  };
  const handleMicrosoft = async () => {
    if (!microsoft?.enabled || microsoftLoading || submitting) return;
    setMicrosoftLoading(true); setError(null);
    try {
      const client = await microsoftClient(microsoft);
      const challenge = await authApi.microsoftChallenge();
      sessionStorage.setItem(MICROSOFT_PENDING, JSON.stringify({ challengeId: challenge.challenge_id, returnPath }));
      await client.loginRedirect({ scopes: ["openid", "profile"], nonce: challenge.nonce, state: challenge.challenge_id, prompt: "select_account", redirectStartPage: `${window.location.origin}/login` });
    } catch (err) {
      sessionStorage.removeItem(MICROSOFT_PENDING);
      setError(err instanceof Error ? err.message : t("Không thể đăng nhập Microsoft.", "Microsoft sign-in failed."));
      setMicrosoftLoading(false);
    }
  };
  const busy = submitting || microsoftLoading;
  return <div className="login-page">
    <header className="login-header">
      <Link to="/login" className="brand-lockup" aria-label="EduFace"><span className="brand-symbol"><ScanFace size={25} strokeWidth={1.7} /></span><span className="brand-wordmark">Edu<span>Face</span></span></Link>
      <div className="login-utilities"><button className="icon-button language-button" onClick={toggleLang} aria-label={t("Chuyển sang Tiếng Anh", "Switch to Vietnamese")}><Globe size={16} /><span>{lang === "vi" ? "Tiếng Việt" : "English"}</span></button><button className="icon-button" onClick={toggleTheme} aria-label={t("Đổi giao diện Sáng / Tối", "Toggle Light / Dark mode")}>{theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}</button></div>
    </header>
    <main className="login-split">
      <section className={`login-visual ${imageFailed ? "image-unavailable" : ""}`} aria-label={t("Giới thiệu EduFace", "About EduFace")}>
        {!imageFailed && <img src="/images/eduface-campus.png" width="1152" height="1536" fetchPriority="high" alt={t("Sinh viên bước vào lớp học trong khuôn viên đại học", "Students entering a university classroom")} onError={() => setImageFailed(true)} />}
        <div className="login-visual-caption"><p className="login-visual-label">EDUFACE / CAMPUS</p><h2>{t("Bắt đầu từ\nsự có mặt.", "It starts with\nshowing up.")}</h2><p>{t("Điểm danh, quản lý lớp và theo dõi chuyên cần trong cùng một không gian.", "Attendance, classes and participation. Together in one workspace.")}</p><span>{t("Ảnh minh họa được tạo bằng AI", "AI-generated illustration")}</span></div>
      </section>
      <section className="login-form-panel" aria-labelledby="login-heading"><div className="login-form-wrap">
        <p className="login-form-eyebrow">{t("CỔNG ĐIỂM DANH", "ATTENDANCE PORTAL")}</p><h1 id="login-heading">{t("Chào mừng trở lại", "Welcome back")}</h1><p className="login-intro">{t("Đăng nhập để tiếp tục với EduFace.", "Sign in to continue to EduFace.")}</p>
        <button className="microsoft-signin" type="button" disabled={!microsoft?.enabled || busy} onClick={handleMicrosoft} aria-describedby="microsoft-login-hint"><span className="microsoft-mark" aria-hidden="true"><i /><i /><i /><i /></span>{microsoftLoading ? t("Đang đăng nhập…", "Signing in…") : t("Tiếp tục với Microsoft", "Continue with Microsoft")}</button>
        <p id="microsoft-login-hint" className="microsoft-login-hint">{microsoft?.enabled ? t("Dùng tài khoản trường học hoặc công ty của bạn.", "Use your school or work account.") : microsoft ? t("Microsoft chưa được quản trị viên cấu hình.", "Microsoft sign-in has not been configured by your administrator.") : t("Đang kiểm tra đăng nhập Microsoft…", "Checking Microsoft sign-in…")}</p>
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
