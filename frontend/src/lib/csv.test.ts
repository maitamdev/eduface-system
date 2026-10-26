import { describe, expect, it } from "vitest";
import { csvCell, csvDocument } from "./csv";

describe("CSV exports", () => {
  it.each(["=1+1", "+SUM(A1)", "-1+2", "@SUM(A1)", "  =1", "\t=1", "\n=1"])("neutralizes text that spreadsheet software may execute: %s", (value) => {
    expect(csvCell(value)).toBe(`"'${value}"`);
  });
  it("preserves Unicode, embedded quotes, commas and newlines", () => {
    expect(csvCell('Nguyễn, "An"\nK24')).toBe('"Nguyễn, ""An""\nK24"');
  });
  it("keeps real numbers numeric and adds BOM and CRLF", () => {
    expect(csvDocument([["Họ tên", "Điểm"], ["An", -1.5]])).toBe('\uFEFF"Họ tên","Điểm"\r\n"An",-1.5');
  });
});


it("parses quoted commas, escaped quotes and embedded newlines", async () => {
  const { parseCsv } = await import("./csv");
  expect(parseCsv('ID,"A, B","line 1\nline 2"\r\nSV2,"A ""quoted"" name",CS'))
    .toEqual([["ID", "A, B", "line 1\nline 2"], ["SV2", 'A "quoted" name', "CS"]]);
});
it("rejects unclosed quotes and characters after a closing quote", async () => {
  const { parseCsv } = await import("./csv");
  expect(() => parseCsv('ID,"broken')).toThrow();
  expect(() => parseCsv('ID,"name"unexpected,CS')).toThrow();
});
