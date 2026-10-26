import { apiFetch } from "@/api/client";

export type Stage = { id: number; title: string; range: string; focus: string; weeks: string };
export type Card = { id: string; lesson_id: string; term: string; meaning: string; example: string; version: number; due: string | null; reviews: number };
export type Lesson = { id: string; title: string; stage: number; part: number; minutes: number; question_count: number; objectives: string[]; sections?: {title: string; body: string}[]; practice_rule: string; vocabulary?: Card[] };
export type Catalog = { version: string; notice: string; stages: Stage[]; lessons: Lesson[]; question_count: number; vocabulary_count: number; sources: {id: string; title: string; url: string; provider: string; access: string; stage: string; usage: string}[] };
export type Result = { correct: number; total: number; percent: number; parts: {part: number; correct: number; total: number; percent: number}[]; suggested_stage: number; score_notice: string };
export type Question = { id: string; lesson_id: string; part: number; prompt: string; options: string[]; passage?: string; group_id?: string; audio_id?: string; image?: string; correct?: number; explanation?: string; transcript?: string };
export type Answers = Record<string, number | null>;
export type Attempt = { id: string; kind: string; lesson_id?: string; status: "active" | "submitted"; started_at: string; deadline: string; server_now: string; revision: number; answers: Answers; questions: Question[]; result?: Result };
export type Progress = { target: number; daily_minutes: number; lessons: Record<string, number>; recent: (Omit<Attempt, "questions"> & {submitted_at: string})[]; active: Omit<Attempt, "questions">[]; streak: number; cards_learned: number; cards_due: number; days: {day: string; questions?: number; reviews?: number}[] };
const call = <T>(path: string, method = "GET", body?: unknown) => apiFetch<T>(`/api/toeic${path}`, {method, ...(body === undefined ? {} : {body: JSON.stringify(body)})});
export const toeicApi = {
  catalog: () => call<Catalog>("/catalog"),
  progress: () => call<Progress>("/progress"),
  lesson: (id: string) => call<Lesson>(`/lessons/${encodeURIComponent(id)}`),
  preferences: (target: number, daily_minutes: number) => call("/preferences", "PUT", {target, daily_minutes}),
  start: (kind: string, request_id: string, lesson_id?: string, part?: number) => call<Attempt>("/attempts", "POST", {kind, request_id, ...(lesson_id ? {lesson_id} : {}), ...(part ? {part} : {})}),
  attempt: (id: string) => call<Attempt>(`/attempts/${id}`),
  save: (id: string, answers: Answers, revision: number) => call<{revision: number}>(`/attempts/${id}/answers`, "PUT", {answers, revision}),
  submit: (id: string, answers: Answers, revision: number) => call<Attempt>(`/attempts/${id}/submit`, "POST", {answers, revision}),
  vocabulary: () => call<Card[]>("/vocabulary"),
  review: (id: string, rating: number, expected_version: number, event_id: string) => call<{due: string; version: number}>(`/vocabulary/${id}/review`, "POST", {rating, expected_version, event_id}),
};
export const partNames = ["", "Mô tả hình", "Hỏi – đáp", "Hội thoại", "Bài nói", "Hoàn thành câu", "Hoàn thành đoạn", "Đọc hiểu"];
export const dateTime = (value: string) => new Date(value).toLocaleString("vi-VN", {dateStyle: "short", timeStyle: "short"});
export const kindName = (kind: string) => ({lesson: "Bài học", part: "Luyện Part", diagnostic: "Khảo sát đầu vào", mock: "Đề luyện 200 câu"}[kind] || kind);
