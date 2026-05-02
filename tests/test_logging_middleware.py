"""Tests for the structured-logging middleware (Phase 2)."""
from __future__ import annotations

import json
import logging

import pytest

from app.config import settings
from app.logging_middleware import JsonFormatter, configure_logging


def test_json_formatter_emits_valid_json():
    fmt = JsonFormatter()
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    record.request_id = "abc"
    out = fmt.format(record)
    parsed = json.loads(out)
    assert parsed["msg"] == "hello world"
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "app.test"
    assert parsed["request_id"] == "abc"
    assert "ts" in parsed


def test_request_id_header_round_trip(client, admin_token):
    """The middleware should accept an inbound X-Request-ID and not crash."""
    headers = {"X-Request-ID": "req-12345", "Authorization": f"Bearer {admin_token}"}
    resp = client.get("/auth/me", headers=headers)
    # Just exercising the middleware path; auth/me returns 200 for admin.
    assert resp.status_code == 200


def test_configure_logging_idempotent(monkeypatch):
    monkeypatch.setattr(settings, "JSON_LOGS", True)
    monkeypatch.setattr(settings, "LOG_LEVEL", "DEBUG")
    configure_logging()
    configure_logging()  # second call should not duplicate handlers
    assert len(logging.getLogger().handlers) == 1
