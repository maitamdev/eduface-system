import { useEffect, useRef, useState } from "react";
import { ArrowLeft, ArrowRight, BookOpen, Download, ExternalLink, Layers3, RotateCcw, Search, SlidersHorizontal, Volume2, X } from "lucide-react";
import { dateTime, posNames, toeicApi, type LexiconCard, type LexiconFilters, type LexiconPage } from "./api";
import "./lexicon.css";

const pageSize = 30;
const alphabet = ["all", ..."abcdefghijklmnopqrstuvwxyz"];
const sourceNames: Record<string, string> = {ngsl:"NGSL", tsl:"TOEIC Service List", thichhoc:"thichhoc", wiktionary:"Wiktionary", "wiktionary-vi":"Wiktionary tiếng Việt", dhv:"DHV"};
const format = (count: number) => count.toLocaleString("vi-VN");

function Pos({word}: {word: LexiconCard}) {
  return <span className="toeic-pos-list">{word.pos?.map(p => <span className="toeic-pos-badge" key={p}>{posNames[p] || p}</span>)}</span>;
}

function Meanings({word}: {word: LexiconCard}) {
  const senses = word.senses_vi || [];
  const extra = senses.filter(s => s.text.replace(/[.;]+$/, "").toLowerCase() !== (word.meaning_vi || word.meaning).replace(/[.;]+$/, "").toLowerCase());
  return <div className="dictionary-meanings">
    <div className="dictionary-main-meaning"><h4>Nghĩa tiếng Việt</h4><p lang="vi">{word.meaning_vi || word.meaning}</p></div>
    {extra.length > 0 && <details className="dictionary-senses" key={word.id}>
      <summary>Xem đầy đủ {senses.length} nghĩa theo từ loại</summary>
      <ol>{senses.map((sense, i) => <li key={`${sense.pos}-${i}`}><span className="dictionary-sense-pos">{posNames[sense.pos] || sense.pos}</span><span lang="vi">{sense.text}</span></li>)}</ol>
    </details>}
    {!!word.examples?.length && <section className="dictionary-examples"><h4>Ví dụ song ngữ</h4>{word.examples.slice(0, 3).map((ex, i) => <div key={i}><p lang="en">{ex.en}</p><p lang="vi">{ex.vi}</p></div>)}
      {word.examples.length > 3 && <details key={`${word.id}-examples`}><summary>Thêm {word.examples.length - 3} ví dụ</summary>{word.examples.slice(3).map((ex, i) => <div key={i}><p lang="en">{ex.en}</p><p lang="vi">{ex.vi}</p></div>)}</details>}
    </section>}
    {!word.examples?.length && word.example && <section className="dictionary-examples"><h4>Ví dụ</h4><p lang="en">{word.example}</p></section>}
    {!!word.inflections?.length && <details key={`${word.id}-forms`}><summary>Biến thể từ · {word.inflections.length}</summary><p className="dictionary-forms" lang="en">{word.inflections.join(" · ")}</p></details>}
    {!!word.definitions.length && <details key={`${word.id}-english`}><summary>Định nghĩa tiếng Anh</summary>{word.definitions.map((d,i) => <div className="dictionary-english" key={`${d.source_id}-${i}`}><p lang="en">{d.text}</p><small>{sourceNames[d.source_id] || d.source_id}{d.adapted_by_dhv ? " · DHV bổ sung" : ""}</small></div>)}</details>}
    <p className="dictionary-provenance">
      {word.translation_status === "machine" ? "Nghĩa tham khảo từ bản dịch máy thichhoc; nguồn chưa được con người duyệt." : word.translation_status === "edited" ? "Nghĩa thường dùng được biên soạn/bổ sung bởi DHV." : "Nghĩa và ví dụ từ cộng đồng Wiktionary tiếng Việt."}
      {word.source_url && <> <a href={word.source_url} target="_blank" rel="noopener noreferrer">Xem nguồn<ExternalLink size={12}/></a></>}
    </p>
  </div>;
}

