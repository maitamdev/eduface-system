import { useState, type FormEvent } from "react";
import { authApi } from "@/api/client";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useToast } from "@/context/ToastContext";
import { Dialog, ErrorNotice, Field } from "@/components/ProductUI";
import { errorMessage } from "@/lib/format";

export function AccountSecurity({ onClose }: { onClose: () => void }) {
  const { t } = useLanguage(); const { refreshProfile } = useAuth(); const toast = useToast();
  const [current, setCurrent] = useState(""); const [next, setNext] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false); const [error, setError] = useState<string | null>(null);
  async function submit(e: FormEvent) {
    e.preventDefault(); if (busy) return;
    if (next !== confirmation) { setError(t("Hai mật khẩu mới chưa khớp.", "New passwords do not match.")); return; }
    setBusy(true); setError(null);
    try { await authApi.changePassword(current, next); await refreshProfile(); toast.success(t("Đã đổi mật khẩu và thu hồi các phiên cũ.", "Password changed. Previous sessions revoked.")); onClose(); }
    catch (err) { setError(errorMessage(err)); } finally { setBusy(false); }
  }
  return <Dialog title={t("Đổi mật khẩu", "Change password")} onClose={onClose} busy={busy}>
    <form className="stack-form" onSubmit={submit}>
      <p className="muted">{t("Dùng ít nhất 12 ký tự. Các phiên đăng nhập cũ sẽ hết hiệu lực.", "Use at least 12 characters. Previous sessions will be revoked.")}</p>
      <ErrorNotice message={error} />
      <Field id="current-password" label={t("Mật khẩu hiện tại", "Current password")}><input id="current-password" autoComplete="current-password" type="password" value={current} onChange={(e) => setCurrent(e.target.value)} required maxLength={128} /></Field>
      <Field id="new-password" label={t("Mật khẩu mới", "New password")}><input id="new-password" autoComplete="new-password" type="password" value={next} onChange={(e) => setNext(e.target.value)} required minLength={12} maxLength={128} /></Field>
      <Field id="confirm-password" label={t("Nhập lại mật khẩu mới", "Confirm new password")}><input id="confirm-password" autoComplete="new-password" type="password" value={confirmation} onChange={(e) => setConfirmation(e.target.value)} required minLength={12} maxLength={128} /></Field>
      <button className="primary-button" disabled={busy} type="submit">{busy ? t("Đang lưu…", "Saving…") : t("Đổi mật khẩu", "Change password")}</button>
    </form>
  </Dialog>;
}
