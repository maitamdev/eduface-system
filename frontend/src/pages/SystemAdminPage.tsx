import React, { useCallback, useState } from "react";
import { authApi, personsApi } from "@/api/client";
import { useLanguage } from "@/context/LanguageContext";
import { useToast } from "@/context/ToastContext";
import { useResource } from "@/hooks/useResource";
import { dateTime, errorMessage } from "@/lib/format";
import { PageHeader, Section, RefreshButton, ErrorNotice, Field, EmptyState, Table } from "@/components/ProductUI";

export const SystemAdminPage: React.FC = () => {
  const { t, lang } = useLanguage();
  const toast = useToast();
  const usersLoader = useCallback(() => authApi.listUsers(), []);
  const configLoader = useCallback(() => personsApi.getDebugConfig(), []);
  const encodingsLoader = useCallback(() => personsApi.getDebugEncodings(), []);
  const users = useResource(usersLoader, []);
  const config = useResource(configLoader, null);
  const encodings = useResource(encodingsLoader, null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"operator" | "admin">("operator");
  const [creating, setCreating] = useState(false);
  const create = async (event: React.FormEvent) => {
    event.preventDefault();
    if (creating) return;
    if (username.trim().length < 3 || password.length < 6) { toast.warning(t("Tên đăng nhập tối thiểu 3 ký tự; mật khẩu tối thiểu 6 ký tự.", "Username needs 3 characters; password needs 6.")); return; }
    setCreating(true);
    try {
      const result = await authApi.registerUser({ username: username.trim(), password, role });
      users.setData((previous) => [result, ...previous]); setUsername(""); setPassword(""); setRole("operator");
      toast.success(t("Đã tạo tài khoản.", "Account created."));
    } catch (err) { toast.error(errorMessage(err)); } finally { setCreating(false); }
  };
  const reload = () => { void users.reload(); void config.reload(); void encodings.reload(); };
  return <div className="product-page">
    <PageHeader title={t("Tài khoản & hệ thống", "Users & system")} description={t("Cấp tài khoản và kiểm tra cấu hình nhận diện.", "Manage accounts and inspect recognition configuration.")}><RefreshButton onClick={reload} loading={users.loading || config.loading || encodings.loading} /></PageHeader>
    <div className="management-grid"><Section title={t("Tạo tài khoản", "Create account")} description={t("Operator sử dụng máy quét; Admin quản lý hồ sơ và báo cáo.", "Operators handle check-ins; admins manage profiles and reports.")}><form onSubmit={create} className="stack-form">
      <Field id="user-username" label={t("Tên đăng nhập *", "Username *")}><input id="user-username" autoComplete="off" value={username} minLength={3} maxLength={50} onChange={(event) => setUsername(event.target.value)} required /></Field>
      <Field id="user-password" label={t("Mật khẩu *", "Password *")} hint={t("Tối thiểu 6 ký tự theo chính sách hiện tại.", "At least 6 characters under the current policy.")}><input id="user-password" type="password" autoComplete="new-password" value={password} minLength={6} onChange={(event) => setPassword(event.target.value)} required /></Field>
      <Field id="user-role" label={t("Vai trò", "Role")}><select id="user-role" value={role} onChange={(event) => setRole(event.target.value as "admin" | "operator")}><option value="operator">{t("Operator · Vận hành", "Operator")}</option><option value="admin">{t("Admin · Quản trị viên", "Administrator")}</option></select></Field>
      <button className="primary-button" type="submit" disabled={creating}>{creating ? t("Đang tạo…", "Creating…") : t("Tạo tài khoản", "Create account")}</button>
    </form></Section><Section title={t("Tài khoản hệ thống", "System accounts")}><ErrorNotice message={users.error} retry={users.reload} /><Table label={t("Danh sách tài khoản", "Accounts")}><thead><tr><th>{t("Tài khoản", "Username")}</th><th>{t("Vai trò", "Role")}</th><th>{t("Ngày tạo", "Created")}</th><th>{t("Trạng thái", "Status")}</th></tr></thead><tbody>{users.data.map((user) => <tr key={user.id}><td className="cell-strong">{user.username}</td><td>{user.role}</td><td>{dateTime(user.created_at, lang)}</td><td className={user.is_active ? "attendance-status" : "muted"}>{user.is_active ? t("Hoạt động", "Active") : t("Đã khóa", "Disabled")}</td></tr>)}</tbody></Table>{!users.data.length && <EmptyState loading={users.loading}>{users.error ? t("Chưa tải được tài khoản.", "Accounts unavailable.") : t("Chưa có tài khoản.", "No accounts.")}</EmptyState>}</Section></div>
    <Section title={t("Chẩn đoán cấu hình", "Configuration diagnostics")}><ErrorNotice message={config.error} retry={config.reload} />{config.data ? <><dl className="config-grid"><div><dt>MongoDB</dt><dd>{config.data.MONGODB_URL}</dd></div><div><dt>{t("Cơ sở dữ liệu", "Database")}</dt><dd>{config.data.MONGODB_DB_NAME}</dd></div><div><dt>{t("Ngưỡng nhận diện", "Recognition threshold")}</dt><dd>{config.data.MIN_CONFIDENCE}</dd></div><div><dt>{t("Ngưỡng phát hiện trùng", "Duplicate threshold")}</dt><dd>{config.data.DUPLICATE_THRESHOLD}</dd></div></dl>{config.data.issues.length > 0 && <ul className="diagnostic-issues">{config.data.issues.map((issue) => <li key={issue}>{issue}</li>)}</ul>}</> : <EmptyState loading={config.loading}>{t("Chưa có thông tin cấu hình.", "Configuration unavailable.")}</EmptyState>}</Section>
    <Section title={t("Dữ liệu nhận diện khuôn mặt", "Face recognition data")}><ErrorNotice message={encodings.error} retry={encodings.reload} />{encodings.data ? <><p className="section-note">{t(`${encodings.data.persons_with_encodings} hồ sơ có vector · ${encodings.data.persons_missing_encodings} hồ sơ thiếu vector`, `${encodings.data.persons_with_encodings} profiles with vectors · ${encodings.data.persons_missing_encodings} missing vectors`)}</p>{encodings.data.missing.length ? <Table label={t("Hồ sơ cần kiểm tra", "Profiles to inspect")}><thead><tr><th>{t("Họ và tên", "Name")}</th><th>{t("Ngày đăng ký", "Enrolled")}</th><th>{t("Cần xử lý", "Action needed")}</th></tr></thead><tbody>{encodings.data.missing.map((person) => <tr key={person.person_id}><td className="cell-strong">{person.name}</td><td>{dateTime(person.enrolled_at, lang)}</td><td>{t("Kiểm tra và đăng ký lại khuôn mặt", "Review and re-enroll facial data")}</td></tr>)}</tbody></Table> : <p className="attendance-status">{t("Không có hồ sơ thiếu vector nhận diện.", "No profiles missing face vectors.")}</p>}</> : <EmptyState loading={encodings.loading}>{t("Chưa tải được trạng thái dữ liệu.", "Data status unavailable.")}</EmptyState>}</Section>
  </div>;
};
