"""
Smart Attendance System — FastAPI Backend (MongoDB + InsightFace)

Phase 0 hardening (see Remediation_Plan.md):
  - API-key auth on mutating/sensitive endpoints (core/auth.py)
  - Per-IP rate limiting on expensive face-recognition endpoints (slowapi)
  - Defensive ObjectId parsing (no more unhandled 500s on bad session IDs)
  - /api/persons/debug-azure now reports the env vars actually used

Phase 1 hardening:
  - Upload validation: real image decode + size cap, not just content-type (core/validation.py)
  - Request-ID middleware + structured log correlation (core/logging_context.py)
  - backend/.gitignore added (no secrets/venv/cache protection existed before)
  - Dependency scanning wired into CI (.github/workflows/backend-ci.yml)

Phase 2 hardening:
  - Backend unit tests for face-matching thresholds, quality-check rejections,
    and mark_attendance idempotency (backend/tests/, wired into CI)
  - Timing metrics on the InsightFace-heavy path: enroll/identify/duplicate-check
    now log structured op=... duration_ms=... lines (core/azure_face.py)
  - Embedding-store scaling (_load_all) documented as a known, deferred
    limitation rather than fixed — see its docstring and backend/README.md

Phase 3 hardening:
  - RBAC: operator vs admin API keys (core/auth.py) — operators can create/end
    sessions and mark attendance; only admins can enroll/delete persons,
    export data, or hit /debug-* endpoints
  - CORS wildcard guard: startup now hard-fails if ALLOWED_ORIGINS ever
    resolves to "*" while allow_credentials=True (_resolve_cors_origins)
  - Disaster recovery runbook added: see ../docs/DISASTER_RECOVERY.md
"""

import os
import logging
import asyncio
from fastapi import FastAPI, Response
from core.http_app import CorsFastAPI
from contextlib import asynccontextmanager

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from core.database import init_db
from core.rate_limit import limiter
from pymongo.errors import DuplicateKeyError, OperationFailure
from fastapi.responses import JSONResponse
from core.logging_context import install_request_id_filter
from routers import persons, sessions, attendance, reports, dashboard, auth, microsoft_auth, google_auth, academic, toeic

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
install_request_id_filter()


def _preload_insightface():
    """Pre-warm InsightFace model at startup."""
    try:
        from core.azure_face import _get_insight_app
        _get_insight_app()
        logger.info("✅ InsightFace model ready.")
    except Exception as e:
        logger.warning("Pre-load warning (non-fatal): %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.startup_attempted = True
    app.state.database_initialized = False
    retry_task = None
    try:
        await asyncio.wait_for(init_db(), timeout=30.0)
        app.state.database_initialized = True
    except Exception as exc:
        logger.warning(
            "Initial MongoDB connection failed (%s). Will retry in background every 10s — check MongoDB connectivity, least-privilege network access, and index migration diagnostics.",
            exc,
        )
        async def _retry_init_db():
            while True:
                await asyncio.sleep(10)
                try:
                    await asyncio.wait_for(init_db(), timeout=30.0)
                    app.state.database_initialized = True
                    logger.info("✅ Background MongoDB connection succeeded!")
                    return
                except Exception:
                    pass
        retry_task = asyncio.create_task(_retry_init_db())

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _preload_insightface)

    mongo_url = os.getenv("MONGODB_URL", "")
    if not mongo_url:
        logger.warning("MONGODB_URL not set — using localhost!")

    logger.info("=== Startup complete. Ready to serve requests. ===")

    from core.biometric_cleanup import cleanup_loop
    cleanup_task = asyncio.create_task(cleanup_loop())
    keepalive_task = None
    render_url = os.getenv("RENDER_EXTERNAL_URL", "https://eduface-system.onrender.com").rstrip("/")
    if os.getenv("RENDER") or os.getenv("RENDER_EXTERNAL_URL"):
        import urllib.request

        async def _self_keepalive():
            while True:
                await asyncio.sleep(8 * 60)  # mỗi 8 phút
                try:
                    await asyncio.to_thread(
                        urllib.request.urlopen, f"{render_url}/health", None, 10
                    )
                except Exception:
                    pass

        keepalive_task = asyncio.create_task(_self_keepalive())

    try:
        yield
    finally:
        cleanup_task.cancel()
        await asyncio.gather(cleanup_task, return_exceptions=True)
        if retry_task and not retry_task.done():
            retry_task.cancel()
        if keepalive_task and not keepalive_task.done():
            keepalive_task.cancel()


