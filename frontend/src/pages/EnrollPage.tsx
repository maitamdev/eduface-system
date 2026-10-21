import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
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
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [department, setDepartment] = useState("");
  const [source, setSource] = useState<"camera" | "upload">("upload");
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
      const person = await personsApi.enroll({ name: name.trim(), email: email.trim() || undefined, department: department.trim() || undefined, photos: photos.map((photo) => photo.blob) });
      camera.stop(); setEnrolled(person); changePhotos([]); toast.success(t("Đã đăng ký khuôn mặt.", "Person enrolled."));
    } catch (err) { setError(errorMessage(err)); } finally { setSubmitting(false); }
  };
  if (enrolled) return <div className="product-page"><PageHeader title={t("Đã đăng ký khuôn mặt", "Enrollment complete")} /><div className="enrollment-success"><CheckCircle2 size={23} /><div><h2>{enrolled.name}</h2><p>{t("Hồ sơ đã sẵn sàng để điểm danh.", "The profile is ready for check-ins.")}</p></div></div><div className="page-actions"><Link className="secondary-button" to={appPath("/people")}>{t("Về danh bạ", "View directory")}</Link><button className="primary-button" onClick={() => { setEnrolled(null); setName(""); setEmail(""); setDepartment(""); }}>{t("Đăng ký người tiếp theo", "Enroll another person")}</button></div></div>;
  return <div className="product-page">
    <PageHeader title={t("Đăng ký khuôn mặt", "Face enrollment")} description={t("Nhập thông tin và thêm từ 1 đến 5 ảnh rõ khuôn mặt.", "Enter profile details and add 1–5 clear face photos.")}><Link className="secondary-button" to={appPath("/people")}>{t("Về danh bạ", "Back to directory")}</Link></PageHeader>
    <ErrorNotice message={error || camera.error} />
    <form onSubmit={submit} className="enrollment-grid">
      <Section title={t("Thông tin hồ sơ", "Profile information")}><div className="stack-form">
        <Field id="enroll-name" label={t("Họ và tên *", "Full name *")}><input id="enroll-name" autoComplete="name" value={name} maxLength={200} onChange={(event) => setName(event.target.value)} required /></Field>
        <Field id="enroll-email" label="Email"><input id="enroll-email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} /></Field>
        <Field id="enroll-department" label={t("Khoa / Lớp", "Department / Class")}><input id="enroll-department" value={department} maxLength={100} onChange={(event) => setDepartment(event.target.value)} /></Field>
        <p className="field-hint">{t("Chọn ảnh chính diện, đủ sáng, không đeo khẩu trang. Mỗi ảnh tối đa 10 MB.", "Use well-lit frontal photos without a mask. Maximum 10 MB per photo.")}</p>
        <button className="primary-button" disabled={busy || !photos.length} type="submit">{submitting ? t("Đang đăng ký…", "Enrolling…") : t("Lưu hồ sơ", "Save profile")}</button>
      </div></Section>
      <Section title={t("Ảnh khuôn mặt", "Face photos")} action={<span className="muted">{photos.length} / 5</span>}>
        <div className="source-tabs" aria-label={t("Nguồn ảnh", "Photo source")}><button type="button" aria-pressed={source === "upload"} onClick={() => setSource("upload")}><Upload size={14} />{t("Tải ảnh", "Upload")}</button><button type="button" aria-pressed={source === "camera"} onClick={() => setSource("camera")}><Camera size={14} />Camera</button></div>
        {source === "upload" ? <div className="upload-zone"><label htmlFor="enroll-photos">{t("Chọn ảnh từ thiết bị", "Choose photos from your device")}</label><input id="enroll-photos" type="file" accept="image/*" multiple disabled={busy} onChange={(event) => { addFiles(event.target.files); event.target.value = ""; }} /><p>{t("JPG, PNG hoặc WebP · Tối đa 5 ảnh", "JPG, PNG or WebP · Up to 5 photos")}</p></div> : <><div className="camera-stage"><video ref={camera.videoRef} autoPlay muted playsInline className={camera.facing === "user" ? "mirror-video" : ""} />{!camera.streaming && <div className="camera-placeholder"><Camera size={28} /><p>{t("Camera chưa bật", "Camera is off")}</p></div>}</div><div className="camera-controls"><button className="secondary-button" type="button" disabled={camera.starting || isDesignPreview()} onClick={() => camera.streaming ? camera.stop() : void camera.start()}>{camera.starting ? t("Đang mở…", "Starting…") : camera.streaming ? t("Tắt camera", "Stop camera") : t("Bật camera", "Start camera")}</button><button className="icon-button" type="button" disabled={camera.starting} onClick={() => void camera.flip()} aria-label={t("Đổi camera", "Switch camera")}><SwitchCamera size={17} /></button><button className="primary-button" type="button" onClick={capture} disabled={!camera.streaming || busy || photos.length >= 5}>{t("Chụp ảnh", "Capture")}</button></div></>}
        {isDesignPreview() && <p className="field-hint">{t("Bản xem thử không mở camera hoặc gửi ảnh ra máy chủ.", "Preview does not open the camera or send photos to the server.")}</p>}
        {photos.length > 0 && <div className="photo-previews">{photos.map((photo, index) => <figure key={photo.url}><img src={photo.url} alt={t(`Ảnh khuôn mặt ${index + 1}`, `Face photo ${index + 1}`)} /><button className="icon-button" type="button" disabled={busy} aria-label={t(`Xóa ảnh ${index + 1}`, `Remove photo ${index + 1}`)} onClick={() => changePhotos(photos.filter((_, item) => item !== index))}><Trash2 size={14} /></button></figure>)}</div>}
        <button className="secondary-button quality-button" type="button" disabled={!photos.length || busy} onClick={analyze}>{analyzing ? t("Đang kiểm tra…", "Checking…") : t("Kiểm tra chất lượng ảnh", "Check photo quality")}</button>
        {analysis && <div className="quality-results"><p>{t(`${analysis.valid}/${analysis.total} ảnh đạt chất lượng`, `${analysis.valid}/${analysis.total} photos passed`)}</p>{analysis.results.map((item) => <div key={item.photo} className={item.ok ? "attendance-status" : "warning-text"}>{t("Ảnh", "Photo")} {item.photo}: {item.ok ? t("Đạt", "Passed") : item.reason}</div>)}</div>}
      </Section>
    </form>
  </div>;
};
