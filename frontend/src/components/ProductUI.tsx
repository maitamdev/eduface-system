import React, { useEffect, useRef } from "react";
import { RefreshCw, AlertCircle, Search, X, ChevronLeft, ChevronRight } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export function PageHeader({ title, description, children }: { title: string; description?: string; children?: React.ReactNode }) {
  return <header className="product-page-header"><div><h1>{title}</h1>{description && <p>{description}</p>}</div>{children && <div className="page-actions">{children}</div>}</header>;
}
export function Section({ title, description, action, children, className = "" }: { title?: string; description?: string; action?: React.ReactNode; children: React.ReactNode; className?: string }) {
  return <section className={`product-section ${className}`}>{title && <div className="section-heading"><div><h2>{title}</h2>{description && <p>{description}</p>}</div>{action}</div>}{children}</section>;
}
export function RefreshButton({ onClick, loading }: { onClick: () => void; loading: boolean }) {
  const { t } = useLanguage();
  return <button type="button" className="secondary-button" onClick={onClick} disabled={loading}><RefreshCw size={14} className={loading ? "animate-spin" : ""} />{t("Làm mới", "Refresh")}</button>;
}
export function ErrorNotice({ message, retry }: { message: string | null; retry?: () => void }) {
  const { t } = useLanguage();
  return message ? <div role="alert" className="product-error"><AlertCircle size={16} /><span>{message}</span>{retry && <button onClick={retry}>{t("Thử lại", "Retry")}</button>}</div> : null;
}
export function Field({ id, label, hint, children }: { id: string; label: string; hint?: string; children: React.ReactNode }) {
  return <div className="form-field"><label htmlFor={id}>{label}</label>{children}{hint && <small>{hint}</small>}</div>;
}
export function SearchField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  const { t } = useLanguage();
  return <div className="record-search"><Search size={15} /><input type="search" aria-label={label} placeholder={label} value={value} onChange={(event) => onChange(event.target.value)} />{value && <button type="button" className="icon-button" onClick={() => onChange("")} aria-label={t("Xóa tìm kiếm", "Clear search")}><X size={14} /></button>}</div>;
}
export function EmptyState({ loading = false, children }: { loading?: boolean; children: React.ReactNode }) {
  const { t } = useLanguage();
  return <div role="status" className="panel-empty">{loading && <RefreshCw size={18} className="animate-spin" />}<p>{loading ? t("Đang tải…", "Loading…") : children}</p></div>;
}
export function Table({ children, label }: { children: React.ReactNode; label: string }) {
  return <div className="data-table-scroll" tabIndex={0} role="region" aria-label={label}><table className="data-table">{children}</table></div>;
}
export function Pager({ page, pages, count, onChange }: { page: number; pages: number; count: number; onChange: (page: number) => void }) {
  const { t } = useLanguage();
  return <div className="table-pagination"><span>{t(`${count} kết quả`, `${count} results`)}</span><div><button className="icon-button" disabled={page <= 1} aria-label={t("Trang trước", "Previous page")} onClick={() => onChange(page - 1)}><ChevronLeft size={17} /></button><span>{page} / {pages}</span><button className="icon-button" disabled={page >= pages} aria-label={t("Trang sau", "Next page")} onClick={() => onChange(page + 1)}><ChevronRight size={17} /></button></div></div>;
}
export function Dialog({ title, children, onClose, busy = false }: { title: string; children: React.ReactNode; onClose: () => void; busy?: boolean }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const close = useRef(onClose);
  close.current = onClose;
  const { t } = useLanguage();
  useEffect(() => {
    const element = dialog.current!;
    element.showModal();
    return () => element.close();
  }, []);
  return <dialog ref={dialog} className="product-dialog" aria-label={title} onCancel={(event) => { event.preventDefault(); if (!busy) close.current(); }}><div className="dialog-heading"><h2>{title}</h2><button className="icon-button" type="button" disabled={busy} onClick={onClose} aria-label={t("Đóng", "Close")}><X size={18} /></button></div>{children}</dialog>;
}
