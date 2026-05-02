"""End-to-end test: upload a medical record file via the new pluggable storage layer."""
from __future__ import annotations

from pathlib import Path

import pytest

from app import storage as storage_mod
from app.auth import hash_password
from app.models.doctor import Doctor
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.models.user import User


def test_upload_uses_local_backend(client, db, monkeypatch, tmp_path):
    """Smoke test: doctor uploads a PDF; backend writes to tmp dir; record updated."""
    from app.config import settings

    # Force local backend pointing at the test tmp dir
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    storage_mod.reset_storage()

    # Seed doctor user + doctor profile + patient + medical record
    doc_user = User(username="updoc", password_hash=hash_password("p"), full_name="D", role="doctor")
    db.add(doc_user)
    db.flush()
    doctor = Doctor(user_id=doc_user.id, name="D", specialization="X", department="Y", contact="9")
    db.add(doctor)
    patient = Patient(name="P", age=30, gender="M", contact="9", address="A", blood_group="O+", is_active=True)
    db.add(patient)
    db.flush()
    record = MedicalRecord(patient_id=patient.id, doctor_id=doctor.id, diagnosis="d", prescription="p", notes="n")
    db.add(record)
    db.commit()
    record_id = record.id

    token_resp = client.post("/auth/login", json={"username": "updoc", "password": "p"})
    token = token_resp.json()["access_token"]

    fake_pdf = b"%PDF-1.4 fake content"
    resp = client.post(
        f"/upload/{record_id}",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("xray.pdf", fake_pdf, "application/pdf")},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["backend"] == "local"
    saved = Path(body["file_path"])
    assert saved.exists()
    assert saved.read_bytes() == fake_pdf
    storage_mod.reset_storage()


def test_upload_rejects_disallowed_extension(client, db, monkeypatch, tmp_path):
    from app.config import settings

    monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    storage_mod.reset_storage()

    doc_user = User(username="updoc2", password_hash=hash_password("p"), full_name="D", role="doctor")
    db.add(doc_user)
    db.flush()
    doctor = Doctor(user_id=doc_user.id, name="D", specialization="X", department="Y", contact="9")
    db.add(doctor)
    patient = Patient(name="P", age=30, gender="M", contact="9", address="A", blood_group="O+", is_active=True)
    db.add(patient)
    db.flush()
    record = MedicalRecord(patient_id=patient.id, doctor_id=doctor.id, diagnosis="d", prescription="p", notes="n")
    db.add(record)
    db.commit()

    token = client.post("/auth/login", json={"username": "updoc2", "password": "p"}).json()["access_token"]
    resp = client.post(
        f"/upload/{record.id}",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("evil.exe", b"MZ", "application/octet-stream")},
    )
    assert resp.status_code == 400
    assert "not allowed" in resp.json()["detail"]
    storage_mod.reset_storage()
