import { describe, expect, it } from "vitest";
import { safeReturnPath } from "./microsoft";
import { matchesSearch } from "@/lib/format";

describe("authentication return paths", () => {
  it.each(["https://untrusted.example", "//untrusted.example", "/\\untrusted.example", "/\nuntrusted.example", "/login", null, undefined])("rejects external or unsafe destination %s", (path) => {
    expect(safeReturnPath(path)).toBe("/");
  });
  it("preserves a protected local destination", () => {
    expect(safeReturnPath("/records?sessionId=123")).toBe("/records?sessionId=123");
  });
});
describe("Vietnamese record search", () => {
  it("matches unaccented queries and đ", () => {
    expect(matchesSearch("pham duc", "Phạm Đức Huy")).toBe(true);
    expect(matchesSearch("LE PHUONG", "Lê Phương Linh", "Thiết kế")).toBe(true);
    expect(matchesSearch("CNTT", "Nguyễn Minh Anh", "CNTT · K24")).toBe(true);
    expect(matchesSearch("unknown", "Nguyễn Minh Anh")).toBe(false);
  });
});
