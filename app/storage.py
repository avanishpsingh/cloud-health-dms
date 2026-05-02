"""Pluggable storage backend.

Phase 1 used the local filesystem (`uploads/`). Phase 2 introduces an S3
backend so the same FastAPI code runs unchanged on AWS EC2.

The backend is selected at import time via `settings.STORAGE_BACKEND`:
  * `local` — write to `settings.UPLOAD_DIR` (Phase 1 behaviour)
  * `s3`    — write to `settings.S3_BUCKET` using boto3

Both backends share the same interface:
    save(filename, content_bytes, content_type)  -> str  (storage key)
    url(key)                                     -> str  (download URL)
    delete(key)                                  -> None

This keeps callers (routers/records.py) identical between phases.
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Protocol

from app.config import settings


class StorageBackend(Protocol):
    """Storage backend protocol — both Local and S3 implement this."""

    def save(self, filename: str, content: bytes, content_type: str = "application/octet-stream") -> str: ...

    def url(self, key: str) -> str: ...

    def delete(self, key: str) -> None: ...


class LocalStorage:
    """Filesystem-backed storage (Phase 1 behaviour, also used in tests)."""

    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        ext = Path(filename).suffix.lower()
        key = f"{uuid.uuid4().hex}{ext}"
        (self.root / key).write_bytes(content)
        return str(self.root / key)

    def url(self, key: str) -> str:
        # For local storage the "URL" is just the filesystem path.
        return key

    def delete(self, key: str) -> None:
        p = Path(key)
        if p.exists():
            p.unlink()


class S3Storage:
    """S3-backed storage (Phase 2)."""

    def __init__(self, bucket: str, region: str, prefix: str = "medical-records/"):
        # boto3 is imported lazily so local-only environments don't need it
        import boto3  # type: ignore

        self.bucket = bucket
        self.prefix = prefix.rstrip("/") + "/"
        self.region = region
        self.client = boto3.client("s3", region_name=region)

    def save(self, filename: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        ext = Path(filename).suffix.lower()
        key = f"{self.prefix}{uuid.uuid4().hex}{ext}"
        # Server-side encryption with KMS — required for HIPAA/DISHA compliance
        extra = {"ContentType": content_type, "ServerSideEncryption": "AES256"}
        if settings.S3_KMS_KEY_ID:
            extra["ServerSideEncryption"] = "aws:kms"
            extra["SSEKMSKeyId"] = settings.S3_KMS_KEY_ID
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content, **extra)
        return key

    def url(self, key: str) -> str:
        # Pre-signed URL with 1 hour expiry — never expose raw S3 URLs
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=3600,
        )

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)


def build_storage() -> StorageBackend:
    """Factory that returns the configured storage backend."""
    backend = (getattr(settings, "STORAGE_BACKEND", "local") or "local").lower()
    if backend == "s3":
        bucket = settings.S3_BUCKET
        if not bucket:
            raise RuntimeError("STORAGE_BACKEND=s3 but S3_BUCKET is not configured")
        return S3Storage(
            bucket=bucket,
            region=getattr(settings, "AWS_REGION", os.getenv("AWS_REGION", "us-east-1")),
            prefix=getattr(settings, "S3_PREFIX", "medical-records/"),
        )
    return LocalStorage(settings.UPLOAD_DIR)


# Module-level singleton — but built lazily so tests can monkeypatch settings first.
_storage: StorageBackend | None = None


def get_storage() -> StorageBackend:
    global _storage
    if _storage is None:
        _storage = build_storage()
    return _storage


def reset_storage() -> None:
    """Test helper — drop the cached backend so the next call rebuilds it."""
    global _storage
    _storage = None
