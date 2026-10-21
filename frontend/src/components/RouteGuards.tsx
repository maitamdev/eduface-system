import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";

export const RequireAuth: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading, role } = useAuth();
  const { t } = useLanguage();
  const location = useLocation();

  if (isLoading) {
    return (
      <div role="status" className="panel-empty min-h-screen">
        <Loader2 size={20} className="animate-spin" />
        <p>{t("Đang xác thực phiên đăng nhập…", "Verifying session…")}</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (role === "student" && location.pathname !== "/student") {
    return <Navigate to="/student" replace />;
  }

  return <>{children}</>;
};

export const RequireAdmin: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { role } = useAuth();
  if (role !== "admin") {
    return <Navigate to={role === "student" ? "/student" : "/"} replace />;
  }
  return <>{children}</>;
};
