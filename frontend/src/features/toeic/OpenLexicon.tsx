import { useEffect, useRef, useState } from "react";
import { ArrowLeft, ArrowRight, Download, Volume2 } from "lucide-react";
import { dateTime, toeicApi, type LexiconFilters, type LexiconPage } from "./api";
import "./lexicon.css";

const pageSize = 30;
export function OpenLexicon({preview, onReviewed}: {preview: boolean; onReviewed: () => void}) {
  const [deck, setDeck] = useState<LexiconFilters["deck"]>("all");
  const [state, setState] = useState<LexiconFilters["state"]>("all");
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [offset, setOffset] = useState(0);
  const [reload, setReload] = useState(0);
  const [data, setData] = useState<LexiconPage>();
  const [selected, setSelected] = useState<string>();
  const [revealed, setRevealed] = useState<string>();
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const lock = useRef(false);
  const event = useRef<{card: string; rating: number; id: string} | null>(null);

  useEffect(() => {
    const timer = window.setTimeout(() => {setQuery(search); setOffset(0);}, 250);
    return () => window.clearTimeout(timer);
  }, [search]);
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setLoading(true); setError(""); setData(undefined); setSelected(undefined); setRevealed(undefined);
    toeicApi.lexicon({deck, state, q:query, offset, limit:pageSize}, controller.signal)
      .then(result => {
        if (!active) return;
        if (offset > 0 && result.items.length === 0) setOffset(Math.max(0, Math.floor((result.total - 1) / pageSize) * pageSize));
        else setData(result);
      })
      .catch(e => {if (active && !controller.signal.aborted) setError((e as Error).message);})
      .finally(() => {if (active) setLoading(false);});
    return () => {active = false; controller.abort();};
  }, [deck, state, query, offset, reload]);
  useEffect(() => () => {if ("speechSynthesis" in window) speechSynthesis.cancel();}, []);

  const pendingSearch = search !== query;
  const items = data?.items || [];
  const card = items.find(c => c.id === selected) || items.find(c => !c.due || new Date(c.due).getTime() <= Date.now()) || items[0];
  const canReview = card && (!card.due || new Date(card.due).getTime() <= Date.now());

  async function review(rating: number) {
    if (!card || !canReview || preview || lock.current || pendingSearch) return;
    lock.current = true; setBusy(true); setError("");
    if (event.current?.card !== card.id || event.current.rating !== rating) event.current = {card:card.id, rating, id:crypto.randomUUID()};
    try {
      const result = await toeicApi.review(card.id, rating, card.version, event.current.id);
      setNotice(`Đã ôn “${card.term}”. Lần tới: ${dateTime(result.due)}.`);
      setRevealed(undefined); event.current = null; setReload(n => n + 1); onReviewed();
    } catch (e) {setError((e as Error).message);}
    finally {lock.current = false; setBusy(false);}
  }
  function speak() {
    if (!card) return;
    if (!("speechSynthesis" in window)) {setNotice("Thiết bị chưa hỗ trợ đọc từ. Bạn vẫn có thể xem định nghĩa và ôn thẻ."); return;}
    speechSynthesis.cancel();
    const voice = new SpeechSynthesisUtterance(card.term);
    voice.lang = "en-US"; voice.rate = .85;
    voice.onerror = () => setNotice("Không phát được giọng đọc trên thiết bị này.");
    speechSynthesis.speak(voice);
  }

  return <section className="toeic-lexicon" aria-label="Kho từ mở NGSL và TOEIC Service List">
    <div className="toeic-section-heading"><div><span className="toeic-eyebrow">NGSL + TOEIC SERVICE LIST</span><h2>Từ nền tảng đến ngôn ngữ công việc.</h2><p>Tra từ, tự nhớ định nghĩa rồi ôn theo lịch cá nhân. Định nghĩa ở bộ này bằng tiếng Anh; bộ thẻ DHV bên cạnh có nghĩa tiếng Việt và ví dụ.</p></div></div>
    <div className="toeic-vocab-filters toeic-lexicon-filters">
      <label>Bộ từ<select value={deck} disabled={busy} onChange={e => {setDeck(e.target.value as LexiconFilters["deck"]); setOffset(0);}}><option value="all">NGSL + TOEIC Service List</option><option value="ngsl">NGSL · 2.809 từ nền tảng</option><option value="tsl">TSL · 1.250 từ xếp hạng + 2 mục bổ sung</option></select></label>
      <label>Tìm từ hoặc định nghĩa tiếng Anh<input value={search} maxLength={120} disabled={busy} onChange={e => setSearch(e.target.value)} placeholder="meeting, café, customer…" type="search"/></label>
      <label>Trạng thái thẻ<select value={state} disabled={busy} onChange={e => {setState(e.target.value as LexiconFilters["state"]); setOffset(0);}}><option value="all">Tất cả</option><option value="due">Đến hạn ôn</option><option value="new">Chưa học</option><option value="learned">Đã bắt đầu học</option></select></label>
    </div>
    {error && <div className="toeic-alert" role="alert">{error}<button disabled={busy} onClick={() => setReload(n => n + 1)}>Tải lại kho từ</button></div>}
    {notice && <p role="status" className="toeic-muted">{notice}</p>}
    {loading || pendingSearch ? <p role="status">Đang tìm trong kho từ…</p> : data && <>
      <p className="toeic-muted" role="status">{data.total.toLocaleString("vi-VN")} kết quả · {data.due_count} thẻ đến hạn · {data.new_count} thẻ mới trong bộ lọc từ và danh sách</p>
      <div className="toeic-vocab-layout">
        <section className="toeic-flashcard" aria-label="Thẻ từ đang chọn">
          {card ? <>
            <span className="toeic-eyebrow">{card.lists.map(s => `${s.id.toUpperCase()}${s.rank ? ` #${s.rank}` : " · bổ sung, chưa xếp hạng"}`).join(" / ")}</span>
            <h3 lang="en">{card.term}</h3><button className="toeic-button secondary" onClick={speak}><Volume2 size={17}/>Nghe từ</button>
            {revealed === card.id ? <div className="toeic-card-answer"><h4>Định nghĩa tiếng Anh</h4>{card.definitions.map(d => <div key={d.source_id}><p lang="en">{d.text}</p><small>{d.source_id.toUpperCase()}{d.adapted_by_dhv ? " · định nghĩa do DHV bổ sung" : " · định nghĩa từ tác giả"}</small></div>)}
              {canReview ? <><p>Bạn nhớ ở mức nào?</p><div className="toeic-ratings">{["Học lại", "Khó", "Nhớ được", "Dễ"].map((label, i) => <button key={label} disabled={busy || preview} onClick={() => void review(i + 1)}>{label}</button>)}</div>{preview && <p>Đăng nhập để lưu lịch ôn theo tài khoản.</p>}</> : <p>Lần ôn tiếp: {card.due && dateTime(card.due)}. Bạn vẫn có thể đọc lại định nghĩa.</p>}
            </div> : <button className="toeic-button" onClick={() => setRevealed(card.id)}>Hiện định nghĩa tiếng Anh</button>}
          </> : <><h3>{state === "due" ? "Chưa có thẻ đến hạn trong bộ lọc." : "Không có từ khớp bộ lọc."}</h3><p>Đổi danh sách, trạng thái hoặc từ khóa để tiếp tục học.</p></>}
        </section>
        <aside className="toeic-word-list"><h3>Chọn từ để học</h3><p>Thứ hạng trong từng danh sách phản ánh tần suất, không phải điểm TOEIC.</p><div>{items.map(word => <button key={word.id} disabled={busy} className={card?.id === word.id ? "active" : ""} aria-pressed={card?.id === word.id} onClick={() => {setSelected(word.id); setRevealed(undefined);}}><strong lang="en">{word.term}</strong><small>{!word.due ? "Mới" : new Date(word.due).getTime() <= Date.now() ? "Đến hạn" : "Đã lên lịch"}</small></button>)}</div>
          <nav className="toeic-lexicon-pagination" aria-label="Phân trang kho từ"><button className="toeic-button secondary" disabled={busy || offset === 0} onClick={() => setOffset(n => Math.max(0, n - pageSize))}><ArrowLeft size={16}/>Trước</button><span>{data.total ? `${offset + 1}–${Math.min(offset + pageSize, data.total)} / ${data.total.toLocaleString("vi-VN")}` : "0 kết quả"}</span><button className="toeic-button secondary" disabled={busy || offset + pageSize >= data.total} onClick={() => setOffset(n => n + pageSize)}>Sau<ArrowRight size={16}/></button></nav>
        </aside>
      </div>
    </>}
    <div className="toeic-note toeic-lexicon-credit"><strong>4.060 từ riêng biệt, giữ đầy đủ ghi nguồn.</strong><p>NGSL: Charles Browne, Brent Culligan, Joseph Phillips. TSL: Charles Browne, Brent Culligan. Có 4.059 mục xếp hạng; “born” là từ bổ sung chưa xếp hạng, “criteria” có trong cả hai bảng định nghĩa. Sáu định nghĩa còn thiếu được DHV bổ sung và đánh dấu.</p><p>Dữ liệu và bản điều chỉnh được chia sẻ theo <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener noreferrer">CC BY-SA 4.0</a>. <a href="/toeic/licenses/NGSL-TSL.md" target="_blank" rel="noopener noreferrer">Xem nguồn, giấy phép và thay đổi</a>.</p><a className="toeic-button secondary" href="/toeic/lexicon.json" download><Download size={16}/>Tải dữ liệu từ vựng JSON</a></div>
  </section>;
}
