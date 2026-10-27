import { useCallback, useEffect, useRef, useState } from "react";
import { ArrowLeft, ArrowRight, BookOpen, CheckCircle2, Clock3, ExternalLink, Flame, Headphones, Layers3, Play, RefreshCw, Target, Volume2 } from "lucide-react";
import { AttemptRunner } from "./AttemptRunner";
import { CurriculumRoadmap } from "./CurriculumRoadmap";
import { toeicApi, partNames, dateTime, kindName, type Catalog, type Progress, type Lesson, type Attempt, type Card } from "./api";
import "./toeic.css";

const tabs = ["Lộ trình", "Luyện tập", "Từ vựng", "Tiến độ", "Nguồn học"];
export function ToeicPage({preview = false}: {preview?: boolean}) {
  const [catalog, setCatalog] = useState<Catalog>();
  const [progress, setProgress] = useState<Progress>();
  const [tab, setTab] = useState(0);
  const [stage, setStage] = useState(0);
  const [roadmapMode, setRoadmapMode] = useState<"sessions" | "library">("sessions");
  const [sessionId, setSessionId] = useState<string>();
  const [lesson, setLesson] = useState<Lesson>();
  const [attempt, setAttempt] = useState<Attempt>();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [target, setTarget] = useState(650);
  const [minutes, setMinutes] = useState(30);
  const [message, setMessage] = useState("");
  const pending = useRef<{key: string; id: string} | null>(null);
  const actionLock = useRef(false);
  const refresh = useCallback(async () => { const p = await toeicApi.progress(); setProgress(p); setTarget(p.target); setMinutes(p.daily_minutes); }, []);
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try { const [c, p] = await Promise.all([toeicApi.catalog(), toeicApi.progress()]); setCatalog(c); setProgress(p); setTarget(p.target); setMinutes(p.daily_minutes); }
    catch (e) { setError((e as Error).message); } finally { setLoading(false); }
  }, []);
  useEffect(() => { void load(); }, [load]);
  async function action(work: () => Promise<void>) {
    if (actionLock.current) return;
    actionLock.current = true; setBusy(true); setError(""); setMessage("");
    try { await work(); } catch (e) { setError((e as Error).message); } finally { setBusy(false); actionLock.current = false; }
  }
  const openLesson = (id: string) => void action(async () => { setLesson(await toeicApi.lesson(id)); window.scrollTo({top: 0, behavior: "instant"}); });
  const start = (kind: string, lessonId?: string, part?: number) => void action(async () => {
    if (preview) return;
    const key = `${kind}:${lessonId || ""}:${part || ""}`;
    if (pending.current?.key !== key) pending.current = {key, id: crypto.randomUUID()};
    setAttempt(await toeicApi.start(kind, pending.current.id, lessonId, part)); pending.current = null;
    window.scrollTo({top: 0, behavior: "instant"});
  });
  const resume = (id: string) => void action(async () => { setAttempt(await toeicApi.attempt(id)); window.scrollTo({top: 0, behavior: "instant"}); });
  const completed = catalog?.lessons.filter(l => (progress?.lessons[l.id] || 0) >= 70).length || 0;
  const nextLesson = catalog?.lessons.find(l => (progress?.lessons[l.id] || 0) < 70) || catalog?.lessons[0];
  const weakPart = progress?.recent.flatMap(a => a.result?.parts || []).reduce<Record<number, {correct: number; total: number}>>((all, p) => { const prior = all[p.part] || {correct: 0, total: 0}; all[p.part] = {correct: prior.correct + p.correct, total: prior.total + p.total}; return all; }, {});
  const weakest = weakPart && Object.entries(weakPart).sort((a,b) => a[1].correct/a[1].total - b[1].correct/b[1].total)[0];

  function beginLearning() {
    if (catalog?.curriculum) {
      setTab(0); setRoadmapMode("sessions");
      setSessionId((catalog.curriculum.sessions.find(s => !progress?.curriculum_completed?.includes(s.id)) || catalog.curriculum.sessions[0]).id);
      requestAnimationFrame(() => document.getElementById("toeic-curriculum")?.scrollIntoView({behavior: "smooth"}));
    } else if (nextLesson) openLesson(nextLesson.id);
  }

  if (loading) return <div className="toeic-page toeic-loading" role="status"><BookOpen/><p>Đang mở góc học tiếng Anh…</p></div>;
  if (!catalog || !progress) return <div className="toeic-page"><div className="toeic-alert" role="alert">{error || "Chưa tải được học liệu."}<button onClick={() => void load()}>Tải lại</button></div></div>;
  if (attempt) return <main className="toeic-page"><AttemptRunner key={attempt.id} initial={attempt} onComplete={() => { void refresh().catch(e => setError(e.message)); }} onExit={() => {setAttempt(undefined); setLesson(undefined); void refresh().catch(e => setError(e.message));}}/></main>;
  return <main className="toeic-page">
    {preview && <div className="toeic-preview">Đang xem thử học liệu. Đăng nhập tài khoản thật để làm bài và lưu tiến độ.</div>}
    {error && <div className="toeic-alert" role="alert">{error}<button onClick={() => setError("")}>Đóng thông báo</button></div>}
    {lesson ? <>
      <button className="toeic-button secondary" onClick={() => setLesson(undefined)}><ArrowLeft size={16}/>Về lộ trình</button>
      <header className="toeic-lesson-header"><span className="toeic-eyebrow">CHẶNG {lesson.stage + 1} · PART {lesson.part}</span><h1>{lesson.title}</h1><p>{lesson.minutes} phút gợi ý · {catalog.lessons.find(l => l.id === lesson.id)?.question_count} câu luyện · đạt từ 70% để hoàn thành</p></header>
      <div className="toeic-study-layout"><article className="toeic-lesson-body"><section><h2>Sau bài này, bạn có thể</h2><ul>{lesson.objectives.map(o => <li key={o}>{o}</li>)}</ul></section>{lesson.sections?.map((s,i) => <section key={s.title} className={i === 1 ? "examples" : ""}><span className="toeic-eyebrow">0{i+1}</span><h2>{s.title}</h2><p>{s.body}</p></section>)}<div className="toeic-note"><strong>Học đến đâu, thực hành đến đó.</strong><p>{lesson.practice_rule}</p></div><button className="toeic-button" disabled={busy || preview} onClick={() => start("lesson", lesson.id)}><Play size={16}/>Luyện bài này</button></article><aside className="toeic-lesson-vocab"><h2>10 từ đi cùng bài</h2>{lesson.vocabulary?.map(c => <details key={c.id}><summary lang="en">{c.term}</summary><p>{c.meaning}</p><small lang="en">{c.example}</small></details>)}<button className="toeic-button secondary" onClick={() => {setLesson(undefined); setTab(2);}}>Mở thẻ ôn tập<ArrowRight size={16}/></button></aside></div>
    </> : <>
      <header className="toeic-hero"><div><span className="toeic-eyebrow">DHV ENGLISH STUDIO · LISTENING & READING</span><h1>TOEIC cùng DHV<span>Mỗi ngày một bước tiến.</span></h1><p>Từ nền tảng đến mục tiêu 900. Học rõ bản chất, nghe có ngữ cảnh và biết vì sao mình chọn đúng.</p><div className="toeic-actions"><button className="toeic-button" onClick={beginLearning} disabled={busy}><BookOpen size={17}/>{completed || progress.curriculum_completed?.length ? "Tiếp tục lộ trình" : "Bắt đầu học"}<ArrowRight size={16}/></button><button className="toeic-button secondary" onClick={() => {setTab(1);}}><Headphones size={17}/>Góc luyện tập</button></div></div><div className="toeic-goal-card"><span>MỤC TIÊU CỦA BẠN</span><strong>{progress.target}<small>TOEIC L&R</small></strong><div><Clock3 size={16}/>{progress.daily_minutes} phút mỗi ngày</div><div><Flame size={16}/>{progress.streak} ngày học liên tiếp</div><p>Mục tiêu định hướng học, không phải điểm dự đoán.</p></div></header>
      <div className="toeic-stats"><div><strong>{completed}<span> / {catalog.lessons.length}</span></strong><span>bài luyện đạt từ 70%</span></div><div><strong>{catalog.question_count}</strong><span>câu luyện có giải thích</span></div><div><strong>{progress.cards_learned}<span> / {catalog.vocabulary_count}</span></strong><span>từ đã bắt đầu ôn</span></div><div><strong>{progress.cards_due}</strong><span>từ đến hạn hôm nay</span></div></div>
      <nav className="toeic-tabs" aria-label="Các khu vực học TOEIC">{tabs.map((name,i) => <button key={name} aria-current={tab === i ? "page" : undefined} onClick={() => {setTab(i); setMessage("");}}>{name}</button>)}</nav>
      {tab === 0 && catalog.curriculum && <div className="toeic-roadmap-mode" role="group" aria-label="Cách xem lộ trình"><button aria-pressed={roadmapMode === "sessions"} onClick={() => setRoadmapMode("sessions")}>Học theo buổi</button><button aria-pressed={roadmapMode === "library"} onClick={() => setRoadmapMode("library")}>Thư viện {catalog.lessons.length} bài luyện</button></div>}
      {tab === 0 && catalog.curriculum && roadmapMode === "sessions" && <CurriculumRoadmap curriculum={catalog.curriculum} catalog={catalog} completed={progress.curriculum_completed || []} selectedId={sessionId} onSelect={setSessionId} onOpenLesson={openLesson} onPractice={() => setTab(1)} busy={busy} preview={preview} error={error} onComplete={(id, done) => {setSessionId(id); void action(async () => {await toeicApi.completeSession(id, done); await refresh();});}}/>}
      {tab === 0 && (!catalog.curriculum || roadmapMode === "library") && <><div className="toeic-section-heading"><div><span className="toeic-eyebrow">LỘ TRÌNH CỦA BẠN</span><h2>Vững nền tảng, rồi tăng tốc.</h2><p>Các mốc điểm là định hướng. Bạn có thể mở bất kỳ chặng nào để học hoặc ôn lại.</p></div><span className="toeic-pill">{catalog.stages.length} chặng · {catalog.lessons.length} bài</span></div><div className="toeic-roadmap"><aside className="toeic-stages" aria-label="Chọn chặng học">{catalog.stages.map(s => <button key={s.id} className={stage === s.id ? "active" : ""} aria-pressed={stage === s.id} onClick={() => setStage(s.id)}><span>{String(s.id+1).padStart(2,"0")}</span><div><strong>{s.range}</strong><small>{s.title}</small></div><ArrowRight size={16}/></button>)}</aside><div className="toeic-stage-content"><div className="toeic-stage-intro"><span className="toeic-eyebrow">CHẶNG {stage+1}</span><h2>{catalog.stages[stage].title}</h2><p>{catalog.stages[stage].focus}</p><small>{catalog.stages[stage].weeks} · thời gian thực tế tùy nền tảng và mức luyện</small></div>{catalog.lessons.filter(l => l.stage === stage).map((l,i) => <button className="toeic-lesson-row" key={l.id} onClick={() => openLesson(l.id)} disabled={busy}><span className="toeic-lesson-number">{(progress.lessons[l.id] || 0) >= 70 ? <CheckCircle2 size={24}/> : String(i+1).padStart(2,"0")}</span><div><small>PART {l.part} · {l.minutes} PHÚT</small><h3>{l.title}</h3><p>{l.question_count} câu luyện{progress.lessons[l.id] !== undefined ? ` · tốt nhất ${progress.lessons[l.id]}%` : " · chưa hoàn thành"}</p></div><ArrowRight size={20}/></button>)}</div></div><div className="toeic-note"><strong>Chưa biết bắt đầu ở đâu?</strong><p>Bài khảo sát 25 câu giúp gợi ý chặng học. Kết quả chỉ phản ánh bộ câu hỏi ngắn trong ứng dụng, không phải bài xếp hạng TOEIC chuẩn hóa.</p><button className="toeic-button secondary" onClick={() => start("diagnostic")} disabled={busy || preview}>Làm khảo sát · 25 phút</button></div></>}
      {tab === 1 && <><div className="toeic-section-heading"><div><span className="toeic-eyebrow">PRACTICE MAKES PROGRESS</span><h2>Luyện một kỹ năng, hoặc cả hành trình.</h2><p>Đáp án và giải thích được mở sau khi nộp. Bài đang làm được lưu trên tài khoản.</p></div></div><div className="toeic-practice-featured"><article><Target size={26}/><h3>Khảo sát điểm xuất phát</h3><p>25 câu từ cả 7 phần. Tìm chặng học để bắt đầu và xem kỹ năng cần củng cố.</p><span>25 phút · không quy đổi điểm</span><button className="toeic-button secondary" disabled={busy || preview} onClick={() => start("diagnostic")}>Bắt đầu khảo sát<ArrowRight size={16}/></button></article><article className="featured"><Headphones size={26}/><h3>Đề luyện toàn diện</h3><p>200 câu theo số lượng từng phần của TOEIC L&R. Dùng đồng hồ 120 phút để luyện sức bền.</p><span>120 phút · 100 Listening + 100 Reading</span><button className="toeic-button" disabled={busy || preview} onClick={() => start("mock")}>Bắt đầu 200 câu<ArrowRight size={16}/></button></article></div><div className="toeic-note"><strong>Chế độ luyện tập có hỗ trợ</strong><p>Audio tổng hợp được nghe lại và điều khiển thủ công; chưa khóa riêng 45 phút nghe / 75 phút đọc như kỳ thi. Đề được ghép từ cùng ngân hàng {catalog.question_count} câu nên các lượt có thể trùng. Part 1 dùng hình minh họa. Hãy kết hợp mẫu chính thức tại Nguồn học.</p></div><div className="toeic-parts">{partNames.slice(1).map((name,i) => <article key={name}><span className="toeic-eyebrow">PART {i+1}</span><h3>{name}</h3><p>{[6,10,9,9,10,8,10][i]} câu · luyện theo nhóm nội dung</p><button className="toeic-button secondary" disabled={busy || preview} onClick={() => start("part", undefined, i+1)}>Luyện phần này<ArrowRight size={15}/></button></article>)}</div></>}
      {tab === 2 && <Vocabulary preview={preview} lessons={catalog.lessons} onReviewed={() => void refresh().catch(e => setError(e.message))}/>}
      {tab === 3 && <><div className="toeic-section-heading"><div><span className="toeic-eyebrow">NHÌN LẠI ĐỂ TIẾN LÊN</span><h2>Nhịp học của bạn.</h2><p>Hoàn thành bài hoặc ôn một từ để ghi nhận ngày học theo múi giờ Việt Nam.</p></div><button className="toeic-button secondary" onClick={() => void action(refresh)} disabled={busy}><RefreshCw size={16}/>Cập nhật</button></div><div className="toeic-progress-layout"><section className="toeic-panel"><h3>Thiết lập nhịp học</h3><form onSubmit={e => {e.preventDefault(); void action(async () => {await toeicApi.preferences(target, minutes); await refresh(); setMessage("Đã lưu mục tiêu học.");});}}><label>Mục tiêu định hướng<select value={target} onChange={e => setTarget(Number(e.target.value))}>{[350,550,650,750,900].map(t => <option key={t} value={t}>{t} TOEIC</option>)}</select></label><label>Thời gian mỗi ngày<select value={minutes} onChange={e => setMinutes(Number(e.target.value))}>{[15,30,45,60].map(m => <option key={m} value={m}>{m} phút</option>)}</select></label><button className="toeic-button" disabled={busy || preview}>Lưu mục tiêu</button><p role="status">{message}</p></form></section><section className="toeic-panel"><h3>Gợi ý lượt học tiếp theo</h3>{weakest ? <><p>Trong 20 lượt gần nhất, Part {weakest[0]} có tỷ lệ đúng thấp nhất: {Math.round(100*weakest[1].correct/weakest[1].total)}% ({weakest[1].correct}/{weakest[1].total} câu).</p><button className="toeic-button secondary" disabled={busy || preview} onClick={() => start("part", undefined, Number(weakest[0]))}>Ôn Part {weakest[0]}<ArrowRight size={15}/></button></> : <p>Làm khảo sát hoặc một bài luyện để có gợi ý dựa trên kết quả của bạn.</p>}<p>{progress.cards_due} thẻ đang đến hạn. Ôn nhớ chủ động trước khi học thêm từ mới.</p><button className="toeic-button secondary" onClick={() => setTab(2)}>Mở thẻ từ vựng</button></section></div><section className="toeic-panel"><h3>Bài đang làm</h3>{progress.active.length ? progress.active.map(a => <div className="toeic-history-row" key={a.id}><div><strong>{kindName(a.kind)}</strong><p>Hạn nộp {dateTime(a.deadline)} · thời gian vẫn chạy khi rời trang</p></div><button className="toeic-button secondary" disabled={busy} onClick={() => resume(a.id)}>Tiếp tục</button></div>) : <p>Không có bài đang làm.</p>}</section><section className="toeic-panel"><h3>20 lượt luyện gần nhất</h3>{progress.recent.length ? progress.recent.map(a => <div className="toeic-history-row" key={a.id}><div><strong>{kindName(a.kind)}{a.lesson_id ? ` · ${catalog.lessons.find(l => l.id === a.lesson_id)?.title || a.lesson_id}` : ""}</strong><p>{dateTime(a.submitted_at)} · {a.result?.correct}/{a.result?.total} đúng ({a.result?.percent}%)</p></div><button className="toeic-button secondary" disabled={busy} onClick={() => resume(a.id)}>Xem lời giải</button></div>) : <p>Bài đã nộp sẽ xuất hiện ở đây. Điểm hiển thị là tỷ lệ đúng trong ứng dụng.</p>}</section><section className="toeic-panel"><h3>Nhật ký học · 90 ngày hoạt động gần nhất</h3><div className="toeic-activity">{progress.days.length ? progress.days.map(d => <div key={d.day}><strong>{d.day}</strong><span>{d.questions || 0} câu · {d.reviews || 0} lượt ôn từ</span></div>) : <p>Ngày đầu tiên bắt đầu từ một bài học nhỏ.</p>}</div></section></>}
      {tab === 4 && <><div className="toeic-section-heading"><div><span className="toeic-eyebrow">TỰ HỌC CÓ CHỌN LỌC</span><h2>Học liệu và khóa học đáng tham khảo.</h2><p>Nguồn chính thức được dẫn link để bạn xem điều kiện truy cập, lịch học và học phí trực tiếp.</p></div></div><div className="toeic-sources">{catalog.sources.map(s => <article key={s.id}><span className="toeic-eyebrow">{s.provider} · {s.stage}</span><h3>{s.title}</h3><span className="toeic-pill">{s.access}</span><p>{s.usage}</p><a className="toeic-button secondary" href={s.url} target="_blank" rel="noopener noreferrer">Mở nguồn chính thức<ExternalLink size={15}/></a></article>)}</div><div className="toeic-note"><strong>Học liệu trong DHV</strong><p>{catalog.notice}</p><p>Lộ trình theo buổi kết nối kiến thức, nhiệm vụ tự học, thư viện bài luyện DHV và tài nguyên bên ngoài. Với mục tiêu cao, bổ sung nghe người thật và đề mới có nguồn hợp lệ; cần giáo viên rà soát khi dùng làm đánh giá chính thức.</p></div></>}
      <footer className="toeic-footer">DHV English Studio · Học liệu tự biên soạn · Mục tiêu 900 là định hướng, không bảo đảm kết quả.</footer>
    </>}
  </main>;
}

