"""One explicit origin policy for HTTP and WebSocket transports."""
import os
from urllib.parse import urlsplit


def allowed_origins() -> list[str]:
    defaults = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080",
                "https://ai-attendance-system-mauve.vercel.app", "https://eduface-system.vercel.app",
                "https://face-dhv-edu.vercel.app", "https://dhv-edu.tech", "https://www.dhv-edu.tech",
                "https://maitamdev.io.vn", "https://www.maitamdev.io.vn"]
    configured = os.getenv("ALLOWED_ORIGINS", "").strip()
    origins = [s.strip().rstrip("/") for s in configured.split(",") if s.strip()] if configured else defaults
    for origin in origins:
        parsed = urlsplit(origin)
        if "*" in origin or parsed.scheme not in {"https", "http"} or not parsed.netloc or parsed.path or parsed.query or parsed.fragment or parsed.username:
            raise RuntimeError("ALLOWED_ORIGINS must contain explicit HTTP(S) origins without wildcards or paths.")
    return list(dict.fromkeys(origins))
