export const normalizeSearch = (value: string) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d").replace(/Đ/g, "D").toLocaleLowerCase().trim();
export const matchesSearch = (query: string, ...values: (string | null | undefined)[]) => normalizeSearch(values.filter(Boolean).join(" ")).includes(normalizeSearch(query));
export const errorMessage = (error: unknown) => error instanceof Error ? error.message : "Không thể hoàn tất yêu cầu / Request failed";
export const isDesignPreview = () => import.meta.env.DEV && /^\/design-preview(?:\/|$)/.test(window.location.pathname);
export function appPath(path: string) { return isDesignPreview() ? `/design-preview${path === "/" ? "" : path}` : path; }
export function dateTime(value: string | null, lang: string) {
  if (!value) return "–";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "–" : date.toLocaleString(lang === "vi" ? "vi-VN" : "en-GB", { dateStyle: "short", timeStyle: "short" });
}
