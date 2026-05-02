"""Tests for the pluggable storage layer (Phase 2).

Covers:
  * LocalStorage round-trip (save → read bytes).
  * S3Storage round-trip via the `moto` mocked S3 service.
  * Factory selects the correct backend from settings.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from app import storage as storage_mod
from app.config import settings


# ---------------------------------------------------------------------------
# LocalStorage
# ---------------------------------------------------------------------------
def test_local_storage_round_trip(tmp_path: Path):
    backend = storage_mod.LocalStorage(str(tmp_path))
    key = backend.save("report.pdf", b"hello world", content_type="application/pdf")

    p = Path(key)
    assert p.exists(), "file should be written to disk"
    assert p.read_bytes() == b"hello world"
    assert p.suffix == ".pdf"

    # url() for local is just the path
    assert backend.url(key) == key

    backend.delete(key)
    assert not p.exists()


# ---------------------------------------------------------------------------
# S3Storage (mocked with moto)
# ---------------------------------------------------------------------------
moto = pytest.importorskip("moto", reason="install moto to run S3 tests")
boto3 = pytest.importorskip("boto3")


@pytest.fixture
def s3_bucket(monkeypatch):
    """Spin up an in-memory S3, create a bucket, yield its name."""
    from moto import mock_aws

    with mock_aws():
        client = boto3.client("s3", region_name="ap-south-1")
        client.create_bucket(
            Bucket="test-medical-files",
            CreateBucketConfiguration={"LocationConstraint": "ap-south-1"},
        )
        # Make sure factory builds the S3 backend
        monkeypatch.setattr(settings, "STORAGE_BACKEND", "s3")
        monkeypatch.setattr(settings, "S3_BUCKET", "test-medical-files")
        monkeypatch.setattr(settings, "AWS_REGION", "ap-south-1")
        monkeypatch.setattr(settings, "S3_KMS_KEY_ID", "")  # use SSE-S3 in tests
        storage_mod.reset_storage()
        yield "test-medical-files"
        storage_mod.reset_storage()


def test_s3_storage_round_trip(s3_bucket):
    backend = storage_mod.get_storage()
    assert isinstance(backend, storage_mod.S3Storage)

    key = backend.save("scan.png", b"PNGDATA", content_type="image/png")
    assert key.startswith("medical-records/")
    assert key.endswith(".png")

    # The object should exist in the mocked S3
    head = backend.client.head_object(Bucket=s3_bucket, Key=key)
    assert head["ContentLength"] == len(b"PNGDATA")

    # Pre-signed URL should be returned and contain the bucket + key
    url = backend.url(key)
    assert s3_bucket in url and key in url

    backend.delete(key)
    with pytest.raises(Exception):
        backend.client.head_object(Bucket=s3_bucket, Key=key)


def test_factory_default_is_local(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    storage_mod.reset_storage()
    backend = storage_mod.get_storage()
    assert isinstance(backend, storage_mod.LocalStorage)


def test_factory_rejects_s3_without_bucket(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "s3")
    monkeypatch.setattr(settings, "S3_BUCKET", "")
    storage_mod.reset_storage()
    with pytest.raises(RuntimeError):
        storage_mod.get_storage()
    storage_mod.reset_storage()