def _resolve_cors_origins() -> list:
    from core.origins import allowed_origins
    return allowed_origins()


allow_origins = _resolve_cors_origins()
app = CorsFastAPI(
    cors_origins=allow_origins,
    title="Smart Attendance System API",
    description="InsightFace + MongoDB powered attendance backend",
    version="4.2.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def add_security_headers(request, call_next):
    if (request.url.path.startswith("/api/") and getattr(app.state, "startup_attempted", False)
            and not getattr(app.state, "database_initialized", False)):
        response = JSONResponse({"detail": "Cơ sở dữ liệu chưa sẵn sàng. Vui lòng thử lại sau."}, status_code=503)
    else:
        response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and response.status_code < 400:
        user = getattr(request.state, "user", None)
        if user is not None:
            from core.audit import record_audit_event
            await record_audit_event(action=f"{request.method} {request.url.path}", actor_id=user.id,
                actor_role=user.role, ip_address=request.client.host if request.client else "unknown",
                target_id=request.url.path, metadata=getattr(request.state, "audit_metadata", {}))
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"

    return response


app.include_router(auth.router,        prefix="/api/auth",       tags=["Authentication"])
app.include_router(google_auth.router, prefix="/api/auth",       tags=["Google sign-in"])
app.include_router(microsoft_auth.router, prefix="/api/auth", tags=["Microsoft sign-in"])
app.include_router(dashboard.router,  prefix="/api/dashboard",  tags=["Dashboard"])
app.include_router(persons.router,    prefix="/api/persons",    tags=["Persons"])
app.include_router(sessions.router,   prefix="/api/sessions",   tags=["Sessions"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(reports.router,    prefix="/api/reports",    tags=["Reports"])
app.include_router(academic.router,   prefix="/api/academic",   tags=["Academic Management"])
app.include_router(toeic.router, prefix="/api/toeic", tags=["TOEIC cùng DHV"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Smart Attendance System API is running"}


@app.get("/health", tags=["Health"])
async def health():
    from fastapi.responses import JSONResponse
    from core.database import get_database
    from core import azure_face
    database_ready = False
    try:
        await asyncio.wait_for(get_database().command("ping"), timeout=2)
        database_ready = True
    except Exception:
        pass
    model_ready = azure_face._app is not None
    ready = database_ready and model_ready and getattr(app.state, "database_initialized", False)
    return JSONResponse({"status": "healthy" if ready else "not_ready",
                         "database": database_ready, "model": model_ready}, status_code=200 if ready else 503)


@app.get("/live", tags=["Health"])
async def liveness():
    return {"status": "alive"}


@app.get("/metrics", tags=["Observability"])
async def metrics():
    from core.metrics import get_prometheus_metrics
    payload, media_type = get_prometheus_metrics()
    return Response(content=payload, media_type=media_type)


@app.exception_handler(DuplicateKeyError)
async def duplicate_key_handler(request, exc):
    return JSONResponse({"detail": "Dữ liệu trùng mã hoặc liên kết đã tồn tại. Tải lại và kiểm tra hồ sơ."}, status_code=409)


@app.exception_handler(OperationFailure)
async def database_operation_handler(request, exc):
    logger.error("Database operation failed (code=%s)", exc.code)
    return JSONResponse({"detail": "Không thể hoàn tất thao tác dữ liệu. Vui lòng tải lại và thử lại."}, status_code=503)


@app.exception_handler(Exception)
async def unexpected_error_handler(request, exc):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error("Unhandled request error: %s %s request_id=%s", request.method,
                 request.url.path, request_id, exc_info=(type(exc), exc, exc.__traceback__))
    return JSONResponse(
        {"detail": "Máy chủ gặp lỗi khi xử lý yêu cầu. Vui lòng cung cấp mã yêu cầu cho quản trị viên.",
         "request_id": request_id},
        status_code=500,
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY"},
    )
