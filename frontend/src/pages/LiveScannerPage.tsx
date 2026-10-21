import React, { useCallback, useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Camera, Upload, SwitchCamera, ScanFace } from "lucide-react";
import { attendanceApi, sessionsApi, getSocketAuthentication, type IdentifyResult, type WsFrameResponse } from "@/api/client";
import { useLanguage } from "@/context/LanguageContext";
import { useResource } from "@/hooks/useResource";
import { useCamera, captureVideoFrame } from "@/hooks/useCamera";
import { appPath, dateTime, errorMessage, isDesignPreview } from "@/lib/format";
import { PageHeader, Section, RefreshButton, ErrorNotice, Field, EmptyState, Table } from "@/components/ProductUI";

export const LiveScannerPage: React.FC = () => {
  const { t, lang } = useLanguage();
  const [params, setParams] = useSearchParams();
  const sessionLoader = useCallback(() => sessionsApi.list(true), []);
  const sessions = useResource(sessionLoader, []);
  const sessionId = params.get("sessionId") || sessions.data[0]?.id || "";
  const selected = sessions.data.find((session) => session.id === sessionId);
  const recordsLoader = useCallback(() => selected ? attendanceApi.list({ session_id: selected.id, limit: 50 }) : Promise.resolve([]), [selected?.id]);
  const records = useResource(recordsLoader, []);
  const camera = useCamera();
  const [source, setSource] = useState<"camera" | "upload">("camera");
  const [mode, setMode] = useState<"mark" | "identify">("mark");
  const [confidence, setConfidence] = useState(.4);
  const [uploaded, setUploaded] = useState<File | null>(null);
  const [uploadUrl, setUploadUrl] = useState("");
  const [results, setResults] = useState<IdentifyResult[]>([]);
  const [scanning, setScanning] = useState(false);
  const [auto, setAuto] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [socketState, setSocketState] = useState<"off" | "connecting" | "on">("off");
  const busy = useRef(false);
  const generation = useRef(0);
  const overlayRef = useRef<HTMLCanvasElement>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const socketTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const socketFrameBusy = useRef(false);
  const [frameSize, setFrameSize] = useState({ width: 1280, height: 720 });

  useEffect(() => {
    if (!uploaded) { setUploadUrl(""); return; }
    const url = URL.createObjectURL(uploaded); setUploadUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [uploaded]);
  const stopSocket = useCallback(() => {
    if (socketTimer.current) clearInterval(socketTimer.current);
    socketTimer.current = null;
    const socket = socketRef.current; socketRef.current = null;
    if (socket) { socket.onclose = null; socket.onerror = null; socket.close(); }
    socketFrameBusy.current = false; setSocketState("off");
  }, []);
  useEffect(() => {
    generation.current++; setResults([]); setMessage(null); setError(null); setAuto(false); stopSocket();
    return () => { generation.current++; stopSocket(); };
  }, [sessionId, source, mode, stopSocket]);
  useEffect(() => { if (source !== "camera") camera.stop(); }, [source, camera.stop]);
  useEffect(() => {
    const canvas = overlayRef.current;
    if (!canvas) return;
    canvas.width = frameSize.width; canvas.height = frameSize.height;
    const context = canvas.getContext("2d");
    if (!context) return;
    context.clearRect(0, 0, canvas.width, canvas.height);
    results.forEach((result) => {
      const box = result.face_box;
      context.strokeStyle = result.already_marked ? "#d6ae5e" : "#81b798"; context.lineWidth = 3;
      context.strokeRect(box.left, box.top, box.width, box.height);
    });
  }, [results, frameSize]);

  const scan = useCallback(async () => {
    if (busy.current) return;
    if (mode === "mark" && !selected) { setError(t("Chọn một phiên đang mở trước khi điểm danh.", "Select an active session before checking in.")); setAuto(false); return; }
    if (source === "upload" && !uploaded) { setError(t("Chọn ảnh trước khi quét.", "Select an image first.")); return; }
    const request = generation.current;
    busy.current = true; setScanning(true); setError(null); setMessage(null);
    try {
      const frame = source === "camera" ? await captureVideoFrame(camera.videoRef.current) : uploaded!;
      if (request !== generation.current) return;
      if (source === "camera" && camera.videoRef.current) setFrameSize({ width: camera.videoRef.current.videoWidth, height: camera.videoRef.current.videoHeight });
      const response = mode === "mark" && selected ? await attendanceApi.mark(selected.id, frame, confidence) : await attendanceApi.identify(frame, confidence);
      if (request !== generation.current) return;
      const identified = Array.isArray(response) ? response : response.identified;
      setResults(identified);
      if (Array.isArray(response)) setMessage(identified.length ? t(`Đã nhận diện ${identified.length} người. Không ghi điểm danh.`, `Identified ${identified.length} people. Attendance was not recorded.`) : t("Không tìm thấy khuôn mặt đã đăng ký.", "No enrolled faces found."));
      else {
        setMessage(response.new_records ? t(`Đã ghi nhận ${response.new_records} lượt điểm danh.`, `${response.new_records} check-ins recorded.`) : identified.length ? t("Những người này đã điểm danh trong phiên.", "These people have already checked in.") : t("Không tìm thấy khuôn mặt đã đăng ký.", "No enrolled faces found."));
        if (response.new_records) void records.reload();
      }
    } catch (err) { if (request === generation.current) { setError(errorMessage(err)); setAuto(false); } }
    finally { busy.current = false; setScanning(false); }
  }, [mode, selected?.id, source, uploaded, confidence, camera.videoRef, records.reload, t]);
  const scanRef = useRef(scan); scanRef.current = scan;
  useEffect(() => {
    if (!auto || !camera.streaming || source !== "camera") return;
    let stopped = false;
    let timer: ReturnType<typeof setTimeout>;
    const tick = async () => { await scanRef.current(); if (!stopped) timer = setTimeout(tick, 3500); };
    timer = setTimeout(tick, 3500);
    return () => { stopped = true; clearTimeout(timer); };
  }, [auto, camera.streaming, source]);

  const startSocket = () => {
    if (!camera.streaming || !selected || mode !== "identify" || isDesignPreview()) return;
    stopSocket(); setAuto(false); setSocketState("connecting"); setError(null);
    const socket = new WebSocket(attendanceApi.getWebSocketUrl(selected.id));
    socketRef.current = socket;
    socket.onopen = () => socket.send(JSON.stringify({ type: "auth", ...getSocketAuthentication(), confidence }));
    socket.onmessage = (event) => {
      if (socketRef.current !== socket) return;
      try {
        const data: WsFrameResponse = JSON.parse(event.data);
        if (data.error) { setError(data.error); stopSocket(); return; }
        if (data.status === 200 && !data.matches) {
          setSocketState("on");
          socketTimer.current = setInterval(async () => {
            if (socket.readyState !== WebSocket.OPEN || socketFrameBusy.current) return;
            socketFrameBusy.current = true;
            try { const frame = await captureVideoFrame(camera.videoRef.current); if (socket.readyState === WebSocket.OPEN) { if (camera.videoRef.current) setFrameSize({ width: camera.videoRef.current.videoWidth, height: camera.videoRef.current.videoHeight }); socket.send(frame); } }
            catch (err) { setError(errorMessage(err)); stopSocket(); }
          }, 3500);
        } else if (data.matches) { socketFrameBusy.current = false; setResults(data.matches); }
      } catch { setError(t("Phản hồi máy chủ không hợp lệ.", "Invalid server response.")); stopSocket(); }
    };
    socket.onerror = () => { if (socketRef.current === socket) { setError(t("Không kết nối được luồng nhận diện.", "Live recognition connection failed.")); stopSocket(); } };
    socket.onclose = () => { if (socketRef.current === socket) { setError(t("Luồng nhận diện đã ngắt kết nối.", "Live recognition disconnected.")); stopSocket(); } };
  };
  const stopCamera = () => { setAuto(false); stopSocket(); camera.stop(); };
  const changeUpload = (file: File | undefined) => {
    if (!file) return;
    if (!file.type.startsWith("image/") || file.size > 10 * 1024 * 1024) { setError(t("Chọn ảnh tối đa 10 MB.", "Choose an image of up to 10 MB.")); return; }
    generation.current++; setUploaded(file); setResults([]); setMessage(null); setError(null);
  };
  return <div className="product-page">
    <PageHeader title={t("Máy quét điểm danh", "Attendance scanner")} description={t("Chọn phiên, kiểm tra hình ảnh và bắt đầu nhận diện.", "Select a session, check the image and start recognition.")}><RefreshButton onClick={sessions.reload} loading={sessions.loading} /><Link className="secondary-button" to={appPath("/sessions")}>{t("Quản lý phiên", "Manage sessions")}</Link></PageHeader>
    <ErrorNotice message={sessions.error || records.error || error || camera.error} retry={sessions.error ? sessions.reload : undefined} />
    <div className="scanner-setup"><Field id="scanner-session" label={t("Phiên điểm danh", "Attendance session")}><select id="scanner-session" value={selected?.id || ""} disabled={scanning || socketState !== "off"} onChange={(event) => { const next = new URLSearchParams(params); next.set("sessionId", event.target.value); setParams(next, { replace: true }); }}><option value="">{t("Chọn phiên đang mở", "Choose an active session")}</option>{sessions.data.map((session) => <option value={session.id} key={session.id}>{session.label}</option>)}</select></Field><Field id="scanner-mode" label={t("Chế độ", "Mode")}><select id="scanner-mode" value={mode} disabled={scanning} onChange={(event) => setMode(event.target.value as "mark" | "identify")}><option value="mark">{t("Nhận diện và ghi điểm danh", "Recognize and record attendance")}</option><option value="identify">{t("Chỉ nhận diện · Không lưu điểm danh", "Recognize only · No attendance record")}</option></select></Field></div>
    {!selected && mode === "mark" && !sessions.loading && <p className="section-note">{t("Cần một phiên đang mở để ghi điểm danh.", "An active session is required to record attendance.")} <Link to={appPath("/sessions")} className="text-link">{t("Tạo phiên", "Create session")}</Link></p>}
    <div className="scanner-grid"><Section title={t("Hình ảnh đầu vào", "Input image")}>
      <div className="source-tabs" aria-label={t("Nguồn ảnh", "Image source")}><button aria-pressed={source === "camera"} onClick={() => setSource("camera")} disabled={scanning}><Camera size={14} />Camera</button><button aria-pressed={source === "upload"} onClick={() => setSource("upload")} disabled={scanning}><Upload size={14} />{t("Tải ảnh", "Upload")}</button></div>
      <div className="camera-stage"><video ref={camera.videoRef} autoPlay muted playsInline className={`${source !== "camera" ? "hidden" : ""} ${camera.facing === "user" ? "mirror-video" : ""}`} />{source === "upload" && uploadUrl && <img src={uploadUrl} alt={t("Ảnh dùng để nhận diện", "Image selected for recognition")} onLoad={(event) => setFrameSize({ width: event.currentTarget.naturalWidth, height: event.currentTarget.naturalHeight })} />}{((source === "camera" && !camera.streaming) || (source === "upload" && !uploadUrl)) && <div className="camera-placeholder"><Camera size={30} /><p>{source === "camera" ? t("Camera chưa bật", "Camera is off") : t("Chưa chọn ảnh", "No image selected")}</p></div>}<canvas ref={overlayRef} className={`camera-overlay ${source === "camera" && camera.facing === "user" ? "mirror-video" : ""}`} /></div>
      {source === "camera" ? <div className="camera-controls"><button className="secondary-button" disabled={camera.starting || isDesignPreview()} onClick={() => camera.streaming ? stopCamera() : void camera.start()}>{camera.starting ? t("Đang mở…", "Starting…") : camera.streaming ? t("Tắt camera", "Stop camera") : t("Bật camera", "Start camera")}</button><button className="icon-button" disabled={camera.starting || scanning || socketState !== "off"} onClick={() => { setAuto(false); void camera.flip(); }} aria-label={t("Đổi camera", "Switch camera")}><SwitchCamera size={17} /></button></div> : <Field id="scanner-upload" label={t("Chọn ảnh · Tối đa 10 MB", "Choose image · Up to 10 MB")}><input id="scanner-upload" type="file" accept="image/*" disabled={scanning} onChange={(event) => { changeUpload(event.target.files?.[0]); event.target.value = ""; }} /></Field>}
      {isDesignPreview() && <p className="field-hint">{t("Bản xem thử không mở camera hoặc gửi ảnh lên máy chủ.", "Preview does not open the camera or send photos to the server.")}</p>}
      <div className="scan-options"><Field id="scanner-confidence" label={t(`Ngưỡng nhận diện: ${Math.round(confidence * 100)}%`, `Recognition threshold: ${Math.round(confidence * 100)}%`)}><input id="scanner-confidence" type="range" min="0.1" max="1" step="0.05" value={confidence} disabled={scanning || auto || socketState !== "off"} onChange={(event) => setConfidence(Number(event.target.value))} /></Field>{source === "camera" && <label className="checkbox-label"><input type="checkbox" checked={auto} disabled={!camera.streaming || socketState !== "off" || (mode === "mark" && !selected)} onChange={(event) => setAuto(event.target.checked)} />{t("Quét tự động", "Auto scan")}</label>}</div>
      <div className="page-actions"><button className="primary-button" disabled={scanning || auto || socketState !== "off" || (source === "camera" ? !camera.streaming : !uploaded) || (mode === "mark" && !selected) || isDesignPreview()} onClick={() => void scan()}><ScanFace size={15} />{scanning ? t("Đang quét…", "Scanning…") : mode === "mark" ? t("Quét và điểm danh", "Scan and check in") : t("Nhận diện", "Identify")}</button>{source === "camera" && mode === "identify" && <button className="secondary-button" disabled={!camera.streaming || !selected || scanning || isDesignPreview()} onClick={() => socketState === "off" ? startSocket() : stopSocket()}>{socketState === "off" ? t("Nhận diện trực tiếp", "Live recognition") : socketState === "connecting" ? t("Hủy kết nối", "Cancel connection") : t("Dừng trực tiếp", "Stop live recognition")}</button>}</div>
      {message && <p className="scan-message" role="status">{message}</p>}
    </Section><Section title={t("Kết quả nhận diện", "Recognition results")} description={mode === "identify" ? t("Chế độ này không ghi điểm danh.", "This mode does not record attendance.") : undefined}>{results.length ? <div className="recognition-list">{results.map((result) => <div key={result.azure_person_id}><strong>{result.name}</strong><span>{Math.round(result.confidence * 100)}%</span><small>{mode === "mark" ? result.already_marked ? t("Đã có bản ghi", "Already recorded") : t("Đã ghi điểm danh", "Recorded") : t("Đã nhận diện", "Identified")}</small></div>)}</div> : <EmptyState>{t("Kết quả xuất hiện sau khi quét.", "Results appear after scanning.")}</EmptyState>}</Section></div>
    <Section title={t("Bản ghi của phiên đang chọn", "Selected session records")} action={<Link to={appPath(`/records${selected ? `?sessionId=${selected.id}` : ""}`)} className="text-link">{t("Mở sổ điểm danh", "View records")}</Link>}><Table label={t("Điểm danh trong phiên", "Session check-ins")}><thead><tr><th>{t("Họ và tên", "Name")}</th><th>{t("Khoa / Lớp", "Department")}</th><th>{t("Thời gian", "Time")}</th><th className="align-right">{t("Độ tin cậy", "Confidence")}</th></tr></thead><tbody>{records.data.map((record) => <tr key={record.id}><td className="cell-strong">{record.person_name}</td><td>{record.department || "–"}</td><td>{dateTime(record.marked_at, lang)}</td><td className="align-right">{record.confidence != null ? `${Math.round(record.confidence * 100)}%` : "–"}</td></tr>)}</tbody></Table>{!records.data.length && <EmptyState loading={records.loading}>{records.error ? t("Bản ghi chưa tải được.", "Records unavailable.") : t("Chưa có lượt điểm danh trong phiên.", "No check-ins in this session.")}</EmptyState>}</Section>
  </div>;
};