function Vocabulary({preview, lessons, onReviewed}: {preview: boolean; lessons: Lesson[]; onReviewed: () => void}) {
  const [cards, setCards] = useState<Card[]>([]);
  const [filter, setFilter] = useState("");
  const [search, setSearch] = useState("");
  const [revealed, setRevealed] = useState(false);
  const [selected, setSelected] = useState<string>();
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const lock = useRef(false);
  const event = useRef<{card: string; rating: number; id: string} | null>(null);
  const load = async () => {setLoading(true); setError(""); try {setCards(await toeicApi.vocabulary());} catch(e) {setError((e as Error).message);} finally {setLoading(false);} };
  useEffect(() => {void load(); return () => { if ("speechSynthesis" in window) speechSynthesis.cancel(); };}, []);
  const filtered = cards.filter(c => (!filter || c.lesson_id === filter) && `${c.term} ${c.meaning}`.toLowerCase().includes(search.toLowerCase()));
  const due = filtered.filter(c => c.due && new Date(c.due).getTime() <= Date.now());
  const fresh = filtered.filter(c => !c.due);
  const queue = [...due, ...fresh];
  const card = filtered.find(c => c.id === selected) || queue[0];
  const canReview = card && (!card.due || new Date(card.due).getTime() <= Date.now());
  useEffect(() => { setRevealed(false); }, [card?.id]);
  async function review(rating: number) {
    if (!card || preview || lock.current) return;
    lock.current = true; setBusy(true); setError("");
    if (event.current?.card !== card.id || event.current.rating !== rating) event.current = {card: card.id, rating, id: crypto.randomUUID()};
    try {const result = await toeicApi.review(card.id, rating, card.version, event.current.id); setCards(old => old.map(c => c.id === card.id ? {...c, ...result, reviews: c.reviews+1} : c)); setNotice(`Đã ôn “${card.term}”. Lần tới: ${dateTime(result.due)}.`); setSelected(undefined); setRevealed(false); event.current = null; onReviewed();}
    catch(e) {setError((e as Error).message);} finally {setBusy(false); lock.current = false;}
  }
  const speak = () => { if (!card || !("speechSynthesis" in window)) {setNotice("Trình duyệt chưa hỗ trợ đọc từ. Bạn vẫn có thể luyện nghe ở từng bài học."); return;} speechSynthesis.cancel(); const utterance = new SpeechSynthesisUtterance(card.term); utterance.lang="en-US"; utterance.rate=.85; utterance.onerror=()=>setNotice("Không phát được giọng đọc trên thiết bị này. Hãy dùng audio trong bài học."); speechSynthesis.speak(utterance); };
  return <><div className="toeic-section-heading"><div><span className="toeic-eyebrow">NHỚ LÂU BẰNG ÔN ĐÚNG LÚC</span><h2>200 từ, học trong ngữ cảnh.</h2><p>Tự nhớ nghĩa trước khi lật thẻ. FSRS dùng mức nhớ của bạn để lên lịch ôn tiếp theo.</p></div><Layers3 size={28}/></div><div className="toeic-vocab-filters"><label>Lọc theo bài<select value={filter} onChange={e=>{setFilter(e.target.value);setSelected(undefined);}}><option value="">Tất cả bài học</option>{lessons.map(l=><option key={l.id} value={l.id}>{l.title}</option>)}</select></label><label>Tìm từ hoặc nghĩa<input value={search} onChange={e=>{setSearch(e.target.value);setSelected(undefined);}} placeholder="appointment, cuộc hẹn…"/></label></div>{error && <div className="toeic-alert" role="alert">{error}<button onClick={()=>void load()}>Tải lại thẻ</button></div>}<p role="status" className="toeic-muted">{notice || `${due.length} thẻ đến hạn · ${fresh.length} thẻ mới trong bộ lọc`}</p>{loading ? <p role="status">Đang tải thẻ…</p> : <div className="toeic-vocab-layout"><section className="toeic-flashcard">{card ? <><span className="toeic-eyebrow">{card.due ? "THẺ ĐÃ HỌC" : "TỪ MỚI"} · {lessons.find(l=>l.id===card.lesson_id)?.title}</span><h3 lang="en">{card.term}</h3><button className="toeic-button secondary" onClick={speak}><Volume2 size={18}/>Nghe từ</button>{revealed ? <div className="toeic-card-answer"><h4>{card.meaning}</h4><p lang="en">{card.example}</p>{canReview ? <><p>Bạn nhớ ở mức nào?</p><div className="toeic-ratings">{["Học lại", "Khó", "Nhớ được", "Dễ"].map((r,i)=><button key={r} disabled={busy || preview} onClick={()=>void review(i+1)}>{r}</button>)}</div></> : <p>Lần ôn tiếp: {card.due && dateTime(card.due)}. Bạn vẫn có thể đọc lại nghĩa và ví dụ.</p>}</div> : <button className="toeic-button" onClick={()=>setRevealed(true)}>Hiện nghĩa & ví dụ</button>}</> : <><CheckCircle2 size={44}/><h3>{filtered.length ? "Đã ôn xong các thẻ đang đến hạn." : "Chưa có từ khớp bộ lọc."}</h3><p>Chọn một từ bên cạnh để đọc lại hoặc đổi bộ lọc.</p><button className="toeic-button secondary" onClick={()=>void load()}>Kiểm tra lịch ôn</button></>}</section><aside className="toeic-word-list"><h3>Kho từ của bạn · {filtered.length}</h3><p>Chọn từ để xem lại. Chỉ thẻ mới hoặc đến hạn mới được chấm mức nhớ.</p><div>{filtered.map(c=><button key={c.id} disabled={busy} className={card?.id===c.id ? "active" : ""} onClick={()=>setSelected(c.id)}><strong lang="en">{c.term}</strong><small>{!c.due ? "Mới" : new Date(c.due).getTime()<=Date.now() ? "Đến hạn" : "Đã lên lịch"}</small></button>)}</div></aside></div>}</>;
}