export function OpenLexicon({preview, onReviewed, initialQuery = ""}: {preview: boolean; onReviewed: () => void; initialQuery?: string}) {
  const [mode, setMode] = useState<"dictionary" | "flashcard">("dictionary");
  const [direction, setDirection] = useState<"en-vi" | "vi-en">("en-vi");
  const [deck, setDeck] = useState<LexiconFilters["deck"]>("all");
  const [pos, setPos] = useState<NonNullable<LexiconFilters["pos"]>>("all");
  const [letter, setLetter] = useState("all");
  const [state, setState] = useState<LexiconFilters["state"]>("all");
  const [scope, setScope] = useState<"lookup" | "full">("lookup");
  const [search, setSearch] = useState(initialQuery);
  const [query, setQuery] = useState(initialQuery.trim());
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
  const input = useRef<HTMLInputElement>(null);
  const detail = useRef<HTMLElement>(null);

  useEffect(() => {
    const timer = window.setTimeout(() => {setQuery(search.trim()); setOffset(0);}, 250);
    return () => window.clearTimeout(timer);
  }, [search]);
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setLoading(true); setError(""); setData(undefined); setSelected(undefined); setRevealed(undefined);
    const timeout = window.setTimeout(() => {
      if (!active) return;
      active = false; controller.abort(); setLoading(false);
      setError("Tra cứu mất quá nhiều thời gian. Hãy kiểm tra kết nối và thử lại.");
    }, 45000);
    const filters: LexiconFilters = {deck, state, q:query, scope, ...(pos !== "all" ? {pos} : {}), ...(letter !== "all" ? {letter} : {}), offset, limit:pageSize};
    toeicApi.lexicon(filters, controller.signal)
      .then(result => {
        if (!active) return;
        if (offset > 0 && result.items.length === 0) setOffset(Math.max(0, Math.floor((result.total - 1) / pageSize) * pageSize));
        else setData(result);
      })
      .catch(e => {if (active && !controller.signal.aborted) setError((e as Error).message);})
      .finally(() => {window.clearTimeout(timeout); if (active) setLoading(false);});
    return () => {active = false; window.clearTimeout(timeout); controller.abort();};
  }, [deck, pos, letter, state, query, scope, offset, reload]);
  useEffect(() => () => {if ("speechSynthesis" in window) speechSynthesis.cancel();}, []);

  const pending = search.trim() !== query;
  const items = data?.items || [];
  // An exact lookup stays first, regardless of its review schedule.
  const card = items.find(c => c.id === selected) || items[0];
  const canReview = card && (!card.due || new Date(card.due).getTime() <= Date.now());
  const filtersActive = deck !== "all" || pos !== "all" || letter !== "all" || state !== "all" || scope !== "lookup";
  const answerOpen = !!card && revealed === `${card.id}:${direction}`;

  function searchFor(text: string) {
    setSearch(text); setQuery(text.trim()); setOffset(0); setLetter("all"); setNotice("");
  }
  function clearFilters() {
    setDeck("all"); setPos("all"); setLetter("all"); setState("all"); setScope("lookup"); setOffset(0);
  }
  function choose(id: string) {
    setSelected(id); setRevealed(undefined); setNotice("");
    // Make the result discoverable on a narrow screen and for keyboard users.
    detail.current?.focus({preventScroll:true});
    if (window.matchMedia?.("(max-width: 760px)").matches) detail.current?.scrollIntoView({block:"start"});
  }
  async function review(rating: number) {
    if (!card || !canReview || !answerOpen || preview || lock.current || pending) return;
    lock.current = true; setBusy(true); setError("");
    if (event.current?.card !== card.id || event.current.rating !== rating) event.current = {card:card.id, rating, id:crypto.randomUUID()};
    try {
      const result = await toeicApi.review(card.id, rating, card.version, event.current.id);
      setNotice(`Đã ôn “${card.term}”. Lần tới: ${dateTime(result.due)}.`);
      setRevealed(undefined); event.current = null; setReload(n => n + 1); onReviewed();
    } catch (e) {setError((e as Error).message);}
    finally {lock.current = false; setBusy(false);}
  }
  function speak(term: string) {
    if (!("speechSynthesis" in window)) {setNotice("Thiết bị chưa hỗ trợ giọng đọc. Bạn vẫn có thể tra nghĩa và phiên âm."); return;}
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(term);
    utterance.lang = "en-US"; utterance.rate = .85;
    const voice = speechSynthesis.getVoices().find(v => v.lang === "en-US") || speechSynthesis.getVoices().find(v => v.lang.startsWith("en"));
    if (voice) utterance.voice = voice;
    utterance.onerror = e => {if (!["interrupted", "canceled"].includes(e.error)) setNotice("Chưa phát được giọng đọc trên thiết bị này.");};
    speechSynthesis.speak(utterance);
  }
  function pagination() {
    if (!data) return null;
    return <nav className="toeic-lexicon-pagination" aria-label="Phân trang kho từ">
      <button className="toeic-button secondary" disabled={busy || offset === 0} onClick={() => setOffset(n => Math.max(0,n-pageSize))}><ArrowLeft size={16}/>Trước</button>
      <span>{data.total ? `${format(offset+1)}–${format(Math.min(offset+pageSize,data.total))} / ${format(data.total)}` : "0 kết quả"}</span>
      <button className="toeic-button secondary" disabled={busy || offset+pageSize >= data.total} onClick={() => setOffset(n => n+pageSize)}>Sau<ArrowRight size={16}/></button>
    </nav>;
  }

  return <section className="toeic-lexicon" aria-label="Từ điển Anh–Việt">
    <header className="dictionary-header">
      <div><span className="toeic-eyebrow">TỪ ĐIỂN ANH–VIỆT · DHV</span><h2>Tra từ, hiểu đúng ngữ cảnh.</h2><p>Nghĩa tiếng Việt, ví dụ song ngữ và các dạng của từ. Tìm bằng tiếng Anh hoặc tiếng Việt có dấu, không dấu.</p></div>
      <div className="dictionary-mode" role="group" aria-label="Chế độ từ vựng">
        <button aria-pressed={mode === "dictionary"} onClick={() => setMode("dictionary")}><BookOpen size={17}/>Tra từ</button>
        <button aria-pressed={mode === "flashcard"} onClick={() => {setMode("flashcard"); setRevealed(undefined);}}><Layers3 size={17}/>Ôn thẻ</button>
      </div>
    </header>

    <form role="search" className="dictionary-search" onSubmit={e => {e.preventDefault(); searchFor(search);}}>
      <Search size={22} aria-hidden="true"/>
      <input ref={input} aria-label="Tìm từ tiếng Anh hoặc nghĩa tiếng Việt" value={search} maxLength={120} disabled={busy} autoComplete="off" spellCheck={false} type="search" placeholder="Tìm từ: invoice, xin chào, hoa don, went…"
        onChange={e => {setSearch(e.target.value); setLetter("all"); setNotice("");}}
        onKeyDown={e => {if (e.key === "Escape") searchFor("");}}/>
      {search && <button type="button" className="dictionary-clear" aria-label="Xóa từ khóa" disabled={busy} onClick={() => {searchFor(""); input.current?.focus();}}><X size={18}/></button>}
      <button type="submit" className="toeic-button" disabled={busy}>Tra cứu</button>
    </form>
    {!search && <div className="dictionary-quick-queries"><span>Thử tra</span>{["accommodation", "xin chào", "hóa đơn", "went", "social media"].map(q => <button key={q} disabled={busy} onClick={() => searchFor(q)}>{q}</button>)}</div>}

    <details className="dictionary-filter-panel">
      <summary><SlidersHorizontal size={15}/>Bộ lọc & phạm vi tìm kiếm{filtersActive && <span>Đang áp dụng</span>}</summary>
      <div className="toeic-vocab-filters dictionary-filters">
        <label>Bộ từ<select value={deck} disabled={busy} onChange={e => {setDeck(e.target.value as LexiconFilters["deck"]); setOffset(0);}}><option value="all">Toàn bộ từ điển{data ? ` · ${format(data.word_count)} mục từ` : ""}</option><option value="core">Trọng tâm TOEIC · 4.060 từ</option><option value="ngsl">NGSL · 2.809 từ nền tảng</option><option value="tsl">TSL · 1.252 từ công sở</option><option value="wiktionary">Từ mới từ Wiktionary</option><option value="thichhoc">Kho mở rộng thichhoc</option><option value="dhv">Cụm từ DHV bổ sung</option></select></label>
        <label>Từ loại<select value={pos} disabled={busy} onChange={e => {setPos(e.target.value as typeof pos); setOffset(0);}}><option value="all">Tất cả từ loại</option><option value="n">Danh từ</option><option value="v">Động từ</option><option value="adj">Tính từ</option><option value="adv">Trạng từ</option><option value="func">Từ chức năng</option></select></label>
        <label>Trạng thái ôn<select value={state} disabled={busy} onChange={e => {setState(e.target.value as typeof state); setOffset(0);}}><option value="all">Tất cả trạng thái</option><option value="due">Đến hạn ôn</option><option value="new">Chưa học</option><option value="learned">Đã bắt đầu học</option></select></label>
        <label>Tìm trong<select value={scope} disabled={busy} onChange={e => {setScope(e.target.value as typeof scope); setOffset(0);}}><option value="lookup">Từ, biến thể & nghĩa tiếng Việt</option><option value="full">Thêm định nghĩa tiếng Anh</option></select></label>
      </div>
      <nav className="dictionary-alphabet" aria-label="Tra theo chữ cái">{alphabet.map(ch => <button key={ch} type="button" disabled={busy} aria-pressed={letter === ch} onClick={() => {setLetter(ch); setOffset(0);}}>{ch === "all" ? "Tất cả" : ch.toUpperCase()}</button>)}</nav>
    </details>
    {filtersActive && <p className="dictionary-active-filters">Đang giới hạn: {[deck !== "all" && (deck === "core" ? "TOEIC" : sourceNames[deck] || deck), pos !== "all" && (posNames[pos] || "từ chức năng"), letter !== "all" && `chữ ${letter.toUpperCase()}`, state !== "all" && ({due:"đến hạn ôn",new:"chưa học",learned:"đã học"}[state]), scope === "full" && "cả định nghĩa Anh"].filter(Boolean).join(" · ")}<button disabled={busy} onClick={clearFilters}><RotateCcw size={13}/>Bỏ bộ lọc, giữ từ khóa</button></p>}

    {error && <div className="toeic-alert" role="alert">{error}<button disabled={busy} onClick={() => setReload(n => n+1)}>Thử lại</button></div>}
    {notice && <p className="dictionary-notice" role="status">{notice}</p>}
    {loading || pending ? <div className="dictionary-loading" role="status"><Search size={22}/>Đang tra cứu từ điển…</div> : data && <>
      <div className="dictionary-result-bar"><p role="status">{format(data.total)} kết quả{query && <> cho <strong>“{query}”</strong></>}</p><span>{format(data.word_count)} mục từ trong kho</span></div>
      {!items.length ? <div className="dictionary-empty">
        <BookOpen size={30}/><h3>{state === "due" ? "Chưa có thẻ đến hạn trong bộ lọc." : state === "learned" ? "Bạn chưa ôn từ nào trong bộ lọc này." : "Chưa tìm thấy mục từ phù hợp."}</h3>
        {!!data.suggestions?.length && <div className="dictionary-suggestions"><p>Có phải bạn muốn tìm:</p>{data.suggestions.map(term => <button disabled={busy} key={term} onClick={() => searchFor(term)}>{term}<ArrowRight size={14}/></button>)}</div>}
        {((data.global_total || 0) > 0 || (state !== "all" && (data.matched_count || 0)>0)) && <p>Từ này có trong kho nhưng đang bị bộ lọc ẩn đi.</p>}
        {filtersActive && <button className="toeic-button secondary" onClick={clearFilters}>Tìm trong toàn bộ từ điển</button>}
        {!filtersActive && query && <p>Thử một từ gốc hoặc cụm ngắn hơn. Với từ chưa có trong kho, bạn có thể <a href={`https://en.wiktionary.org/w/index.php?search=${encodeURIComponent(query)}`} target="_blank" rel="noopener noreferrer">tra thêm trên Wiktionary<ExternalLink size={13}/></a>.</p>}
      </div> : <>
        {mode === "flashcard" && <div className="dictionary-study-direction" role="group" aria-label="Chiều ôn thẻ"><span>Tự nhớ trước khi mở đáp án</span><button aria-pressed={direction === "en-vi"} onClick={() => {setDirection("en-vi"); setRevealed(undefined);}}>Anh → Việt</button><button aria-pressed={direction === "vi-en"} onClick={() => {setDirection("vi-en"); setRevealed(undefined);}}>Việt → Anh</button></div>}
        <div className="dictionary-workspace">
          <aside className="dictionary-results" aria-label="Danh sách từ tìm được">
            <div className="dictionary-result-list">{items.map(word => <button key={word.id} disabled={busy} aria-pressed={card?.id === word.id} onClick={() => choose(word.id)}>
              <span className="dictionary-result-term" lang={mode === "flashcard" && direction === "vi-en" ? "vi" : "en"}>{mode === "flashcard" && direction === "vi-en" ? word.meaning_vi || word.meaning : word.term}</span>
              {mode === "dictionary" && <><span className="dictionary-result-meaning" lang="vi">{word.meaning_vi || word.meaning}</span><small>{word.pos?.map(p => posNames[p] || p).join(" · ")}</small></>}
              {mode === "flashcard" && <small>{!word.due ? "Chưa học" : new Date(word.due).getTime() <= Date.now() ? "Đến hạn" : "Đã lên lịch"}</small>}
            </button>)}</div>{pagination()}
          </aside>
          <article ref={detail} tabIndex={-1} className="dictionary-detail" aria-label={mode === "dictionary" ? "Chi tiết từ vựng" : "Thẻ từ đang chọn"}>
            {card && <>
              <div className="dictionary-entry-top"><span>{card.lists.map(s => `${sourceNames[s.id] || s.id}${s.rank ? ` #${s.rank}` : ""}`).join(" · ")}</span>{card.match_kind === "form" && <span className="dictionary-form-match">“{query}” là biến thể của từ này</span>}</div>
              <h3 lang={mode === "flashcard" && direction === "vi-en" && !answerOpen ? "vi" : "en"}>{mode === "flashcard" && direction === "vi-en" && !answerOpen ? card.meaning_vi || card.meaning : card.term}</h3>
              {(mode === "dictionary" || direction === "en-vi" || answerOpen) && <div className="dictionary-pronunciation">{card.ipa ? <span className="dictionary-ipa" title={card.ipa_source}>{card.ipa}</span> : <small>Chưa có phiên âm được xác minh</small>}<button className="toeic-button secondary" aria-label={`Nghe phát âm ${card.term}`} onClick={() => speak(card.term)}><Volume2 size={16}/>Nghe</button></div>}
              <Pos word={card}/>
              {mode === "dictionary" || answerOpen ? <Meanings word={card}/> : <div className="dictionary-recall"><p>{direction === "en-vi" ? "Bạn nhớ nghĩa tiếng Việt của từ này không?" : "Bạn nhớ từ tiếng Anh tương ứng không?"}</p><button className="toeic-button" onClick={() => setRevealed(`${card.id}:${direction}`)}>Hiện đáp án & ví dụ</button></div>}
              {mode === "dictionary" ? <div className="dictionary-entry-footer"><p>Đã hiểu nghĩa? Ôn lại để nhớ lâu hơn.</p><button className="toeic-button" onClick={() => {setMode("flashcard"); setRevealed(undefined);}}><Layers3 size={16}/>Ôn từ này</button></div> : answerOpen && <div className="dictionary-review-actions">{canReview ? <><p>Bạn nhớ ở mức nào?</p><div className="toeic-ratings">{["Học lại", "Khó", "Nhớ được", "Dễ"].map((label, i) => <button key={label} disabled={busy || preview} onClick={() => void review(i+1)}>{label}</button>)}</div>{preview && <p>Đăng nhập để lưu lịch ôn theo tài khoản.</p>}</> : <p>Lần ôn tiếp: {card.due && dateTime(card.due)}. Bạn vẫn có thể đọc lại nghĩa và ví dụ.</p>}</div>}
            </>}
          </article>
        </div>
      </>}
    </>}
    <details className="dictionary-credits"><summary>Nguồn dữ liệu & tải từ điển</summary>
      <p>Dữ liệu từ điển: Từ điển Anh–Việt thichhoc.com (thichhoc-dict), giấy phép CC BY-SA 4.0. <a href="https://github.com/thichhoc-org/thichhoc-dict" target="_blank" rel="noopener noreferrer">thichhoc-dict</a>. Nguồn gốc: WordNet 3.1 (Princeton), CMUdict (CMU), Wiktionary. Đã chỉnh sửa dữ liệu.</p>
      <p>Bổ sung nghĩa và ví dụ từ Wiktionary tiếng Việt qua Kaikki.org, danh sách NGSL/TSL và biên soạn DHV. Một phần kho mở rộng là bản dịch máy, có nhãn nguồn ở từng từ. Giọng đọc do thiết bị cung cấp; chỉ hiện phiên âm có nguồn.</p>
      <div className="toeic-lexicon-downloads"><a className="toeic-button secondary" href={data?.download_url || "/toeic/dictionary/dictionary.json.gz"} download><Download size={15}/>Tải từ điển đầy đủ (.json.gz)</a><a href={data?.attribution_url || "/toeic/licenses/DICTIONARY.md"} target="_blank" rel="noopener noreferrer">Ghi nguồn & giấy phép CC BY-SA 4.0</a></div>
    </details>
  </section>;
}
