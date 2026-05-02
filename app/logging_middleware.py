"""CloudWatch-friendly structured JSON logging.

When `settings.JSON_LOGS=True` (set on EC2 via environment), every log line
is emitted as a single JSON object that the CloudWatch agent ingests
directly into CloudWatch Logs. The middleware also stamps each request
with a UUID and records its latency, enabling per-request tracing in
CloudWatch Logs Insights.
"""
from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings


class JsonFormatter(logging.Formatter):
    """Renders log records as one-line JSON suitable for CloudWatch Logs."""

    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - thin wrapper
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Merge any extra fields attached via logger.info("msg", extra={...})
        for key, value in record.__dict__.items():
            if key in ("args", "msg", "levelname", "name", "msecs", "created",
                       "relativeCreated", "exc_info", "exc_text", "stack_info",
                       "lineno", "funcName", "module", "pathname", "filename",
                       "thread", "threadName", "processName", "process",
                       "levelno"):
                continue
            payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Configure root logger once at app startup."""
    handler = logging.StreamHandler(sys.stdout)
    if settings.JSON_LOGS:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))


logger = logging.getLogger("app.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Adds an X-Request-ID header and emits one structured log per request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "request",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": status_code,
                    "duration_ms": duration_ms,
                    "client": request.client.host if request.client else None,
                },
            )
