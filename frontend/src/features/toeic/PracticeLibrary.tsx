import { useEffect, useState } from "react";
import { ArrowRight, BookOpen, Download, Headphones, RefreshCw } from "lucide-react";
import { partNames, toeicApi, type Catalog, type Exam, type PracticeMode, type ReviewBook, type StartOptions } from "./api";
import "./practice.css";

type Props = {catalog: Catalog; preview: boolean; busy: boolean; mode: PracticeMode; onMode: (mode: PracticeMode) => void; selectedTopicId?: string; onTopic: (id: string) => void; onStart: (kind: string, part?: number, options?: StartOptions) => void};
const modes: {id: PracticeMode; name: string}[] = [{id:"topics",name:"Ôn theo dạng"},{id:"exams",name:"Đề thi thử"},{id:"review",name:"Ôn câu sai"},{id:"parts",name:"Luyện từng Part"}];

export function PracticeLibrary({catalog, preview, busy, mode, onMode, selectedTopicId, onTopic, onStart}: Props) {
  const [part, setPart] = useState(0);
  const [search, setSearch] = useState("");
  const [examType, setExamType] = useState<"all" | Exam["type"]>("all");
  const topics = catalog.topics || [];
  const normalized = (s: string) => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/gi, "d").toLowerCase();
  const filtered = topics.filter(t => (!part || t.part === part) && normalized(`${t.title} ${t.recognition}`).includes(normalized(search)));
  const selected = filtered.find(t => t.id === selectedTopicId) || filtered[0];
  const exams = (catalog.exams || []).filter(e => examType === "all" || e.type === examType);
  return <section className="toeic-practice-library" aria-label="Thư viện ôn tập">
    <div className="toeic-section-heading"><div><span className="toeic-eyebrow">HỌC DẠNG BÀI · LUYỆN ĐỀ · CHỮA LỖI</span><h2>Ôn đúng dạng, luyện đủ ngữ cảnh.</h2><p>{topics.length} chuyên đề · {catalog.question_count} câu trong ngân hàng · {(catalog.exams || []).length} mã đề có sẵn.</p></div></div>
    <nav className="toeic-practice-nav" aria-label="Chọn cách luyện tập">{modes.map(m => <button key={m.id} aria-current={mode === m.id ? "page" : undefined} onClick={() => onMode(m.id)}>{m.name}</button>)}</nav>
    {mode === "topics" && <>
      <div className="toeic-study-filters"><label>Dạng bài theo Part<select value={part} onChange={e => setPart(Number(e.target.value))}><option value={0}>Tất cả 7 Part</option>{partNames.slice(1).map((name,i) => <option key={name} value={i+1}>Part {i+1} · {name}</option>)}</select></label><label>Tìm chuyên đề<input type="search" value={search} onChange={e => setSearch(e.target.value)} placeholder="bị động, câu gián tiếp, chèn câu…"/></label><a className="toeic-button secondary" href="/toeic/so-tay-dang-bai.md" download><Download size={16}/>Tải sổ tay</a></div>
      {selected ? <div className="toeic-topic-layout"><aside className="toeic-topic-list" aria-label="Danh sách dạng bài"><p>{filtered.length} chuyên đề khớp bộ lọc</p>{filtered.map(t => <button key={t.id} aria-pressed={selected.id === t.id} onClick={() => {onTopic(t.id); if (window.matchMedia?.("(max-width: 760px)").matches) document.getElementById("toeic-topic-detail")?.scrollIntoView({behavior:"smooth",block:"start"});}}><small>PART {t.part} · {t.question_count} CÂU TRỌNG TÂM</small><strong>{t.title}</strong></button>)}</aside>
        <article className="toeic-topic-detail" id="toeic-topic-detail" key={selected.id}><header><span className="toeic-eyebrow">PART {selected.part} · {partNames[selected.part]}</span><h3>{selected.title}</h3><p>{selected.recognition}</p></header>
          <section><h4>Hiểu bản chất</h4>{selected.rules.map(r => <p key={r}>{r}</p>)}</section>
          <section><h4>Cách xử lý từng bước</h4><ol>{selected.steps.map(s => <li key={s}>{s}</li>)}</ol></section>
          <section className="toeic-topic-example"><h4>Ví dụ có phân tích</h4><p lang="en">{selected.example.text}</p><p>{selected.example.explanation}</p></section>
          <section><h4>Bẫy cần tránh</h4><ul>{selected.traps.map(t => <li key={t}>{t}</li>)}</ul></section>
          <div className="toeic-note"><strong>{selected.question_count} câu thuộc dạng này trong ngân hàng</strong><p>Mỗi lượt lấy tối đa 15 câu và giữ trọn hội thoại hoặc văn bản có liên quan, nên có thể kèm câu của dạng khác. Đáp án mở sau khi nộp; các lượt có thể lặp lại câu đã học.</p><button className="toeic-button" disabled={busy || preview || selected.question_count === 0} onClick={() => {onTopic(selected.id); onStart("topic", undefined, {topic_id:selected.id});}}>Luyện dạng này<ArrowRight size={16}/></button>{preview && <p>Đăng nhập để làm bài và lưu kết quả.</p>}</div>
          <details className="toeic-topic-sources"><summary>Nguồn đối chiếu kiến thức</summary>{catalog.sources.filter(s => selected.source_ids.includes(s.id)).map(s => <a key={s.id} href={s.url} target="_blank" rel="noopener noreferrer">{s.title}</a>)}</details>
        </article></div> : <div className="toeic-panel"><h3>{topics.length ? "Chưa tìm thấy dạng bài phù hợp" : "Chuyên đề đang được cập nhật"}</h3><p>{topics.length ? "Thử từ khóa khác hoặc chọn tất cả Part." : "Bạn vẫn có thể luyện từng Part trong khi học liệu mới được triển khai."}</p><button className="toeic-button secondary" onClick={() => {setSearch(""); setPart(0); if (!topics.length) onMode("parts");}}>{topics.length ? "Xóa bộ lọc" : "Mở luyện từng Part"}</button></div>}
    </>}
    {mode === "exams" && <>
      <div className="toeic-study-filters"><label>Loại đề<select value={examType} onChange={e => setExamType(e.target.value as typeof examType)}><option value="all">Tất cả loại đề</option><option value="full">Toàn phần · 200 câu</option><option value="mini">Mini test · 50 câu</option><option value="listening">Listening · 100 câu</option><option value="reading">Reading · 100 câu</option></select></label><p>Chọn mã đề để biết rõ nội dung của mỗi lần làm. Lượt đang làm có thể tiếp tục trong Tiến độ.</p></div>
      <div className="toeic-exam-cards">{exams.map(e => <article key={e.id}><span className="toeic-eyebrow">{e.type === "full" ? "TOÀN PHẦN" : e.type === "mini" ? "MINI TEST" : e.type.toUpperCase()}</span><h3>{e.title}</h3><div className="toeic-exam-facts"><strong>{e.question_count} câu</strong><span>{e.minutes} phút</span></div><p>{e.description}</p><details><summary>Cấu trúc và cách làm</summary><ul>{e.parts.map(p => <li key={p.part}>Part {p.part}: {p.count} câu</li>)}</ul><p>{e.notice}</p><small>Mã đề: {e.id}</small></details><button className="toeic-button" disabled={busy || preview} onClick={() => onStart("exam", undefined, {exam_id:e.id})}>Làm {e.type === "full" ? "đề toàn phần" : e.type === "mini" ? "mini test" : "bài thi"}<ArrowRight size={16}/></button></article>)}</div>
      {!exams.length && <p>Chưa có mã đề thuộc bộ lọc này.</p>}
      <div className="toeic-note"><strong>Đề luyện có hỗ trợ</strong><p>Đồng hồ bắt đầu ngay khi mở bài và vẫn chạy khi rời trang. Chấm theo đáp án đã lưu đúng hạn. Audio tổng hợp được điều khiển thủ công và nghe lại; chưa khóa riêng hai giai đoạn nghe/đọc như thi thật. Hai đề toàn phần không trùng ID câu hỏi; mini test và bài riêng kỹ năng có dùng lại câu trong ngân hàng.</p><button className="toeic-button secondary" disabled={busy || preview} onClick={() => onStart("mock")}>Ghép một đề ngẫu nhiên · 200 câu</button></div>
    </>}
    {mode === "review" && <MistakeReview preview={preview} busy={busy} onStart={part => onStart("review", part)}/>}
    {mode === "parts" && <><div className="toeic-note"><strong>Khảo sát điểm xuất phát</strong><p>25 câu từ cả 7 phần giúp chọn chặng học. Đây là khảo sát nội bộ, không quy đổi điểm TOEIC.</p><button className="toeic-button secondary" disabled={busy || preview} onClick={() => onStart("diagnostic")}><BookOpen size={16}/>Khảo sát · 25 phút</button></div><div className="toeic-parts">{partNames.slice(1).map((name,i) => <article key={name}><span className="toeic-eyebrow">PART {i+1}</span><h3>{name}</h3><p>{[6,10,9,9,10,8,10][i]} câu · giữ nguyên nhóm nội dung</p><button className="toeic-button secondary" disabled={busy || preview} onClick={() => onStart("part", i+1)}><Headphones size={16}/>Luyện phần này</button></article>)}</div></>}
    <p className="toeic-study-attribution">Nội dung DHV và câu MIT từ <a href="https://github.com/kdeppaei/toeic-question-ocean" target="_blank" rel="noopener noreferrer">TOEIC Question Ocean</a> được chọn lọc, bổ sung lời giải tiếng Việt. <a href="/toeic/licenses/OCEAN-MIT-LICENSE.txt" target="_blank" rel="noopener noreferrer">Giấy phép MIT</a> · <a href="/toeic/licenses/OCEAN-ATTRIBUTION.md" target="_blank" rel="noopener noreferrer">Nguồn hình</a>.</p>
  </section>;
}

