import React, { useCallback, useState } from "react";
import { authApi, personsApi, type UserOut } from "@/api/client";
import { useLanguage } from "@/context/LanguageContext";
import { useToast } from "@/context/ToastContext";
import { useResource } from "@/hooks/useResource";
import { dateTime, errorMessage } from "@/lib/format";
import { PageHeader, Section, RefreshButton, ErrorNotice, Field, EmptyState, Table, Dialog } from "@/components/ProductUI";

export const SystemAdminPage: React.FC = () => {
  const { t, lang } = useLanguage();
  const toast = useToast();
  const usersLoader = useCallback(() => authApi.listUsers(), []);
  const personsLoader = useCallback(() => personsApi.list(), []);
  const configLoader = useCallback(() => personsApi.getDebugConfig(), []);
  const encodingsLoader = useCallback(() => personsApi.getDebugEncodings(), []);
  const users = useResource(usersLoader, []);
  const persons = useResource(personsLoader, []);
  const config = useResource(configLoader, null);
  const encodings = useResource(encodingsLoader, null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"operator" | "admin" | "student">("operator");
  const [personId, setPersonId] = useState("");
  const [creating, setCreating] = useState(false);
  const [googleTarget, setGoogleTarget] = useState<UserOut | null>(null);
  const [googleEmail, setGoogleEmail] = useState("");
  const [linking, setLinking] = useState(false);
  const [linkError, setLinkError] = useState<string | null>(null);
  const [editUserTarget, setEditUserTarget] = useState<UserOut | null>(null);
  const [editUserRole, setEditUserRole] = useState<"operator" | "admin" | "student">("operator");
  const [editUserActive, setEditUserActive] = useState(true);
  const [editUserPersonId, setEditUserPersonId] = useState("");
  const [editUserPassword, setEditUserPassword] = useState("");
  const [savingUser, setSavingUser] = useState(false);

  const openEditUser = (u: UserOut) => {
    setEditUserTarget(u);
    setEditUserRole(u.role);
    setEditUserActive(u.is_active);
    setEditUserPersonId(u.person_id || "");
    setEditUserPassword("");
  };

  const saveEditUser = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!editUserTarget || savingUser) return;
    if (editUserPassword.trim() && editUserPassword.trim().length < 12) {
      toast.warning(t("Mật khẩu mới phải có tối thiểu 12 ký tự.", "New password must be at least 12 characters."));
      return;
    }
    setSavingUser(true);
    try {
      const updated = await authApi.updateUser(editUserTarget.id, {
        role: editUserRole,
        is_active: editUserActive,
        person_id: editUserPersonId,
        ...(editUserPassword.trim() ? { password: editUserPassword.trim() } : {}),
      });
      users.setData((prev) => prev.map((item) => item.id === updated.id ? updated : item));
      setEditUserTarget(null);
      toast.success(t("Đã cập nhật phân quyền & tài khoản.", "Account updated."));
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setSavingUser(false);
    }
  };

  const linkGoogle = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!googleTarget || linking) return;
    setLinking(true); setLinkError(null);
    try {
      const result = await authApi.linkGoogle(googleTarget.id, googleEmail.trim() || null);
      users.setData((previous) => previous.map((user) => user.id === googleTarget.id ? { ...user, google_email: result.google_email } : user));
      setGoogleTarget(null);
      toast.success(t("Đã cập nhật liên kết Google.", "Google account link updated."));
    } catch (err) { setLinkError(errorMessage(err)); } finally { setLinking(false); }
  };

  const create = async (event: React.FormEvent) => {
    event.preventDefault();
    if (creating) return;
    if (username.trim().length < 3 || password.length < 12) { toast.warning(t("Tên đăng nhập tối thiểu 3 ký tự; mật khẩu tối thiểu 12 ký tự.", "Username needs 3 characters; password needs 6.")); return; }
    setCreating(true);
    try {
      const result = await authApi.registerUser({ username: username.trim(), password, role, person_id: role === "student" && personId ? personId : undefined });
      users.setData((previous) => [result, ...previous]); setUsername(""); setPassword(""); setRole("operator"); setPersonId("");
      toast.success(t("Đã tạo tài khoản.", "Account created."));
    } catch (err) { toast.error(errorMessage(err)); } finally { setCreating(false); }
  };
  const reload = () => { void users.reload(); void persons.reload(); void config.reload(); void encodings.reload(); };
  return <div className="product-page">
    <PageHeader title={t("Tài khoản & hệ thống", "Users & system")} description={t("Cấp tài khoản và kiểm tra cấu hình nhận diện.", "Manage accounts and inspect recognition configuration.")}><RefreshButton onClick={reload} loading={users.loading || config.loading || encodings.loading} /></PageHeader>
    <div className="management-grid"><Section title={t("Tạo tài khoản", "Create account")} description={t("Operator vận hành điểm danh; Admin quản trị hệ thống; Student xem lịch sử điểm danh cá nhân.", "Operators handle check-ins; admins manage profiles; students view their personal attendance history.")}><form onSubmit={create} className="stack-form">
      <Field id="user-username" label={t("Tên đăng nhập *", "Username *")}><input id="user-username" autoComplete="off" value={username} minLength={3} maxLength={50} onChange={(event) => setUsername(event.target.value)} required /></Field>
      <Field id="user-password" label={t("Mật khẩu *", "Password *")} hint={t("Tối thiểu 12 ký tự theo chính sách hiện tại.", "At least 12 characters under the current policy.")}><input id="user-password" type="password" autoComplete="new-password" value={password} minLength={12} onChange={(event) => setPassword(event.target.value)} required /></Field>
      <Field id="user-role" label={t("Vai trò", "Role")}><select id="user-role" value={role} onChange={(event) => setRole(event.target.value as "admin" | "operator" | "student")}><option value="operator">{t("Operator · Giảng viên / Vận hành", "Operator · Instructor")}</option><option value="admin">{t("Admin · Quản trị viên", "Administrator")}</option><option value="student">{t("Student · Sinh viên", "Student")}</option></select></Field>
      {role === "student" && <Field id="user-person" label={t("Liên kết hồ sơ khuôn mặt sinh viên", "Link to enrolled student profile")}><select id="user-person" value={personId} onChange={(event) => setPersonId(event.target.value)}><option value="">{t("— Chọn hồ sơ sinh viên —", "— Select student profile —")}</option>{persons.data.map((person) => <option key={person.id} value={person.id}>{person.name} {person.department ? `(${person.department})` : ""}</option>)}</select></Field>}
      <button className="primary-button" type="submit" disabled={creating}>{creating ? t("Đang tạo…", "Creating…") : t("Tạo tài khoản", "Create account")}</button>
    </form></Section><Section title={t("Tài khoản hệ thống & Phân quyền", "System accounts & RBAC")}><ErrorNotice message={users.error} retry={users.reload} /><Table label={t("Danh sách tài khoản", "Accounts")}><thead><tr><th>{t("Tài khoản", "Username")}</th><th>{t("Vai trò", "Role")}</th><th>{t("Hồ sơ liên kết", "Linked profile")}</th><th>{t("Trạng thái", "Status")}</th><th className="align-right">{t("Thao tác", "Actions")}</th></tr></thead><tbody>{users.data.map((user) => {
      const linkedPerson = persons.data.find((p) => p.id === user.person_id);
      return <tr key={user.id}><td className="cell-strong">{user.username}</td><td>{user.role === "admin" ? "Admin" : user.role === "operator" ? t("Giảng viên (Operator)", "Operator") : t("Sinh viên (Student)", "Student")}</td><td>{linkedPerson ? `${linkedPerson.name}${linkedPerson.department ? ` (${linkedPerson.department})` : ""}` : "–"}</td><td className={user.is_active ? "attendance-status" : "warning-text"}>{user.is_active ? t("Hoạt động", "Active") : t("Đã khóa", "Disabled")}</td><td className="align-right"><button className="text-button" onClick={() => openEditUser(user)}>{t("Phân quyền / Sửa", "Manage")}</button></td></tr>;
    })}</tbody></Table>{!users.data.length && <EmptyState loading={users.loading}>{users.error ? t("Chưa tải được tài khoản.", "Accounts unavailable.") : t("Chưa có tài khoản.", "No accounts.")}</EmptyState>}</Section></div>
    <Section title={t("Chẩn đoán cấu hình", "Configuration diagnostics")}><ErrorNotice message={config.error} retry={config.reload} />{config.data ? <><dl className="config-grid"><div><dt>MongoDB</dt><dd>{config.data.MONGODB_URL}</dd></div><div><dt>{t("Cơ sở dữ liệu", "Database")}</dt><dd>{config.data.MONGODB_DB_NAME}</dd></div><div><dt>{t("Ngưỡng nhận diện", "Recognition threshold")}</dt><dd>{config.data.MIN_CONFIDENCE}</dd></div><div><dt>{t("Ngưỡng phát hiện trùng", "Duplicate threshold")}</dt><dd>{config.data.DUPLICATE_THRESHOLD}</dd></div></dl>{config.data.issues.length > 0 && <ul className="diagnostic-issues">{config.data.issues.map((issue) => <li key={issue}>{issue}</li>)}</ul>}</> : <EmptyState loading={config.loading}>{t("Chưa có thông tin cấu hình.", "Configuration unavailable.")}</EmptyState>}</Section>
    <Section title={t("Dữ liệu nhận diện khuôn mặt", "Face recognition data")}><ErrorNotice message={encodings.error} retry={encodings.reload} />{encodings.data ? <><p className="section-note">{t(`${encodings.data.persons_with_encodings} hồ sơ có vector · ${encodings.data.persons_missing_encodings} hồ sơ thiếu vector`, `${encodings.data.persons_with_encodings} profiles with vectors · ${encodings.data.persons_missing_encodings} missing vectors`)}</p>{encodings.data.missing.length ? <Table label={t("Hồ sơ cần kiểm tra", "Profiles to inspect")}><thead><tr><th>{t("Họ và tên", "Name")}</th><th>{t("Ngày đăng ký", "Enrolled")}</th><th>{t("Cần xử lý", "Action needed")}</th></tr></thead><tbody>{encodings.data.missing.map((person) => <tr key={person.person_id}><td className="cell-strong">{person.name}</td><td>{dateTime(person.enrolled_at, lang)}</td><td>{t("Kiểm tra và đăng ký lại khuôn mặt", "Review and re-enroll facial data")}</td></tr>)}</tbody></Table> : <p className="attendance-status">{t("Không có hồ sơ thiếu vector nhận diện.", "No profiles missing face vectors.")}</p>}</> : <EmptyState loading={encodings.loading}>{t("Chưa tải được trạng thái dữ liệu.", "Data status unavailable.")}</EmptyState>}</Section>
    <Section title={t("Đăng nhập Google", "Google sign-in")} description={t("Liên kết tài khoản EduFace với địa chỉ email Google (@gmail.com hoặc @dhv.edu.vn). Vai trò và hồ sơ sinh viên được giữ nguyên.", "Link EduFace accounts to their Google email addresses (@gmail.com or @dhv.edu.vn). Roles and student profiles stay the same.")}>
      <Table label={t("Liên kết tài khoản Google", "Google account links")}><thead><tr><th>{t("Tài khoản EduFace", "EduFace account")}</th><th>{t("Vai trò", "Role")}</th><th>Google Email</th><th>{t("Thao tác", "Actions")}</th></tr></thead><tbody>{users.data.map((user) => <tr key={user.id}><td className="cell-strong">{user.username}</td><td>{user.role}</td><td>{user.google_email || t("Chưa liên kết", "Not linked")}</td><td><button className="text-button" onClick={() => { setGoogleTarget(user); setGoogleEmail(user.google_email || ""); setLinkError(null); }}>{user.google_email ? t("Đổi email", "Edit email") : t("Liên kết email", "Link email")}</button></td></tr>)}</tbody></Table>
    </Section>
    {googleTarget && <Dialog title={t(`Liên kết Google · ${googleTarget.username}`, `Google Link · ${googleTarget.username}`)} busy={linking} onClose={() => setGoogleTarget(null)}><form className="stack-form" onSubmit={linkGoogle}><p className="muted">{t("Nhập địa chỉ email Google (@gmail.com hoặc @dhv.edu.vn) để cho phép người dùng này đăng nhập nhanh bằng nút Google. Để trống để gỡ liên kết.", "Enter a Google email address (@gmail.com or @dhv.edu.vn) to allow this user to sign in with Google. Leave blank to unlink.")}</p><Field id="google-email-input" label="Google Email"><input id="google-email-input" type="email" value={googleEmail} onChange={(event) => setGoogleEmail(event.target.value)} placeholder="tenban@gmail.com / mssv@dhv.edu.vn" /></Field><ErrorNotice message={linkError} /><div className="dialog-actions"><button type="button" className="secondary-button" disabled={linking} onClick={() => setGoogleTarget(null)}>{t("Hủy", "Cancel")}</button><button type="submit" className="primary-button" disabled={linking}>{linking ? t("Đang lưu…", "Saving…") : t("Lưu liên kết", "Save link")}</button></div></form></Dialog>}
    {editUserTarget && (
      <Dialog title={t(`Phân quyền & Tài khoản · ${editUserTarget.username}`, `Manage Account · ${editUserTarget.username}`)} busy={savingUser} onClose={() => setEditUserTarget(null)}>
        <form className="stack-form" onSubmit={saveEditUser}>
          <Field id="edit-user-role" label={t("Vai trò hệ thống (Role)", "System role")}>
            <select id="edit-user-role" value={editUserRole} onChange={(e) => setEditUserRole(e.target.value as "operator" | "admin" | "student")}>
              <option value="student">{t("Student · Sinh viên", "Student")}</option>
              <option value="operator">{t("Operator · Giảng viên / Vận hành", "Operator · Instructor")}</option>
              <option value="admin">{t("Admin · Quản trị viên", "Administrator")}</option>
            </select>
          </Field>
          <Field id="edit-user-active" label={t("Trạng thái hoạt động", "Account status")}>
            <select id="edit-user-active" value={editUserActive ? "active" : "disabled"} onChange={(e) => setEditUserActive(e.target.value === "active")}>
              <option value="active">{t("Đang hoạt động (Cho phép đăng nhập)", "Active (Allowed to sign in)")}</option>
              <option value="disabled">{t("Khóa tài khoản (Chặn đăng nhập)", "Disabled (Blocked)")}</option>
            </select>
          </Field>
          <Field id="edit-user-person" label={t("Liên kết hồ sơ khuôn mặt sinh viên", "Linked student face profile")}>
            <select id="edit-user-person" value={editUserPersonId} onChange={(e) => setEditUserPersonId(e.target.value)}>
              <option value="">{t("— Không liên kết —", "— Not linked —")}</option>
              {persons.data.map((p) => <option key={p.id} value={p.id}>{p.name} {p.student_id ? `· ${p.student_id}` : ""} {p.department ? `(${p.department})` : ""}</option>)}
            </select>
          </Field>
          <Field id="edit-user-password" label={t("Đặt lại mật khẩu mới (Để trống nếu giữ nguyên)", "Reset password (leave blank to keep current)")}>
            <input id="edit-user-password" type="password" autoComplete="new-password" value={editUserPassword} onChange={(e) => setEditUserPassword(e.target.value)} placeholder={t("Nhập tối thiểu 12 ký tự để đổi mật khẩu…", "At least 12 characters…")} />
          </Field>
          <div className="dialog-actions">
            <button type="button" className="secondary-button" disabled={savingUser} onClick={() => setEditUserTarget(null)}>{t("Hủy", "Cancel")}</button>
            <button type="submit" className="primary-button" disabled={savingUser}>{savingUser ? t("Đang lưu…", "Saving…") : t("Lưu thay đổi", "Save changes")}</button>
          </div>
        </form>
      </Dialog>
    )}
  </div>;
};
