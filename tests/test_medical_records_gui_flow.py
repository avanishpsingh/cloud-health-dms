from __future__ import annotations

from datetime import datetime, timedelta

from app import storage as storage_mod
from app.auth import hash_password
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.models.user import User


def _seed_patient(db) -> Patient:
    patient = Patient(name="GUI Patient", age=34, gender="Male", contact="9999999999", is_active=True)
    db.add(patient)
    db.flush()
    return patient


def _seed_doctor_user(db, username: str, password: str, full_name: str) -> tuple[User, Doctor]:
    user = User(username=username, password_hash=hash_password(password), full_name=full_name, role="doctor")
    db.add(user)
    db.flush()
    doctor = Doctor(user_id=user.id, name=full_name, specialization="General", department="General", contact="1234567890")
    db.add(doctor)
    db.flush()
    return user, doctor


def test_create_record_from_appointment_with_file_success(client, db, monkeypatch, tmp_path, doctor_token):
    from app.config import settings

    monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    storage_mod.reset_storage()

    # doctor_token fixture creates user `doc1` + linked doctor profile.
    doctor_user = db.query(User).filter(User.username == "doc1").first()
    doctor = db.query(Doctor).filter(Doctor.user_id == doctor_user.id).first()
    patient = _seed_patient(db)

    appt = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        date_time=datetime.now() + timedelta(days=1),
        reason="Follow-up",
        status="scheduled",
    )
    db.add(appt)
    db.commit()

    resp = client.post(
        f"/appointments/{appt.id}/records",
        headers={"Authorization": f"Bearer {doctor_token}"},
        data={
            "diagnosis": "Viral fever",
            "prescription": "Paracetamol",
            "notes": "Hydrate and rest",
        },
        files={"file": ("report.pdf", b"%PDF-1.4 test", "application/pdf")},
    )

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["patient_id"] == patient.id
    assert body["doctor_id"] == doctor.id
    assert body["diagnosis"] == "Viral fever"
    assert body["file_path"]

    rec = db.query(MedicalRecord).filter(MedicalRecord.id == body["id"]).first()
    assert rec is not None
    assert rec.file_path
    storage_mod.reset_storage()


def test_doctor_cannot_create_record_for_other_doctors_appointment(client, db, monkeypatch, tmp_path, doctor_token):
    from app.config import settings

    monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    storage_mod.reset_storage()

    patient = _seed_patient(db)
    _, other_doctor = _seed_doctor_user(db, username="otherdoc", password="other123", full_name="Dr. Other")

    appt = Appointment(
        patient_id=patient.id,
        doctor_id=other_doctor.id,
        date_time=datetime.now() + timedelta(days=1),
        reason="Specialist review",
        status="scheduled",
    )
    db.add(appt)
    db.commit()

    resp = client.post(
        f"/appointments/{appt.id}/records",
        headers={"Authorization": f"Bearer {doctor_token}"},
        data={
            "diagnosis": "Should fail",
            "prescription": "N/A",
            "notes": "N/A",
        },
        files={"file": ("report.pdf", b"%PDF-1.4 test", "application/pdf")},
    )

    assert resp.status_code == 403
    assert "own appointments" in resp.json()["detail"]
    storage_mod.reset_storage()