function MistakeReview({preview,busy,onStart}:{preview:boolean;busy:boolean;onStart:(part?:number)=>void}) {
  const [data,setData] = useState<ReviewBook>();
  const [error,setError] = useState("");
  const [part,setPart] = useState(0);
  const [reload,setReload] = useState(0);
  useEffect(() => {let alive=true; setError("");setData(undefined); if (!preview) toeicApi.reviewBook().then(d => {if(alive)setData(d);}).catch(e => {if(alive)setError(e.message);}); return () => {alive=false;};},[preview,reload]);
  if (preview) return <div className="toeic-panel"><h3>Sổ câu sai theo tài khoản</h3><p>Đăng nhập và nộp một bài để tạo danh sách câu cần ôn. Bản xem thử không có lịch sử cá nhân.</p></div>;
  if(error) return <div className="toeic-alert" role="alert">{error}<button onClick={()=>setReload(n=>n+1)}>Tải lại sổ câu sai</button></div>;
  if(!data) return <p role="status">Đang đọc các lượt làm bài gần đây…</p>;
  const items=data.items.filter(q=>!part || q.part===part);
  return <><div className="toeic-panel"><h3>{data.count} câu cần ôn lại</h3><p>Từ {data.window} lượt đã nộp gần nhất; câu chưa trả lời cũng được tính. Nếu đã trả lời đúng trong lượt mới hơn, câu đó rời danh sách. Lượt chưa nộp không thay đổi sổ câu sai.</p><div className="toeic-study-filters"><label>Lọc câu sai theo Part<select value={part} onChange={e=>setPart(Number(e.target.value))}><option value={0}>Tất cả Part</option>{data.parts.map(p=><option key={p.part} value={p.part}>Part {p.part} · {p.count} câu</option>)}</select></label><button className="toeic-button" disabled={busy || !items.length} onClick={()=>onStart(part || undefined)}>Ôn lại · tối đa 30 câu<ArrowRight size={16}/></button><button className="toeic-button secondary" onClick={()=>setReload(n=>n+1)}><RefreshCw size={16}/>Cập nhật</button></div><p>Những câu cùng đoạn có thể đi kèm để giữ nguyên ngữ cảnh. Các câu này vẫn được chấm và cập nhật theo kết quả mới.</p></div>
    {items.length ? <div className="toeic-mistake-list" aria-label="Các câu cần ôn">{items.slice(0,30).map(q=><div key={q.id}><span className="toeic-pill">Part {q.part}</span><p lang="en">{q.prompt}</p><small>{q.id}</small></div>)}{items.length>30 && <p>Còn {items.length-30} câu khác trong bộ lọc; mỗi lượt ôn lấy tối đa 30 câu kèm ngữ cảnh.</p>}</div> : <div className="toeic-note"><strong>Chưa có câu cần ôn trong bộ lọc này.</strong><p>Bạn có thể mở đề mới hoặc luyện một dạng bài khác.</p></div>}
  </>;
}
