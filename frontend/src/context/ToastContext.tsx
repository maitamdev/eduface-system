import React, { createContext, useCallback, useContext, useMemo, useState } from "react";
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from "lucide-react";

type ToastType = "success" | "error" | "warning" | "info";

interface ToastItem {
  id: string;
  type: ToastType;
  message: string;
}

interface ToastContextValue {
  toast: {
    success: (message: string) => void;
    error: (message: string) => void;
    warning: (message: string) => void;
    info: (message: string) => void;
  };
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [items, setItems] = useState<ToastItem[]>([]);

  const push = useCallback((type: ToastType, message: string) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    setItems((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setItems((prev) => prev.filter((item) => item.id !== id));
    }, 4200);
  }, []);

  const remove = (id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  const toast = useMemo(() => ({
    success: (m: string) => push("success", m),
    error: (m: string) => push("error", m),
    warning: (m: string) => push("warning", m),
    info: (m: string) => push("info", m),
  }), [push]);

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none px-4 sm:px-0">
        {items.map((item) => {
          const styles: Record<ToastType, string> = {
            success:
              "bg-[var(--ui-surface)] border-[var(--ui-border)] border-l-2 border-l-[var(--ui-green)] text-[var(--ui-text)]",
            error:
              "bg-[var(--ui-surface)] border-[var(--ui-border)] border-l-2 border-l-[#b64743] text-[var(--ui-text)]",
            warning:
              "bg-[var(--ui-surface)] border-[var(--ui-border)] border-l-2 border-l-[#bd934c] text-[var(--ui-text)]",
            info:
              "bg-[var(--ui-surface)] border-[var(--ui-border)] border-l-2 border-l-[var(--ui-accent)] text-[var(--ui-text)]",
          };
          const icons: Record<ToastType, React.ReactNode> = {
            success: <CheckCircle2 className="w-4 h-4 text-[var(--ui-green)] shrink-0 mt-0.5" />,
            error: <XCircle className="w-4 h-4 text-[#b64743] dark:text-[#efa8a2] shrink-0 mt-0.5" />,
            warning: <AlertTriangle className="w-4 h-4 text-[#8b662e] dark:text-[#dfbd80] shrink-0 mt-0.5" />,
            info: <Info className="w-4 h-4 text-[var(--ui-muted)] shrink-0 mt-0.5" />,
          };
          return (
            <div
              key={item.id}
              role="status"
              className={`pointer-events-auto flex items-start gap-2.5 px-3.5 py-2.5 rounded border shadow-sm transition-all ${styles[item.type]}`}
            >
              {icons[item.type]}
              <p className="text-xs flex-1 leading-relaxed">{item.message}</p>
              <button
                type="button"
                onClick={() => remove(item.id)}
                aria-label="Close notification"
                className="icon-button !min-w-6 !min-h-6 !p-1"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used inside ToastProvider");
  return ctx.toast;
}
