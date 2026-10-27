import { apiFetch } from "@/api/client";

export type Stage = { id: number; title: string; range: string; focus: string; weeks: string };
export type PosTag = "n" | "v" | "adj" | "adv" | "prep" | "conj" | "pron" | "det" | "interj";
export type Card = { id: string; lesson_id: string; term: string; ipa?: string; pos?: PosTag[]; meaning: string; example: string; version: number; due: string | null; reviews: number };
export type LexiconSource = {id: string; name: string; authors: string; url: string; license: string; license_url: string};
export type LexiconWord = {id: string; term: string; ipa?: string; pos?: PosTag[]; meaning_vi?: string; example?: string; vi_source?: string; meaning_language: "en"; definitions: {source_id: string; text: string; source_term: string; adapted_by_dhv: boolean}[]; lists: {id: string; rank: number | null; supplemental: boolean}[]};
export type LexiconCard = Card & LexiconWord & {meaning_en?: string};
export type LexiconFilters = {deck: "all" | "ngsl" | "tsl"; q: string; state: "all" | "due" | "new" | "learned"; pos?: "all" | "n" | "v" | "adj" | "adv" | "func"; letter?: string; offset: number; limit: number};
export type LexiconPage = {version: string; total: number; word_count: number; offset: number; limit: number; due_count: number; new_count: number; items: LexiconCard[]; license: string; license_url: string; sources: LexiconSource[]; download_url: string; handbook_url?: string; attribution_url: string};
export type Lesson = { id: string; title: string; stage: number; part: number; minutes: number; question_count: number; objectives: string[]; sections?: {title: string; body: string}[]; practice_rule: string; vocabulary?: Card[] };
export type StudySession = {
  id: string; level_id: string; number: number; title: string; skill: string; minutes: number;
  objectives: string[]; knowledge: string[]; examples: {text: string; explanation: string}[];
  checks: {prompt: string; options: string[]; correct: number; explanation: string}[];
  practice: string[]; homework: string[]; lesson_ids: string[]; source_ids: string[];
  vocabulary_focus: string[]; checkpoint: string | null; agenda: {minutes: number; task: string}[];
};
export type Curriculum = {
  version: string; title: string; reviewed_on: string; description: string; notice: string;
  entry: string[]; daily_routine: {minutes: number; task: string}[];
  levels: {id: string; name: string; title: string; target: string; session_count: number; entry: string; outcomes: string[]; exit: string; checkpoints: number[]}[];
  sessions: StudySession[];
};
export type PracticeMode = "topics" | "exams" | "review" | "parts";
export type Topic = {id: string; part: number; title: string; recognition: string; rules: string[]; steps: string[]; traps: string[]; example: {text: string; explanation: string}; source_ids: string[]; question_count: number};
export type Exam = {id: string; title: string; type: "full" | "mini" | "listening" | "reading"; minutes: number; description: string; notice: string; question_count: number; parts: {part: number; count: number}[]};
export type StartOptions = {topic_id?: string; exam_id?: string};
export type ReviewBook = {window: number; count: number; parts: {part: number; count: number}[]; items: {id: string; part: number; prompt: string; topic_ids: string[]}[]};
export type Catalog = { version: string; notice: string; stages: Stage[]; lessons: Lesson[]; question_count: number; vocabulary_count: number; lexicon_count?: number; curriculum?: Curriculum; topics?: Topic[]; exams?: Exam[]; sources: {id: string; title: string; url: string; provider: string; access: string; stage: string; usage: string}[] };
export type Result = { correct: number; total: number; percent: number; parts: {part: number; correct: number; total: number; percent: number}[]; suggested_stage: number; score_notice: string };
export type Question = { id: string; lesson_id: string; part: number; prompt: string; options: string[]; passage?: string; group_id?: string; audio_id?: string; image?: string; image_credit?: string; correct?: number; explanation?: string; transcript?: string; evidence?: string; graphic?: {title: string; columns: string[]; rows: string[][]}; provenance?: {provider: string; url?: string; license?: string} };
export type Answers = Record<string, number | null>;
export type Attempt = { id: string; kind: string; title?: string; topic_id?: string; exam_id?: string; lesson_id?: string; status: "active" | "submitted"; started_at: string; deadline: string; server_now: string; revision: number; answers: Answers; questions: Question[]; result?: Result };
export type Progress = { target: number; daily_minutes: number; lessons: Record<string, number>; curriculum_completed?: string[]; recent: (Omit<Attempt, "questions"> & {submitted_at: string})[]; active: Omit<Attempt, "questions">[]; streak: number; cards_learned: number; cards_due: number; days: {day: string; questions?: number; reviews?: number}[] };
const call = <T>(path: string, method = "GET", body?: unknown) => apiFetch<T>(`/api/toeic${path}`, {method, ...(body === undefined ? {} : {body: JSON.stringify(body)})});
export const toeicApi = {
  catalog: () => call<Catalog>("/catalog"),
  progress: () => call<Progress>("/progress"),
  lesson: (id: string) => call<Lesson>(`/lessons/${encodeURIComponent(id)}`),
  preferences: (target: number, daily_minutes: number) => call("/preferences", "PUT", {target, daily_minutes}),
  completeSession: (id: string, completed: boolean) => call<{session_id: string; completed: boolean}>(`/curriculum/sessions/${encodeURIComponent(id)}`, "PUT", {completed}),
  start: (kind: string, request_id: string, lesson_id?: string, part?: number, options?: StartOptions) => call<Attempt>("/attempts", "POST", {kind, request_id, ...(lesson_id ? {lesson_id} : {}), ...(part ? {part} : {}), ...options}),
  reviewBook: () => call<ReviewBook>("/review"),
  attempt: (id: string) => call<Attempt>(`/attempts/${id}`),
  save: (id: string, answers: Answers, revision: number) => call<{revision: number}>(`/attempts/${id}/answers`, "PUT", {answers, revision}),
  submit: (id: string, answers: Answers, revision: number) => call<Attempt>(`/attempts/${id}/submit`, "POST", {answers, revision}),
  vocabulary: () => call<Card[]>("/vocabulary"),
  lexicon: (filters: LexiconFilters, signal?: AbortSignal) => apiFetch<LexiconPage>(`/api/toeic/lexicon?${new URLSearchParams(Object.entries(filters).filter(([, value]) => value !== undefined).map(([key, value]) => [key, String(value)]))}`, {signal}),
  review: (id: string, rating: number, expected_version: number, event_id: string) => call<{due: string; version: number}>(`/vocabulary/${id}/review`, "POST", {rating, expected_version, event_id}),
};
export const partNames = ["", "Mô tả hình", "Hỏi – đáp", "Hội thoại", "Bài nói", "Hoàn thành câu", "Hoàn thành đoạn", "Đọc hiểu"];
export const posNames: Record<string, string> = {n: "Danh từ", v: "Động từ", adj: "Tính từ", adv: "Trạng từ", prep: "Giới từ", conj: "Liên từ", pron: "Đại từ", det: "Hạn định từ", interj: "Thán từ"};
export const dateTime = (value: string) => new Date(value).toLocaleString("vi-VN", {dateStyle: "short", timeStyle: "short"});
export const kindName = (kind: string) => ({lesson: "Bài học", part: "Luyện Part", diagnostic: "Khảo sát đầu vào", mock: "Đề luyện 200 câu", topic: "Ôn theo dạng", exam: "Đề thi thử", review: "Ôn câu sai"}[kind] || kind);
