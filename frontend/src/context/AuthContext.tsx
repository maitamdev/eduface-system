import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { authApi, getStoredToken, setStoredToken, type UserOut } from "@/api/client";

interface AuthContextValue {
  user: UserOut | null;
  token: string | null;
  role: "admin" | "operator" | "student" | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<UserOut>;
  loginGoogle: (accessToken: string) => Promise<UserOut>;
  loginMicrosoft: (challengeId: string, idToken: string) => Promise<UserOut>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserOut | null>(null);
  const [token, setToken] = useState<string | null>(getStoredToken());
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const logout = useCallback(() => {
    setStoredToken(null);
    setToken(null);
    setUser(null);
  }, []);

  const refreshProfile = useCallback(async () => {
    const existing = getStoredToken();
    if (!existing) {
      setIsLoading(false);
      return;
    }
    try {
      const profile = await authApi.me();
      setUser(profile);
      setToken(existing);
    } catch {
      logout();
    } finally {
      setIsLoading(false);
    }
  }, [logout]);

  useEffect(() => {
    refreshProfile();
  }, [refreshProfile]);

  useEffect(() => {
    window.addEventListener("aura:unauthorized", logout);
    return () => window.removeEventListener("aura:unauthorized", logout);
  }, [logout]);

  const login = async (username: string, password: string): Promise<UserOut> => {
    try {
      const res = await authApi.login(username, password);
      const profile = await authApi.me();
      setToken(res.access_token); setUser(profile); return profile;
    } catch (error) { logout(); throw error; }
  };

  const loginGoogle = async (accessToken: string): Promise<UserOut> => {
    try {
      const response = await authApi.googleExchange(accessToken);
      const profile = await authApi.me();
      setToken(response.access_token); setUser(profile); return profile;
    } catch (error) { logout(); throw error; }
  };

  const loginMicrosoft = async (challengeId: string, idToken: string): Promise<UserOut> => {
    try {
      const response = await authApi.microsoftExchange(challengeId, idToken);
      const profile = await authApi.me();
      setToken(response.access_token); setUser(profile); return profile;
    } catch (error) { logout(); throw error; }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role: user?.role ?? null,
        isAuthenticated: Boolean(user),
        isLoading,
        login,
        loginGoogle,
        loginMicrosoft,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
