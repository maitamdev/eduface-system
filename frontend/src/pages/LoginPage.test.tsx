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
  login: vi.fn(), loginMicrosoft: vi.fn(), config: vi.fn(), redirect: vi.fn(), loginRedirect: vi.fn(), challenge: vi.fn(),
  authenticated: false, role: "operator",
}));
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ login: mocks.login, loginMicrosoft: mocks.loginMicrosoft, isAuthenticated: mocks.authenticated, user: mocks.authenticated ? { role: mocks.role } : null }) }));
vi.mock("@/api/client", () => ({ healthApi: { check: () => Promise.resolve({ status: "ok" }) }, authApi: { microsoftConfig: mocks.config, microsoftChallenge: mocks.challenge } }));
vi.mock("@/auth/microsoft", async (original) => ({ ...await original<typeof import("@/auth/microsoft")>(), microsoftClient: () => Promise.resolve({ loginRedirect: mocks.loginRedirect }), handleMicrosoftRedirect: mocks.redirect }));

function mount() {
  return render(<MemoryRouter initialEntries={["/login"]}><LanguageProvider><ThemeProvider><Routes><Route path="/login" element={<LoginPage />} /><Route path="/student" element={<h1>Student portal destination</h1>} /><Route path="/" element={<h1>Dashboard destination</h1>} /></Routes></ThemeProvider></LanguageProvider></MemoryRouter>);
}
beforeEach(() => {
  vi.clearAllMocks(); sessionStorage.clear(); localStorage.clear();
  mocks.authenticated = false; mocks.role = "operator";
  mocks.config.mockResolvedValue({ enabled: false, client_id: "", tenant_id: "" });
  mocks.redirect.mockResolvedValue(null);
  mocks.login.mockResolvedValue({ role: "operator" });
  mocks.loginRedirect.mockResolvedValue(undefined);
});
afterEach(cleanup);

describe("split login", () => {
  it("shows the campus image and disables Microsoft until configured", async () => {
    mount();
    expect(screen.getByRole("img", { name: /Sinh viên bước vào lớp học/ }).getAttribute("src")).toBe("/images/eduface-campus.png");
    await waitFor(() => expect(screen.getByRole("button", { name: "Tiếp tục với Microsoft" }).hasAttribute("disabled")).toBe(true));
    expect(await screen.findByText("Microsoft chưa được quản trị viên cấu hình.")).toBeTruthy();
  });
  it("keeps password login usable when Microsoft is disabled", async () => {
    mount(); const user = userEvent.setup();
    await user.type(screen.getByLabelText("Tên đăng nhập"), "operator");
    await user.type(screen.getByLabelText("Mật khẩu", { exact: true }), "secret123");
    await user.click(screen.getByRole("button", { name: /^Đăng nhập$/ }));
    await waitFor(() => expect(mocks.login).toHaveBeenCalledWith("operator", "secret123"));
  });
  it("uses a server challenge before Microsoft redirect", async () => {
    mocks.config.mockResolvedValue({ enabled: true, client_id: "client", tenant_id: "tenant" });
    mocks.challenge.mockResolvedValue({ challenge_id: "challenge-123", nonce: "server-nonce" });
    mount();
    const button = screen.getByRole("button", { name: "Tiếp tục với Microsoft" });
    await waitFor(() => expect(button.hasAttribute("disabled")).toBe(false));
    await userEvent.setup().click(button);
    await waitFor(() => expect(mocks.loginRedirect).toHaveBeenCalledWith(expect.objectContaining({ nonce: "server-nonce", state: "challenge-123", scopes: ["openid", "profile"] })));
  });
  it("rejects a callback whose state does not match the browser request", async () => {
    mocks.config.mockResolvedValue({ enabled: true, client_id: "client", tenant_id: "tenant" });
    mocks.redirect.mockResolvedValue({ state: "wrong-challenge", idToken: "signed-token" });
    sessionStorage.setItem("eduface_microsoft_pending", JSON.stringify({ challengeId: "expected-challenge", returnPath: "/" }));
    mount();
    expect(await screen.findByRole("alert")).toBeTruthy();
    expect(mocks.loginMicrosoft).not.toHaveBeenCalled();
  });
  it("routes students to their portal", async () => {
    mocks.authenticated = true; mocks.role = "student";
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
