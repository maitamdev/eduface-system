// @vitest-environment jsdom
import { afterEach, expect, it, vi } from "vitest";
import { ApiClientError, apiFetch, personsApi, setStoredToken } from "./client";

afterEach(() => {
  setStoredToken(null);
  vi.unstubAllGlobals();
});

it.each(["header", "body"])("shows a server error's request ID from the %s without retrying a write", async (source) => {
  const body = { detail: "Máy chủ gặp lỗi", ...(source === "body" ? { request_id: "enroll-abc123" } : {}) };
  const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(body), {
    status: 500,
    headers: source === "header" ? { "X-Request-ID": "enroll-abc123" } : {},
  }));
  vi.stubGlobal("fetch", fetchMock);
  await expect(apiFetch("/api/persons/self-enroll", { method: "POST" })).rejects.toMatchObject({
    name: "ApiClientError", status: 500,
    message: "Máy chủ gặp lỗi (Mã yêu cầu: enroll-abc123)", detail: body,
  });
  expect(fetchMock).toHaveBeenCalledTimes(1);
});

it("keeps normal validation errors readable", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: [{ msg: "Consent required" }] }), {
    status: 422, headers: { "X-Request-ID": "validation-123" },
  })));
  await expect(apiFetch("/api/persons/self-enroll")).rejects.toMatchObject({ status: 422, message: "Consent required" });
});

it("does not display malformed request IDs", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Unavailable", request_id: "x".repeat(1000) }), { status: 503 })));
  await expect(apiFetch("/api/persons/self-enroll")).rejects.toMatchObject({ message: "Unavailable" });
});

it("sends enrollment consent, photos and authentication without overriding the multipart boundary", async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ id: "test-person" }), { status: 201 }));
  vi.stubGlobal("fetch", fetchMock);
  setStoredToken("synthetic-test-token");
  await personsApi.selfEnroll({ consent: true, name: " Test Student ", student_id: " TEST01 ", department: " Test ", photos: [new Blob(["test"], { type: "image/jpeg" })] });
  const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
  expect(url).toMatch(/\/api\/persons\/self-enroll$/);
  expect(init.method).toBe("POST");
  expect(init.headers).toMatchObject({ Authorization: "Bearer synthetic-test-token" });
  expect(new Headers(init.headers).has("Content-Type")).toBe(false);
  const data = init.body as FormData;
  expect(data.get("consent")).toBe("true");
  expect(data.get("name")).toBe("Test Student");
  expect(data.getAll("photos")).toHaveLength(1);
});

it("preserves genuine network failures instead of presenting a fabricated HTTP response", async () => {
  const networkError = new TypeError("Failed to fetch");
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(networkError));
  await expect(apiFetch("/api/persons/self-enroll")).rejects.toBe(networkError);
  expect(networkError).not.toBeInstanceOf(ApiClientError);
});
