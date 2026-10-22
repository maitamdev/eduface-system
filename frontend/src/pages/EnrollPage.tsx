import React, { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Camera, Upload, Trash2, SwitchCamera, CheckCircle2 } from "lucide-react";
import { personsApi, type EnrollmentAnalysisReport, type PersonOut } from "@/api/client";
import { useLanguage } from "@/context/LanguageContext";
import { useToast } from "@/context/ToastContext";
import { useCamera, captureVideoFrame } from "@/hooks/useCamera";
import { appPath, errorMessage, isDesignPreview } from "@/lib/format";
import { PageHeader, Section, ErrorNotice, Field } from "@/components/ProductUI";

type Photo = { blob: Blob; url: string };
export const EnrollPage: React.FC = () => {
  const { t } = useLanguage();
  const toast = useToast();
  const camera = useCamera();
  const [params] = useSearchParams();
  const [name, setName] = useState(() => params.get("name") || "");
  const [studentId, setStudentId] = useState(() => params.get("studentId") || "");
  const [email, setEmail] = useState(() => params.get("email") || "");
  const [department, setDepartment] = useState(() => params.get("department") || "");
  const [studentUsername, setStudentUsername] = useState("");
  const [studentPassword, setStudentPassword] = useState("");
  const [source, setSource] = useState<"camera" | "upload">(() => params.get("name") ? "camera" : "upload");
  const [photos, setPhotos] = useState<Photo[]>([]);
  const photosRef = useRef(photos);
  const [analysis, setAnalysis] = useState<EnrollmentAnalysisReport | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [capturing, setCapturing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enrolled, setEnrolled] = useState<PersonOut | null>(null);
  const photoGeneration = useRef(0);
  const busy = analyzing || submitting || capturing;
  useEffect(() => { if (source !== "camera") camera.stop(); }, [source, camera.stop]);
  useEffect(() => () => { photosRef.current.forEach((photo) => URL.revokeObjectURL(photo.url)); photoGeneration.current++; }, []);
  const changePhotos = (next: Photo[]) => {
    photosRef.current.filter((photo) => !next.includes(photo)).forEach((photo) => URL.revokeObjectURL(photo.url));
    photosRef.current = next; photoGeneration.current++; setPhotos(next); setAnalysis(null);
  };
  const addFiles = (files: FileList | null) => {
    if (!files) return;
    const incoming = Array.from(files);
    if (incoming.length + photosRef.current.length > 5) { setError(t("Tối đa 5 ảnh cho mỗi hồ sơ.", "Maximum 5 photos per profile.")); return; }
    if (incoming.some((file) => !file.type.startsWith("image/") || file.size > 10 * 1024 * 1024)) { setError(t("Chỉ chọn ảnh, tối đa 10 MB mỗi ảnh.", "Choose image files of up to 10 MB each.")); return; }
    setError(null); changePhotos([...photosRef.current, ...incoming.map((blob) => ({ blob, url: URL.createObjectURL(blob) }))]);
  };
  const capture = async () => {
    if (busy || photosRef.current.length >= 5) return;
    const generation = photoGeneration.current;
    setCapturing(true);
    try { const blob = await captureVideoFrame(camera.videoRef.current); if (generation === photoGeneration.current && photosRef.current.length < 5) changePhotos([...photosRef.current, { blob, url: URL.createObjectURL(blob) }]); }
    catch (err) { setError(errorMessage(err)); } finally { setCapturing(false); }
  };
  const analyze = async () => {
    if (!photos.length || busy) return;
    const generation = photoGeneration.current;
    setAnalyzing(true); setError(null);
    try { const result = await personsApi.analyzePhotos(photos.map((photo) => photo.blob)); if (generation === photoGeneration.current) setAnalysis(result); }
    catch (err) { setError(errorMessage(err)); } finally { setAnalyzing(false); }
  };
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (busy || !name.trim() || !photos.length) return;
    setSubmitting(true); setError(null);
    try {
      const person = await personsApi.enroll({
        name: name.trim(),
        student_id: studentId.trim().toUpperCase() || studentUsername.trim().toUpperCase() || undefined,
        email: email.trim() || undefined,
        department: department.trim() || undefined,
        student_username: studentUsername.trim() || undefined,
        student_password: studentPassword || undefined,
        photos: photos.map((photo) => photo.blob),
      });
      camera.stop(); setEnrolled(person); changePhotos([]); toast.success(t("Đã lưu hồ sơ khuôn mặt.", "Person enrolled."));
    } catch (err) { setError(errorMessage(err)); } finally { setSubmitting(false); }
  };
  const poseGuides = [
    t("1. Chính diện (0°)", "1. Frontal (0°)"),
    t("2. Nghiêng nhẹ trái (~15°)", "2. Slight left (~15°)"),
    t("3. Nghiêng nhẹ phải (~15°)", "3. Slight right (~15°)"),
    t("4. Hơi nâng nhẹ cằm", "4. Slight chin up"),
    t("5. Biểu cảm tự nhiên / Có kính", "5. Natural / Glasses"),
  ];
  if (enrolled) return <div className="product-page"><PageHeader title={t("Đã đăng ký khuôn mặt", "Enrollment complete")} /><div className="enrollment-success"><CheckCircle2 size={23} /><div><h2>{enrolled.name}</h2><p>{t("Hồ sơ đã sẵn sàng để điểm danh.", "The profile is ready for check-ins.")}</p></div></div><div className="page-actions"><Link className="secondary-button" to={appPath("/people")}>{t("Về danh bạ", "View directory")}</Link><button className="primary-button" onClick={() => { setEnrolled(null); setName(""); setStudentId(""); setEmail(""); setDepartment(""); setStudentUsername(""); setStudentPassword(""); }}>{t("Đăng ký người tiếp theo", "Enroll another person")}</button></div></div>;
  return <div className="product-page">
    <PageHeader title={t("Đăng ký & Cập nhật khuôn mặt", "Face enrollment")} description={t("Nhập thông tin (hoặc trùng tên để ghi đè ảnh mới) và chụp từ 1 đến 5 góc mặt chuẩn AI.", "Enter profile details and add 1–5 clear face photos.")}><Link className="secondary-button" to={appPath("/people")}>{t("Về danh bạ", "Back to directory")}</Link></PageHeader>
    <ErrorNotice message={error || camera.error} />
    <form onSubmit={submit} className="enrollment-grid">
      <Section title={t("Thông tin hồ sơ", "Profile information")}><div className="stack-form">
        <Field id="enroll-name" label={t("Họ và tên *", "Full name *")}><input id="enroll-name" autoComplete="name" value={name} maxLength={200} onChange={(event) => setName(event.target.value)} required /></Field>
        <Field id="enroll-mssv" label={t("Mã số sinh viên (MSSV)", "Student ID (MSSV)")}><input id="enroll-mssv" value={studentId} maxLength={50} onChange={(event) => setStudentId(event.target.value)} placeholder={t("VD: 2305CT2070", "e.g. 2305CT2070")} /></Field>
        <Field id="enroll-email" label="Email"><input id="enroll-email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} /></Field>
        <Field id="enroll-department" label={t("Học phần / Lớp", "Course / Class")}><input id="enroll-department" value={department} maxLength={100} onChange={(event) => setDepartment(event.target.value)} placeholder={t("VD: KTCN · CNTT-K21", "e.g. CS-2026 · Intro to AI")} /></Field>
        <Field id="enroll-student-username" label={t("Tạo tài khoản đăng nhập SV (tùy chọn)", "Create student login username (optional)")}><input id="enroll-student-username" autoComplete="off" value={studentUsername} minLength={3} maxLength={50} onChange={(event) => setStudentUsername(event.target.value)} placeholder={t("VD: 2305CT2070", "e.g. 2305CT2070")} /></Field>
        {studentUsername.trim().length > 0 && <Field id="enroll-student-password" label={t("Mật khẩu SV (tối thiểu 6 ký tự)", "Student password (min 6 chars)")}><input id="enroll-student-password" type="password" autoComplete="new-password" value={studentPassword} minLength={6} onChange={(event) => setStudentPassword(event.target.value)} placeholder={t("Mặc định: 123456 nếu để trống", "Defaults to 123456 if blank")} /></Field>}
        <p className="field-hint">{t("Chọn ảnh đủ sáng, lộ rõ cả 2 mắt - mũi - miệng, không che mặt hoặc quay ngang 90°. Nếu nhập trùng họ tên đã có, hệ thống sẽ tự động cập nhật bộ ảnh mới.", "Use well-lit photos where both eyes, nose, and mouth are visible. Re-submitting an existing name updates its face photos.")}</p>
        <button className="primary-button" disabled={busy || !photos.length || (analysis != null && analysis.invalid > 0)} type="submit">{submitting ? t("Đang đăng ký…", "Enrolling…") : t("Lưu hồ sơ", "Save profile")}</button>
      </div></Section>
      <Section title={t("Ảnh khuôn mặt", "Face photos")} action={<span className="muted">{photos.length} / 5</span>}>
        <div className="source-tabs" aria-label={t("Nguồn ảnh", "Photo source")}><button type="button" aria-pressed={source === "upload"} onClick={() => setSource("upload")}><Upload size={14} />{t("Tải ảnh", "Upload")}</button><button type="button" aria-pressed={source === "camera"} onClick={() => setSource("camera")}><Camera size={14} />Camera</button></div>
        {source === "upload" ? <div className="upload-zone"><label htmlFor="enroll-photos">{t("Chọn ảnh từ thiết bị", "Choose photos from your device")}</label><input id="enroll-photos" type="file" accept="image/*" multiple disabled={busy} onChange={(event) => { addFiles(event.target.files); event.target.value = ""; }} /><p>{t("JPG, PNG hoặc WebP · Tối đa 5 ảnh", "JPG, PNG or WebP · Up to 5 photos")}</p></div> : <><div className="camera-stage"><video ref={camera.videoRef} autoPlay muted playsInline className={camera.facing === "user" ? "mirror-video" : ""} />{!camera.streaming && <div className="camera-placeholder"><Camera size={28} /><p>{t("Camera chưa bật", "Camera is off")}</p></div>}</div><div className="camera-controls"><button className="secondary-button" type="button" disabled={camera.starting || isDesignPreview()} onClick={() => camera.streaming ? camera.stop() : void camera.start()}>{camera.starting ? t("Đang mở…", "Starting…") : camera.streaming ? t("Tắt camera", "Stop camera") : t("Bật camera", "Start camera")}</button><button className="icon-button" type="button" disabled={camera.starting} onClick={() => void camera.flip()} aria-label={t("Đổi camera", "Switch camera")}><SwitchCamera size={17} /></button><button className="primary-button" type="button" onClick={capture} disabled={!camera.streaming || busy || photos.length >= 5}>{t("Chụp ảnh", "Capture")}</button></div></>}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 10 }}>
          {poseGuides.map((guide, idx) => (
            <span
              key={idx}
              className={idx < photos.length ? "attendance-status" : "muted"}
              style={{
                fontSize: 11,
                padding: "3px 8px",
                border: "1px solid var(--ui-border)",
                borderRadius: 4,
                background: idx === photos.length ? "var(--ui-soft)" : undefined,
                fontWeight: idx === photos.length ? 600 : 400,
              }}
            >
              {idx < photos.length ? "✓ " : idx === photos.length ? "👉 " : ""}{guide}
            </span>
          ))}
        </div>
        {isDesignPreview() && <p className="field-hint">{t("Bản xem thử không mở camera hoặc gửi ảnh ra máy chủ.", "Preview does not open the camera or send photos to the server.")}</p>}
        {photos.length > 0 && <div className="photo-previews">{photos.map((photo, index) => <figure key={photo.url}><img src={photo.url} alt={t(`Ảnh khuôn mặt ${index + 1}`, `Face photo ${index + 1}`)} /><button className="icon-button" type="button" disabled={busy} aria-label={t(`Xóa ảnh ${index + 1}`, `Remove photo ${index + 1}`)} onClick={() => changePhotos(photos.filter((_, item) => item !== index))}><Trash2 size={14} /></button></figure>)}</div>}
        <button className="secondary-button quality-button" type="button" disabled={!photos.length || busy} onClick={analyze}>{analyzing ? t("Đang kiểm tra…", "Checking…") : t("Kiểm tra chất lượng ảnh", "Check photo quality")}</button>
        {analysis && <div className="quality-results"><p>{t(`${analysis.valid}/${analysis.total} ảnh đạt chất lượng`, `${analysis.valid}/${analysis.total} photos passed`)}</p>{analysis.results.map((item) => <div key={item.photo} className={item.ok ? "attendance-status" : "warning-text"}>{t("Ảnh", "Photo")} {item.photo}: {item.ok ? t("Đạt", "Passed") : item.reason}</div>)}{analysis.invalid > 0 && <p className="warning-text">{t("Vui lòng xóa ảnh không đạt chất lượng trước khi lưu hồ sơ.", "Please remove photos that failed the quality check before saving.")}</p>}</div>}
      </Section>
    </form>
  </div>;
};
