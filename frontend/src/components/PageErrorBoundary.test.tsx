// @vitest-environment jsdom
import React from "react";
import { afterEach, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { LanguageProvider } from "@/context/LanguageContext";
import { PageErrorBoundary } from "./PageErrorBoundary";

afterEach(() => { cleanup(); vi.restoreAllMocks(); localStorage.clear(); });

function BrokenPage(): React.ReactNode { throw new Error("Test rendering failure"); }

it("contains a page failure while preserving navigation and recovers after navigation", async () => {
  vi.spyOn(console, "error").mockImplementation(() => {});
  render(<MemoryRouter initialEntries={["/broken"]}><LanguageProvider>
    <nav>Navigation remains available</nav>
    <PageErrorBoundary><Routes>
      <Route path="/broken" element={<BrokenPage />} />
      <Route path="/" element={<h1>Overview restored</h1>} />
    </Routes></PageErrorBoundary>
  </LanguageProvider></MemoryRouter>);
  expect(screen.getByText("Navigation remains available")).toBeTruthy();
  expect(screen.getByRole("alert")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Tải lại trang" })).toBeTruthy();
  expect(screen.queryByText("Test rendering failure")).toBeNull();
  await userEvent.setup().click(screen.getByRole("link", { name: "Về tổng quan" }));
  expect(await screen.findByRole("heading", { name: "Overview restored" })).toBeTruthy();
  expect(screen.queryByRole("alert")).toBeNull();
});
