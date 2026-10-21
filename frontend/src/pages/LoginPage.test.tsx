// @vitest-environment jsdom
import React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { LanguageProvider } from "@/context/LanguageContext";
import { ThemeProvider } from "@/context/ThemeContext";
import { LoginPage } from "./LoginPage";

const mocks = vi.hoisted(() => ({
  login: vi.fn(),
  loginGoogle: vi.fn(),
  googleConfig: vi.fn(),
  requestToken: vi.fn(),
  authenticated: false,
  role: "operator",
}));

vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({
    login: mocks.login,
    loginGoogle: mocks.loginGoogle,
    isAuthenticated: mocks.authenticated,
    user: mocks.authenticated ? { role: mocks.role } : null,
  }),
}));

vi.mock("@/api/client", () => ({
  healthApi: { check: () => Promise.resolve({ status: "ok" }) },
  authApi: { googleConfig: mocks.googleConfig },
}));

vi.mock("@/auth/google", () => ({
  requestGoogleAccessToken: mocks.requestToken,
}));

function mount() {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <LanguageProvider>
        <ThemeProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/student" element={<h1>Student portal destination</h1>} />
            <Route path="/" element={<h1>Dashboard destination</h1>} />
          </Routes>
        </ThemeProvider>
      </LanguageProvider>
    </MemoryRouter>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  sessionStorage.clear();
  localStorage.clear();
  mocks.authenticated = false;
  mocks.role = "operator";
  mocks.googleConfig.mockResolvedValue({ enabled: false, client_id: "" });
  mocks.login.mockResolvedValue({ role: "operator" });
  mocks.loginGoogle.mockResolvedValue({ role: "admin" });
  mocks.requestToken.mockResolvedValue("google-access-token-123");
});

afterEach(cleanup);

describe("split login with Google Sign-In", () => {
  it("shows the campus image and disables Google until configured", async () => {
    mount();
    expect(screen.getByRole("img", { name: /Sinh viên bước vào lớp học/ }).getAttribute("src")).toBe("/images/eduface-campus.png");
    await waitFor(() => expect(screen.getByRole("button", { name: "Tiếp tục với Google" }).hasAttribute("disabled")).toBe(true));
    expect(await screen.findByText(/Google chưa được cấu hình/)).toBeTruthy();
  });

  it("keeps password login usable when Google is disabled", async () => {
    mount();
    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Tên đăng nhập"), "operator");
    await user.type(screen.getByLabelText("Mật khẩu", { exact: true }), "secret123");
    await user.click(screen.getByRole("button", { name: /^Đăng nhập$/ }));
    await waitFor(() => expect(mocks.login).toHaveBeenCalledWith("operator", "secret123"));
  });

  it("requests Google access token and exchanges it when Google is enabled", async () => {
    mocks.googleConfig.mockResolvedValue({ enabled: true, client_id: "123456-test.apps.googleusercontent.com" });
    mount();
    const button = screen.getByRole("button", { name: "Tiếp tục với Google" });
    await waitFor(() => expect(button.hasAttribute("disabled")).toBe(false));
    await userEvent.setup().click(button);
    await waitFor(() => expect(mocks.requestToken).toHaveBeenCalledWith("123456-test.apps.googleusercontent.com"));
    await waitFor(() => expect(mocks.loginGoogle).toHaveBeenCalledWith("google-access-token-123"));
  });

  it("routes students to their portal", async () => {
    mocks.authenticated = true;
    mocks.role = "student";
    mount();
    expect(await screen.findByRole("heading", { name: "Student portal destination" })).toBeTruthy();
  });

  it("retains a usable login form if the illustration fails to load", () => {
    mount();
    fireEvent.error(screen.getByRole("img", { name: /Sinh viên bước vào lớp học/ }));
    expect(screen.queryByRole("img", { name: /Sinh viên bước vào lớp học/ })).toBeNull();
    expect(screen.getByRole("button", { name: /^Đăng nhập$/ })).toBeTruthy();
  });
});
