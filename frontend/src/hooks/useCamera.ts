import { useCallback, useEffect, useRef, useState } from "react";

export function useCamera() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const generation = useRef(0);
  const mounted = useRef(true);
  const [streaming, setStreaming] = useState(false);
  const [starting, setStarting] = useState(false);
  const [facing, setFacing] = useState<"user" | "environment">("user");
  const [error, setError] = useState<string | null>(null);
  const stop = useCallback(() => {
    generation.current++;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    if (mounted.current) { setStreaming(false); setStarting(false); }
  }, []);
  const start = useCallback(async (mode?: "user" | "environment") => {
    stop();
    const request = generation.current;
    setError(null); setStarting(true);
    try {
      if (!navigator.mediaDevices?.getUserMedia) throw new Error("Camera cần HTTPS hoặc localhost / Camera requires HTTPS or localhost.");
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: mode || facing }, width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false });
      if (!mounted.current || request !== generation.current) { stream.getTracks().forEach((track) => track.stop()); return; }
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setStreaming(true);
    } catch (err) {
      if (mounted.current && request === generation.current) setError(err instanceof Error ? err.message : "Camera unavailable");
    } finally { if (mounted.current && request === generation.current) setStarting(false); }
  }, [facing, stop]);
  const flip = useCallback(async () => {
    const next = facing === "user" ? "environment" : "user";
    setFacing(next);
    if (streaming) await start(next);
  }, [facing, streaming, start]);
  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; generation.current++; streamRef.current?.getTracks().forEach((track) => track.stop()); };
  }, []);
  return { videoRef, streaming, starting, facing, error, start, stop, flip };
}

export async function captureVideoFrame(video: HTMLVideoElement | null): Promise<Blob> {
  if (!video || video.readyState < 2 || !video.videoWidth || !video.videoHeight) throw new Error("Camera chưa sẵn sàng / Camera is not ready.");
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth; canvas.height = video.videoHeight;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("Không thể chụp ảnh / Cannot capture a frame.");
  context.drawImage(video, 0, 0);
  return new Promise((resolve, reject) => canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error("Không thể chụp ảnh / Cannot capture a frame.")), "image/jpeg", .9));
}
