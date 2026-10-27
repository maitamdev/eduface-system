import {useRef, useState} from "react";
import {ArrowRight, BookOpen, Check, CheckCircle2, Clock3, Download, ExternalLink} from "lucide-react";
import type {Catalog, Curriculum, StudySession} from "./api";
import "./curriculum.css";

type Props = {
  curriculum: Curriculum;
  catalog: Catalog;
  completed: string[];
  selectedId?: string;
  onSelect: (id: string) => void;
  onOpenLesson: (id: string) => void;
  onComplete: (id: string, completed: boolean) => void;
  onPractice: () => void;
  busy: boolean;
  preview: boolean;
  error?: string;
};

export function CurriculumRoadmap({curriculum, catalog, completed, selectedId, onSelect, onOpenLesson, onComplete, onPractice, busy, preview, error}: Props) {
  const [weekly, setWeekly] = useState(3);
  const detail = useRef<HTMLElement>(null);
  const session = curriculum.sessions.find(s => s.id === selectedId)
    || curriculum.sessions.find(s => !completed.includes(s.id)) || curriculum.sessions[0];
  const level = curriculum.levels.find(l => l.id === session.level_id)!;
  const rows = curriculum.sessions.filter(s => s.level_id === level.id);
  const finished = curriculum.sessions.filter(s => completed.includes(s.id)).length;
  const weeks = curriculum.levels.reduce((total, l) => total + Math.ceil(l.session_count / weekly), 0);
  const hours = curriculum.sessions.reduce((total, s) => total + s.minutes, 0) / 60;
  const isDone = completed.includes(session.id);

  function select(id: string) {
    onSelect(id);
    if (window.matchMedia?.("(max-width: 900px)").matches) {
      requestAnimationFrame(() => detail.current?.scrollIntoView({behavior: "smooth", block: "start"}));
    }
  }

  return <section className="toeic-curriculum" aria-label="Lộ trình học theo buổi" id="toeic-curriculum">
    <div className="toeic-section-heading">
      <div><span className="toeic-eyebrow">LỘ TRÌNH {curriculum.sessions.length} BUỔI · 4 LEVEL</span>
        <h2>Học theo buổi, biết rõ việc cần làm.</h2><p>{curriculum.description}</p></div>
      <a className="toeic-button secondary" href="/toeic/lo-trinh-dhv.md" download><Download size={16}/>Tải lộ trình (.md)</a>
    </div>

    <div className="toeic-schedule">
      <label>Nhịp học<select value={weekly} onChange={e => setWeekly(Number(e.target.value))}>{[2,3,4].map(n => <option value={n} key={n}>{n} buổi / tuần</option>)}</select></label>
      <div><strong>{weeks} tuần</strong><span>để xếp đủ buổi theo nhịp chọn</span></div>
      <div><strong>{hours.toLocaleString("vi-VN")} giờ</strong><span>trong buổi + tự học 45 phút/ngày</span></div>
      <div><strong>{finished} / {curriculum.sessions.length}</strong><span>buổi bạn đánh dấu đã học</span></div>
    </div>
    <p className="toeic-curriculum-caption">Có thể thêm tuần ôn theo nền tảng. Số tuần xếp lịch không phải thời gian bảo đảm đạt điểm; chọn nhịp ở đây chỉ để xem kế hoạch.</p>

    <details className="toeic-study-guide"><summary>Chọn điểm bắt đầu và cách tự học mỗi ngày</summary>
      <ul>{curriculum.entry.map(x => <li key={x}>{x}</li>)}</ul>
      <ol>{curriculum.daily_routine.map(x => <li key={x.task}><strong>{x.minutes} phút:</strong> {x.task}</li>)}</ol>
    </details>

    <nav className="toeic-levels" aria-label="Chọn level">
      {curriculum.levels.map(l => {
        const count = curriculum.sessions.filter(s => s.level_id === l.id && completed.includes(s.id)).length;
        return <button key={l.id} className={level.id === l.id ? "active" : ""} aria-pressed={level.id === l.id}
          onClick={() => onSelect((curriculum.sessions.find(s => s.level_id === l.id && !completed.includes(s.id)) || curriculum.sessions.find(s => s.level_id === l.id)!).id)}>
          <span className="toeic-eyebrow">{l.name} · {l.session_count} BUỔI</span><strong>{l.title}</strong><span>{l.target}</span>
          <small>{count}/{l.session_count} buổi đã học</small><progress value={count} max={l.session_count} aria-label={`Tiến độ ${l.name}`}/>
        </button>;
      })}
    </nav>

    <div className="toeic-level-intro"><div><span className="toeic-eyebrow">{level.name} · {level.target}</span><h3>{level.title}</h3><p>{level.entry}</p></div>
      <details><summary>Đầu ra và tiêu chí chuyển chặng</summary><ul>{level.outcomes.map(x => <li key={x}>{x}</li>)}</ul><p>{level.exit}</p></details>
    </div>

    <div className="toeic-session-layout">
      <aside className="toeic-session-list" aria-label={`Các buổi ${level.name}`}>
        {rows.map(s => <button key={s.id} aria-pressed={s.id === session.id} className={s.id === session.id ? "active" : ""}
          aria-label={`Buổi ${s.number}: ${s.title}${completed.includes(s.id) ? " · Đã học" : ""}`} onClick={() => select(s.id)}>
          <span className="toeic-session-number">{completed.includes(s.id) ? <CheckCircle2 size={19}/> : String(s.number).padStart(2, "0")}</span>
          <span><small>{s.skill} · {s.minutes} phút</small><strong>{s.title}</strong>{s.checkpoint && <em>Mốc đánh giá</em>}</span>
        </button>)}
      </aside>

      <article className="toeic-session-detail" ref={detail} aria-label={`Nội dung buổi ${session.number}`}>
        <header><span className="toeic-eyebrow">{level.name} / BUỔI {String(session.number).padStart(2, "0")}</span><h2>{session.title}</h2>
          <div className="toeic-session-meta"><span><Clock3 size={15}/>{session.minutes} phút</span><span>{session.skill}</span>{isDone && <span><Check size={15}/>Đã đánh dấu học</span>}</div>
        </header>
        <section><h3>Sau buổi này, bạn có thể</h3><ul>{session.objectives.map(x => <li key={x}>{x}</li>)}</ul></section>
        <section><h3>Kiến thức trọng tâm</h3>{session.knowledge.map(x => <p key={x}>{x}</p>)}</section>
        <section className="toeic-session-examples"><h3>Ví dụ có phân tích</h3>{session.examples.map(x => <div key={x.text}><p>{x.text}</p><p>{x.explanation}</p></div>)}</section>
        <details className="toeic-agenda"><summary>Phân bổ {session.minutes} phút trong buổi</summary><ol>{session.agenda.map(x => <li key={x.task}><strong>{x.minutes} phút</strong> · {x.task}</li>)}</ol></details>
        <section><h3>Luyện trong buổi</h3><ol>{session.practice.map(x => <li key={x}>{x}</li>)}</ol>
          <p className="toeic-curriculum-caption">Dùng bài hỗ trợ bên dưới hoặc nguồn được dẫn. Số câu là khối lượng luyện gợi ý; các bài hỗ trợ được dùng chung giữa nhiều buổi.</p>
          <div className="toeic-supporting-lessons">{session.lesson_ids.map(id => {
            const lesson = catalog.lessons.find(l => l.id === id);
            return lesson && <button key={id} className="toeic-button secondary" onClick={() => onOpenLesson(id)} disabled={busy}><BookOpen size={15}/>{lesson.title}<ArrowRight size={14}/></button>;
          })}</div>
          <button className="toeic-button secondary" onClick={onPractice}>Mở góc luyện tập<ArrowRight size={15}/></button>
        </section>
        <SessionCheck key={session.id} session={session}/>
        <section><h3>Bài tập về nhà</h3><ol>{session.homework.map(x => <li key={x}>{x}</li>)}</ol><p><strong>Cụm từ trọng tâm:</strong> {session.vocabulary_focus.join(" · ")}</p></section>
        {session.checkpoint && <div className="toeic-note"><strong>Mốc đánh giá</strong><p>{session.checkpoint}</p></div>}
        <section><h3>Nguồn học bổ trợ</h3><div className="toeic-session-sources">{session.source_ids.map(id => {
          const source = catalog.sources.find(s => s.id === id);
          return source && <a key={id} href={source.url} target="_blank" rel="noopener noreferrer"><span>{source.title}<small>{source.access}</small></span><ExternalLink size={15}/></a>;
        })}</div></section>
        <footer className="toeic-session-completion"><button className="toeic-button" disabled={busy || preview} onClick={() => onComplete(session.id, !isDone)}>
          <CheckCircle2 size={17}/>{isDone ? "Bỏ đánh dấu đã học" : "Đánh dấu đã học buổi này"}</button>
          {error && <p className="toeic-alert" role="alert">{error}</p>}
          <p>{preview ? "Đăng nhập tài khoản thật để lưu buổi đã học." : "Bạn tự xác nhận đã học; trạng thái được lưu theo tài khoản. Điểm bài luyện được ghi riêng trong Tiến độ."}</p>
        </footer>
      </article>
    </div>
    <div className="toeic-note"><strong>Hiểu đúng tiến độ của bạn</strong><p>{curriculum.notice}</p></div>
  </section>;
}

