import { useEffect, useRef, useState } from "react";
import { ArrowLeft, ArrowRight, BookOpen, Download, Layers3, RotateCcw, Volume2 } from "lucide-react";
import { dateTime, posNames, toeicApi, type LexiconCard, type LexiconFilters, type LexiconPage } from "./api";
import "./lexicon.css";

const pageSize = 30;
const alphabet = ["all", ..."abcdefghijklmnopqrstuvwxyz".split("")];

export function OpenLexicon({preview, onReviewed}: {preview: boolean; onReviewed: () => void}) {
  const [viewMode, setViewMode] = useState<"flashcard" | "book">("flashcard");
  const [deck, setDeck] = useState<LexiconFilters["deck"]>("all");
  const [pos, setPos] = useState<NonNullable<LexiconFilters["pos"]>>("all");
  const [letter, setLetter] = useState<string>("all");
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
    const filters: LexiconFilters = {
      deck,
      state,
      q: query,
      ...(pos !== "all" ? {pos} : {}),
      ...(letter !== "all" ? {letter} : {}),
      offset,
      limit: pageSize,
    };
    toeicApi.lexicon(filters, controller.signal)
      .then(result => {
        if (!active) return;
        if (offset > 0 && result.items.length === 0) setOffset(Math.max(0, Math.floor((result.total - 1) / pageSize) * pageSize));
        else setData(result);
      })
      .catch(e => {if (active && !controller.signal.aborted) setError((e as Error).message);})
      .finally(() => {if (active) setLoading(false);});
    return () => {active = false; controller.abort();};
  }, [deck, pos, letter, state, query, offset, reload]);
  useEffect(() => () => {if ("speechSynthesis" in window) speechSynthesis.cancel();}, []);

  const pendingSearch = search !== query;
  const items = data?.items || [];
  const card = items.find(c => c.id === selected) || items.find(c => !c.due || new Date(c.due).getTime() <= Date.now()) || items[0];
  const canReview = card && (!card.due || new Date(card.due).getTime() <= Date.now());
  const hasActiveFilter = deck !== "all" || pos !== "all" || letter !== "all" || state !== "all" || search.trim() !== "";

  function resetFilters() {
    setDeck("all"); setPos("all"); setLetter("all"); setState("all"); setSearch(""); setQuery(""); setOffset(0);
  }

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

  function speakTerm(term?: string) {
    const target = term || card?.term;
    if (!target) return;
    if (!("speechSynthesis" in window)) {setNotice("Thiết bị chưa hỗ trợ đọc từ. Bạn vẫn có thể xem phiên âm IPA, nghĩa song ngữ và ôn thẻ."); return;}
    speechSynthesis.cancel();
    const voice = new SpeechSynthesisUtterance(target);
    voice.lang = "en-US"; voice.rate = .85;
    voice.onerror = () => setNotice("Không phát được giọng đọc trên thiết bị này.");
    speechSynthesis.speak(voice);
  }

  function renderPosBadges(item: LexiconCard) {
    const tags = item.pos?.length ? item.pos : [];
    if (!tags.length) return null;
    return <span className="toeic-pos-list">{tags.map(tag => <span key={tag} className="toeic-pos-badge">{posNames[tag] || tag}</span>)}</span>;
  }

  function renderStatusBadge(item: LexiconCard) {
    const label = !item.due ? "Mới" : new Date(item.due).getTime() <= Date.now() ? "Đến hạn" : "Đã lên lịch";
    const tone = !item.due ? "new" : new Date(item.due).getTime() <= Date.now() ? "due" : "scheduled";
    return <small className={`toeic-status-pill ${tone}`}>{label}</small>;
  }

  return <section className="toeic-lexicon" aria-label="Sổ tra từ và từ điển song ngữ Anh Việt NGSL và TOEIC Service List">
    <div className="toeic-section-heading">
      <div>
        <span className="toeic-eyebrow">SỔ TRA TỪ & TỪ ĐIỂN SONG NGỮ ANH–VIỆT · NGSL + TOEIC SERVICE LIST</span>
        <h2>Từ nền tảng đến ngôn ngữ công việc.</h2>
        <p>Tra cứu song ngữ Anh–Việt (có hoặc không dấu), xem phiên âm IPA chuẩn Mỹ, lọc theo từ loại hoặc bảng chữ cái A–Z và ôn thẻ nhớ chủ động FSRS.</p>
      </div>
      <div className="toeic-roadmap-mode toeic-lexicon-mode" role="group" aria-label="Chế độ xem sổ từ">
        <button type="button" aria-pressed={viewMode === "flashcard"} onClick={() => setViewMode("flashcard")}><Layers3 size={16}/>Thẻ lật FSRS</button>
        <button type="button" aria-pressed={viewMode === "book"} onClick={() => setViewMode("book")}><BookOpen size={16}/>Sổ tra từ song ngữ</button>
      </div>
    </div>

    <div className="toeic-vocab-filters toeic-lexicon-filters">
      <label>Bộ từ<select value={deck} disabled={busy} onChange={e => {setDeck(e.target.value as LexiconFilters["deck"]); setOffset(0);}}><option value="all">NGSL + TOEIC Service List (4.060 từ)</option><option value="ngsl">NGSL · 2.809 từ nền tảng</option><option value="tsl">TSL · 1.250 từ công sở + 2 mục bổ sung</option></select></label>
      <label>Từ loại<select value={pos} disabled={busy} onChange={e => {setPos(e.target.value as NonNullable<LexiconFilters["pos"]>); setOffset(0);}}><option value="all">Tất cả từ loại</option><option value="n">Danh từ (Noun)</option><option value="v">Động từ (Verb)</option><option value="adj">Tính từ (Adjective)</option><option value="adv">Trạng từ (Adverb)</option><option value="func">Từ chức năng (Prep / Conj / Pron)</option></select></label>
      <label>Tìm từ (Anh – Việt) hoặc định nghĩa<input aria-label="Tìm từ hoặc định nghĩa tiếng Anh" value={search} maxLength={120} disabled={busy} onChange={e => setSearch(e.target.value)} placeholder="invoice, hóa đơn, cuộc hẹn, café…" type="search"/></label>
      <label>Trạng thái thẻ<select value={state} disabled={busy} onChange={e => {setState(e.target.value as LexiconFilters["state"]); setOffset(0);}}><option value="all">Tất cả</option><option value="due">Đến hạn ôn</option><option value="new">Chưa học</option><option value="learned">Đã bắt đầu học</option></select></label>
    </div>

    <nav className="toeic-alphabet-bar" aria-label="Tra nhanh theo chữ cái A–Z">
      {alphabet.map(ch => (
        <button key={ch} type="button" disabled={busy} className={letter === ch ? "active" : ""} aria-pressed={letter === ch} onClick={() => {setLetter(ch); setOffset(0);}}>
          {ch === "all" ? "Tất cả A–Z" : ch.toUpperCase()}
        </button>
      ))}
      {hasActiveFilter && <button type="button" className="toeic-reset-filter" disabled={busy} onClick={resetFilters}><RotateCcw size={14}/>Xóa bộ lọc</button>}
    </nav>

    {error && <div className="toeic-alert" role="alert">{error}<button disabled={busy} onClick={() => setReload(n => n + 1)}>Tải lại kho từ</button></div>}
    {notice && <p role="status" className="toeic-muted">{notice}</p>}
    {loading || pendingSearch ? <p role="status">Đang tìm trong sổ từ song ngữ…</p> : data && <>
      <p className="toeic-muted" role="status">{data.total.toLocaleString("vi-VN")} mục từ khớp bộ lọc · {data.due_count} thẻ đến hạn · {data.new_count} thẻ mới</p>

      {viewMode === "flashcard" ? (
        <div className="toeic-vocab-layout">
          <section className="toeic-flashcard" aria-label="Thẻ từ đang chọn">
            {card ? <>
              <span className="toeic-eyebrow">{card.lists.map(s => `${s.id.toUpperCase()}${s.rank ? ` #${s.rank}` : " · bổ sung, chưa xếp hạng"}`).join(" / ")}</span>
              <h3 lang="en">{card.term}</h3>
              <div className="toeic-phonetic-row">
                {card.ipa && <span className="toeic-ipa" aria-label="Phiên âm IPA">{card.ipa}</span>}
                {renderPosBadges(card)}
                <button className="toeic-button secondary" onClick={() => speakTerm(card.term)}><Volume2 size={17}/>Nghe từ</button>
              </div>
              {revealed === card.id ? <div className="toeic-card-answer">
                {(card.meaning_vi || card.meaning) && <div className="toeic-bilingual-vi">
                  <h4>Nghĩa tiếng Việt</h4>
                  <p className="toeic-meaning-vi">{card.meaning_vi || card.meaning}</p>
                </div>}
                {card.example && <div className="toeic-bilingual-example">
                  <h4>Ví dụ ngữ cảnh</h4>
                  <p lang="en">“{card.example}”</p>
                </div>}
                <h4>Định nghĩa tiếng Anh</h4>
                {card.definitions.map(d => <div key={d.source_id} className="toeic-en-def"><p lang="en">{d.text}</p><small>{d.source_id.toUpperCase()}{d.adapted_by_dhv ? " · định nghĩa do DHV bổ sung" : " · định nghĩa từ tác giả"}</small></div>)}
                {canReview ? <><p>Bạn nhớ ở mức nào?</p><div className="toeic-ratings">{["Học lại", "Khó", "Nhớ được", "Dễ"].map((label, i) => <button key={label} disabled={busy || preview} onClick={() => void review(i + 1)}>{label}</button>)}</div>{preview && <p>Đăng nhập để lưu lịch ôn theo tài khoản.</p>}</> : <p>Lần ôn tiếp: {card.due && dateTime(card.due)}. Bạn vẫn có thể đọc lại nghĩa song ngữ và định nghĩa.</p>}
              </div> : <button className="toeic-button" onClick={() => setRevealed(card.id)}>Hiện định nghĩa tiếng Anh & nghĩa tiếng Việt</button>}
            </> : <><h3>{state === "due" ? "Chưa có thẻ đến hạn trong bộ lọc." : "Không có từ khớp bộ lọc."}</h3><p>Đổi danh sách, chữ cái, từ loại hoặc từ khóa để tiếp tục học.</p></>}
          </section>
          <aside className="toeic-word-list">
            <h3>Mục lục trang này · {items.length} từ</h3>
            <p>Thứ hạng phản ánh tần suất xuất hiện trong tiếng Anh tổng quát (NGSL) và công sở (TSL).</p>
            <div>
              {items.map(word => (
                <button key={word.id} disabled={busy} className={card?.id === word.id ? "active" : ""} aria-pressed={card?.id === word.id} onClick={() => {setSelected(word.id); setRevealed(undefined);}}>
                  <div className="toeic-word-item-main">
                    <strong lang="en">{word.term}</strong>
                    {word.ipa && <span className="toeic-word-ipa">{word.ipa}</span>}
                  </div>
                  <div className="toeic-word-item-meta">
                    {word.pos?.length ? <span className="toeic-word-pos">{word.pos.map(p => posNames[p] || p).join(", ")}</span> : null}
                    {renderStatusBadge(word)}
                  </div>
                </button>
              ))}
            </div>
            <nav className="toeic-lexicon-pagination" aria-label="Phân trang kho từ"><button className="toeic-button secondary" disabled={busy || offset === 0} onClick={() => setOffset(n => Math.max(0, n - pageSize))}><ArrowLeft size={16}/>Trước</button><span>{data.total ? `${offset + 1}–${Math.min(offset + pageSize, data.total)} / ${data.total.toLocaleString("vi-VN")}` : "0 kết quả"}</span><button className="toeic-button secondary" disabled={busy || offset + pageSize >= data.total} onClick={() => setOffset(n => n + pageSize)}>Sau<ArrowRight size={16}/></button></nav>
          </aside>
        </div>
      ) : (
        <div className="toeic-dict-book" aria-label="Trang sổ tra từ song ngữ Anh Việt">
          {items.length ? <>
            <div className="toeic-dict-grid">
              {items.map(word => (
                <article key={word.id} className="toeic-dict-entry">
                  <header className="toeic-dict-entry-header">
                    <div>
                      <span className="toeic-eyebrow">{word.lists.map(s => `${s.id.toUpperCase()}${s.rank ? ` #${s.rank}` : " · bổ sung"}`).join(" / ")}</span>
                      <div className="toeic-dict-title-row">
                        <h3 lang="en">{word.term}</h3>
                        {word.ipa && <span className="toeic-ipa">{word.ipa}</span>}
                      </div>
                      {renderPosBadges(word)}
                    </div>
                    <div className="toeic-dict-entry-actions">
                      {renderStatusBadge(word)}
                      <button type="button" className="toeic-button secondary toeic-icon-btn" aria-label={`Nghe phát âm ${word.term}`} onClick={() => speakTerm(word.term)}><Volume2 size={16}/></button>
                    </div>
                  </header>
                  <div className="toeic-dict-body">
                    <div className="toeic-dict-vi">
                      <strong>Nghĩa tiếng Việt:</strong> <span>{word.meaning_vi || word.meaning}</span>
                    </div>
                    <div className="toeic-dict-en">
                      {word.definitions.map(d => (
                        <p key={d.source_id} lang="en"><small>{d.source_id.toUpperCase()}:</small> {d.text}</p>
                      ))}
                    </div>
                    {word.example && <p className="toeic-dict-example" lang="en">Ví dụ: “{word.example}”</p>}
                  </div>
                  <footer className="toeic-dict-footer">
                    <button type="button" className="toeic-button secondary" onClick={() => {setSelected(word.id); setRevealed(word.id); setViewMode("flashcard");}}>
                      <Layers3 size={15}/>Ôn thẻ FSRS
                    </button>
                  </footer>
                </article>
              ))}
            </div>
            <nav className="toeic-lexicon-pagination" aria-label="Phân trang kho từ"><button className="toeic-button secondary" disabled={busy || offset === 0} onClick={() => setOffset(n => Math.max(0, n - pageSize))}><ArrowLeft size={16}/>Trước</button><span>{data.total ? `${offset + 1}–${Math.min(offset + pageSize, data.total)} / ${data.total.toLocaleString("vi-VN")}` : "0 kết quả"}</span><button className="toeic-button secondary" disabled={busy || offset + pageSize >= data.total} onClick={() => setOffset(n => n + pageSize)}>Sau<ArrowRight size={16}/></button></nav>
          </> : <div className="toeic-panel"><h3>Không có mục từ nào khớp bộ lọc.</h3><p>Hãy thử đổi chữ cái, từ loại hoặc từ khóa tìm kiếm.</p></div>}
        </div>
      )}
    </>}
    <div className="toeic-note toeic-lexicon-credit">
      <strong>4.060 mục từ song ngữ Anh–Việt kèm IPA & từ loại, giữ đầy đủ ghi nguồn mở.</strong>
      <p>Danh sách từ, thứ hạng và định nghĩa tiếng Anh từ <strong>NGSL 1.2</strong> (Charles Browne, Brent Culligan, Joseph Phillips) và <strong>TOEIC Service List 1.2</strong> (Charles Browne, Brent Culligan). Nghĩa tiếng Việt và từ loại từ <strong>Vietnamese Wiktionary / Kaikki.org</strong> & biên tập ngữ cảnh <strong>DHV English Studio</strong> (CC BY-SA 4.0); phiên âm tiếng Anh Mỹ từ <strong>open-dict-data/ipa-dict</strong> (MIT).</p>
      <p>Dữ liệu và bản điều chỉnh được chia sẻ theo <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener noreferrer">CC BY-SA 4.0</a> (<a href="/toeic/licenses/NGSL-TSL.md" target="_blank" rel="noopener noreferrer">Xem nguồn, giấy phép và thay đổi</a> · <a href="/toeic/licenses/IPA-MIT-LICENSE.txt" target="_blank" rel="noopener noreferrer">Giấy phép MIT cho IPA</a>).</p>
      <div className="toeic-lexicon-downloads">
        <a className="toeic-button secondary" href={data?.handbook_url || "/toeic/so-tay-tu-vung-song-ngu.md"} download><Download size={16}/>Tải sổ tay từ vựng song ngữ (.md)</a>
        <a className="toeic-button secondary" href="/toeic/lexicon.json" download><Download size={16}/>Tải dữ liệu từ vựng JSON</a>
      </div>
    </div>
  </section>;
}
