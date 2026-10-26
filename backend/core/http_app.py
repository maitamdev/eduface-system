"""Apply CORS outside FastAPI's error handler while retaining its normal API."""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from core.logging_context import RequestIDMiddleware


class CorsFastAPI(FastAPI):
    def __init__(self, *, cors_origins: list[str], **kwargs):
        super().__init__(**kwargs)
        self.cors_origins = list(cors_origins)

    def build_middleware_stack(self) -> ASGIApp:
        # add_middleware(CORSMiddleware) puts CORS inside ServerErrorMiddleware:
        # unexpected 500 responses then bypass CORS and look like network errors.
        cors = CORSMiddleware(
            super().build_middleware_stack(),
            allow_origins=self.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["X-Request-ID"],
        )
        return RequestIDMiddleware(cors)
