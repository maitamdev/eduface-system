import { useCallback, useEffect, useRef, useState } from "react";
import { ArrowLeft, ArrowRight, Check, Flag, Headphones } from "lucide-react";
import { toeicApi, partNames, kindName, type Attempt, type Answers } from "./api";

export function AttemptRunner({initial, onExit, onComplete}: {initial: Attempt; onExit: () => void; onComplete: () => void}) {
  const [attempt, setAttempt] = useState(initial);
  const [answers, setAnswers] = useState<Answers>(initial.answers);
  const [index, setIndex] = useState(0);
  const [flags, setFlags] = useState<Set<string>>(new Set());
  const [status, setStatus] = useState("Đã đồng bộ");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const [audioError, setAudioError] = useState(false);
  const dialogRef = useRef<HTMLDivElement>(null);
  const revision = useRef(initial.revision);
  const latest = useRef(initial.answers);
  const dirty = useRef(false);
  const saving = useRef<Promise<void> | null>(null);
  const locked = useRef(false);
  const alive = useRef(true);
  const done = attempt.status === "submitted";
  const offset = useRef(new Date(initial.server_now).getTime() - Date.now());
  const remaining = () => Math.max(0, Math.ceil((new Date(initial.deadline).getTime() - Date.now() - offset.current) / 1000));
  const [seconds, setSeconds] = useState(remaining);
  const question = attempt.questions[index];
  const answered = Object.values(answers).filter(x => x !== null).length;
  useEffect(() => { alive.current = true; return () => { alive.current = false; }; }, []);
  useEffect(() => { if (done) return; const timer = window.setInterval(() => setSeconds(remaining()), 1000); return () => clearInterval(timer); }, [done]);
  useEffect(() => { setAudioError(false); }, [question.audio_id]);
  useEffect(() => {
    if (!confirm) return;
    const previous = document.activeElement as HTMLElement | null;
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !busy) setConfirm(false);
      if (event.key !== "Tab") return;
      const buttons = dialogRef.current?.querySelectorAll<HTMLButtonElement>("button:not([disabled])");
      if (!buttons?.length) { event.preventDefault(); return; }
      const first = buttons[0], last = buttons[buttons.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener("keydown", handleKey);
    return () => {document.removeEventListener("keydown", handleKey); previous?.focus();};
  }, [confirm, busy]);

  // One serialized queue per attempt, plus server revisions for cross-tab conflicts.
  const flush = useCallback(async (): Promise<void> => {
    if (saving.current) { await saving.current; if (dirty.current) await flush(); return; }
    if (!dirty.current || locked.current) return;
    const snapshot = latest.current;
    dirty.current = false;
    setStatus("Đang lưu…");
    const task = toeicApi.save(initial.id, snapshot, revision.current).then(result => {
      revision.current = result.revision;
      if (alive.current) { setStatus("Đã lưu trên tài khoản"); setError(""); }
    }).catch(e => { dirty.current = true; if (alive.current) { setStatus("Chưa lưu được"); setError(e.message); } throw e; });
    saving.current = task;
    try { await task; } finally { saving.current = null; }
    if (dirty.current) await flush();
  }, [initial.id]);

  useEffect(() => () => { if (dirty.current && remaining() > 0) void flush().catch(() => {}); }, [flush]);

  useEffect(() => {
    if (done || !dirty.current || seconds === 0) return;
    const timer = setTimeout(() => { void flush().catch(() => {}); }, 450);
    return () => clearTimeout(timer);
  }, [answers, done, flush]);
  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => { if (dirty.current || saving.current) { event.preventDefault(); event.returnValue = ""; } };
    const online = () => { if (!done && remaining() > 0) void flush().catch(() => {}); };
    window.addEventListener("beforeunload", warn); window.addEventListener("online", online);
    return () => { window.removeEventListener("beforeunload", warn); window.removeEventListener("online", online); };
  }, [done, flush]);

  async function submit() {
    if (locked.current) return;
    locked.current = true; setBusy(true); setError("");
    try {
      if (saving.current) await saving.current;
      // Submit contains the newest answers. Expired attempts are graded from the server's saved copy.
      const result = await toeicApi.submit(initial.id, latest.current, revision.current);
      dirty.current = false; setAttempt(result); setAnswers(result.answers); latest.current = result.answers;
      setConfirm(false); setStatus("Đã nộp bài"); onComplete();
    } catch (e) { setError((e as Error).message); } finally { locked.current = false; setBusy(false); }
  }
  const autoSubmitted = useRef(false);
  useEffect(() => { if (!done && seconds === 0 && !autoSubmitted.current) { autoSubmitted.current = true; void submit(); } }, [seconds, done]);
  async function leave() {
    if (busy) return;
    setBusy(true);
    try { if (!done && remaining() > 0) await flush(); onExit(); }
    catch { /* Keep the learner here with their unsaved answers. */ }
    finally { setBusy(false); }
  }
  const choose = (value: number) => {
    if (done || busy || seconds === 0) return;
    const next = {...latest.current, [question.id]: value}; latest.current = next; dirty.current = true; setAnswers(next); setStatus("Có thay đổi chưa lưu");
  };
  const navigate = (next: number) => { setIndex(next); document.querySelector<HTMLElement>(".toeic-question-title")?.focus(); };

  return <div className="toeic-runner">
    <div className="toeic-runner-bar"><button className="toeic-button secondary" onClick={() => void leave()} disabled={busy}><ArrowLeft size={16}/> {done ? "Về góc học tập" : "Lưu & về góc học tập"}</button><span>{attempt.title || kindName(attempt.kind)}</span><strong className={seconds < 300 && !done ? "toeic-danger" : ""}>{done ? "Đã hoàn thành" : `${Math.floor(seconds / 60).toString().padStart(2, "0")}:${(seconds % 60).toString().padStart(2, "0")}`}</strong></div>
    {done && attempt.result && <section className="toeic-result" aria-label="Kết quả luyện tập"><div><span className="toeic-eyebrow">KẾT QUẢ CỦA BẠN</span><h2>{attempt.result.correct}<small> / {attempt.result.total} câu đúng</small></h2><p>{attempt.result.score_notice}</p>{attempt.kind === "diagnostic" && <p>Gợi ý bắt đầu: chặng {attempt.result.suggested_stage + 1}. Đây là gợi ý từ bài khảo sát ngắn; hãy điều chỉnh theo mức độ hiểu bài.</p>}</div><div className="toeic-result-parts">{attempt.result.parts.map(p => <div key={p.part}><span>Part {p.part}</span><strong>{p.correct}/{p.total}</strong><progress max={100} value={p.percent} aria-label={`Part ${p.part}: ${p.percent}%`}/></div>)}</div></section>}
    {error && <div role="alert" className="toeic-alert"><p>{error}</p><button onClick={() => void flush().catch(() => {})} disabled={busy || seconds === 0}>Thử lưu lại</button><button onClick={async () => { if (busy) return; setBusy(true); try { const fresh = await toeicApi.attempt(initial.id); setAttempt(fresh); setAnswers(fresh.answers); latest.current = fresh.answers; revision.current = fresh.revision; dirty.current = false; setError(""); } catch (e) { setError((e as Error).message); } finally {setBusy(false);} }}>Lấy bản đã lưu (bỏ thay đổi chưa lưu)</button></div>}
    {!done && seconds === 0 && <div className="toeic-alert">Đã hết giờ. Máy chủ chấm theo đáp án được lưu đúng hạn. {error && <button onClick={() => void submit()} disabled={busy}>Nộp lại bài đã lưu</button>}</div>}
    <div className="toeic-exam-layout"><section className="toeic-question">
      <div className="toeic-question-top"><span className="toeic-pill">PART {question.part} · {partNames[question.part]}</span><button className="toeic-button secondary" aria-pressed={flags.has(question.id)} onClick={() => setFlags(previous => { const next = new Set(previous); next.has(question.id) ? next.delete(question.id) : next.add(question.id); return next; })}><Flag size={15}/>{flags.has(question.id) ? "Đã đánh dấu" : "Xem lại"}</button></div>
      {question.passage && <div className="toeic-passage" lang="en">{question.passage}</div>}
      {question.image && <figure><img src={question.image} alt="Hình minh họa dùng cho câu hỏi nghe"/><figcaption>{question.image_credit || "Hình minh họa tự tạo · luyện mô tả, không phải ảnh đề thi."}</figcaption></figure>}
      {question.graphic && <div className="toeic-graphic"><table lang="en"><caption>{question.graphic.title}</caption><thead><tr>{question.graphic.columns.map(c => <th scope="col" key={c}>{c}</th>)}</tr></thead><tbody>{question.graphic.rows.map((row,i) => <tr key={i}>{row.map((cell,j) => <td key={j}>{cell}</td>)}</tr>)}</tbody></table></div>}
      {question.audio_id && <div className="toeic-audio"><span><Headphones size={17}/> Nghe đoạn {question.group_id ? "hội thoại / bài nói dùng chung" : "câu hỏi"}</span><audio key={question.audio_id} controls preload="metadata" src={`/toeic/audio/${question.audio_id}.wav`} onError={() => setAudioError(true)}/><small>Giọng tổng hợp · có thể nghe lại khi luyện tập.</small>{audioError && <p role="alert">Không tải được âm thanh. Kiểm tra kết nối rồi tải lại trang; không thể làm câu nghe này khi thiếu audio.</p>}</div>}
      <h2 className="toeic-question-title" tabIndex={-1}><span>Câu {index + 1}.</span> <span lang="en">{question.prompt}</span></h2>
      <fieldset className="toeic-options" disabled={done || busy || seconds === 0}><legend className="sr-only">Chọn đáp án cho câu {index + 1}</legend>{question.options.map((option, i) => <label key={`${question.id}-${i}`} className={`${answers[question.id] === i ? "selected" : ""} ${done && question.correct === i ? "correct" : ""} ${done && answers[question.id] === i && question.correct !== i ? "wrong" : ""}`}><input type="radio" name={question.id} checked={answers[question.id] === i} onChange={() => choose(i)}/><b>{String.fromCharCode(65+i)}</b><span lang="en">{question.part <= 2 && !done ? `Lựa chọn ${String.fromCharCode(65+i)} trong audio` : option}</span>{done && question.correct === i && <Check size={18} aria-label="Đáp án đúng"/>}</label>)}</fieldset>
      {done && <div className="toeic-explanation"><strong>{answers[question.id] == null ? "Bạn chưa trả lời." : answers[question.id] === question.correct ? "Chính xác." : "Cùng xem lại nhé."} Đáp án {String.fromCharCode(65 + question.correct!)}.</strong><p>{question.explanation}</p>{question.evidence && <blockquote className="toeic-evidence" lang="en">{question.evidence}</blockquote>}{question.provenance?.url && <p><a href={question.provenance.url} target="_blank" rel="noopener noreferrer">Nguồn câu hỏi: {question.provenance.provider}{question.provenance.license ? " · " + question.provenance.license : ""}</a></p>}{question.transcript && <details><summary>Transcript · đọc sau khi nghe</summary><p lang="en">{question.transcript}</p></details>}</div>}
      <div className="toeic-runner-bar"><button className="toeic-button secondary" disabled={index === 0} onClick={() => navigate(index - 1)}><ArrowLeft size={16}/>Trước</button><span>{index+1} / {attempt.questions.length}</span><button className="toeic-button" disabled={index === attempt.questions.length - 1} onClick={() => navigate(index + 1)}>Tiếp<ArrowRight size={16}/></button></div>
    </section><aside className="toeic-question-map"><h3>Bản đồ câu hỏi</h3><p>{answered}/{attempt.questions.length} câu đã chọn</p><div>{attempt.questions.map((q, i) => <button key={q.id} aria-label={`Câu ${i+1}${answers[q.id] != null ? ", đã trả lời" : ", chưa trả lời"}${flags.has(q.id) ? ", đánh dấu" : ""}`} aria-current={i === index ? "step" : undefined} className={`${i === index ? "current" : ""} ${answers[q.id] != null ? "answered" : ""} ${flags.has(q.id) ? "flagged" : ""} ${done && answers[q.id] !== q.correct ? "missed" : ""}`} onClick={() => navigate(i)}>{i+1}{flags.has(q.id) && <sup>•</sup>}</button>)}</div><small aria-live="polite">{status}</small>{!done && <><button className="toeic-button" onClick={() => setConfirm(true)} disabled={busy}>Nộp bài</button><p className="toeic-muted">Có thể rời trang bằng nút “Lưu & về” rồi tiếp tục từ tiến độ của bạn. Thời gian vẫn chạy.</p></>}</aside></div>
    {confirm && !done && <div ref={dialogRef} className="toeic-confirm" role="dialog" aria-modal="true" aria-labelledby="toeic-submit-title"><div><h2 id="toeic-submit-title">Nộp bài luyện?</h2><p>Bạn đã trả lời {answered}/{attempt.questions.length} câu. {attempt.questions.length - answered > 0 ? "Câu bỏ trống được tính là chưa đúng." : "Sau khi nộp, bạn có thể xem lời giải từng câu."}</p><div className="toeic-actions"><button autoFocus className="toeic-button secondary" onClick={() => setConfirm(false)} disabled={busy}>Tiếp tục làm</button><button className="toeic-button" onClick={() => void submit()} disabled={busy}>{busy ? "Đang nộp…" : "Xác nhận nộp"}</button></div></div></div>}
  </div>;
}