function SessionCheck({session}: {session: StudySession}) {
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [revealed, setRevealed] = useState(false);
  const answered = Object.keys(answers).length === session.checks.length;
  const correct = session.checks.filter((q,i) => q.correct === answers[i]).length;
  return <section className="toeic-session-check" aria-label="Tự kiểm tra kiến thức">
    <h3>Tự kiểm tra kiến thức</h3><p>Chọn trước, xem giải thích sau. Bài ngắn này không lưu điểm và không thay thế bài nghe bằng audio.</p>
    {session.checks.map((q,i) => <fieldset key={q.prompt}><legend>{i+1}. {q.prompt}</legend>
      {q.options.map((option,j) => <label key={option} className={revealed && q.correct === j ? "correct" : ""}>
        <input type="radio" name={`${session.id}-check-${i}`} checked={answers[i] === j} disabled={revealed}
          onChange={() => setAnswers(previous => ({...previous, [i]: j}))}/><span>{String.fromCharCode(65+j)}. {option}</span></label>)}
      {revealed && <p className="toeic-check-explanation"><strong>{answers[i] === q.correct ? "Đúng." : "Cần xem lại."}</strong> {q.explanation}</p>}
    </fieldset>)}
    {revealed ? <><p role="status">Bạn đúng {correct}/{session.checks.length} câu. Đọc lý do trước khi chuyển buổi.</p><button className="toeic-button secondary" onClick={() => {setAnswers({}); setRevealed(false);}}>Làm lại tự kiểm tra</button></>
      : <button className="toeic-button secondary" disabled={!answered} onClick={() => setRevealed(true)}>Kiểm tra câu trả lời</button>}
  </section>;
}
