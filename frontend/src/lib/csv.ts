/** Quote every CSV cell and neutralize formula prefixes in user-authored text. */
export function csvCell(value: string | number | null | undefined): string {
  if (typeof value === "number") return Number.isFinite(value) ? String(value) : "";
  let text = value ?? "";
  if (/^[\s\uFEFF]*[=+@-]/.test(text) || /^[\t\r\n]/.test(text)) text = `'${text}`;
  return `"${text.replace(/"/g, '""')}"`;
}

export function csvDocument(rows: (string | number | null | undefined)[][]): string {
  return "\uFEFF" + rows.map((row) => row.map(csvCell).join(",")).join("\r\n");
}

/** RFC 4180-style fields, escaped quotes and embedded newlines; reject malformed input. */
export function parseCsv(input: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [], field = "", quoted = false, closed = false;
  const text = input.replace(/^\uFEFF/, "");
  const cell = () => { row.push(field); field = ""; closed = false; };
  const finish = () => { cell(); if (row.some((v) => v.trim())) rows.push(row); row = []; };
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') { quoted = false; closed = true; }
      else field += c;
    } else if (c === ',') cell();
    else if (c === '\r' || c === '\n') { if (c === '\r' && text[i + 1] === '\n') i++; finish(); }
    else if (c === '"' && !field && !closed) quoted = true;
    else if (closed || c === '"') throw new Error(`CSV: dấu ngoặc kép không hợp lệ ở dòng ${rows.length + 1}.`);
    else field += c;
  }
  if (quoted) throw new Error("CSV: thiếu dấu ngoặc kép đóng.");
  if (field || row.length || closed) finish();
  return rows;
}

export function downloadCsv(name: string, rows: (string | number | null | undefined)[][]): void {
  const url = URL.createObjectURL(new Blob([csvDocument(rows)], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a"); link.href = url; link.download = name;
  document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
