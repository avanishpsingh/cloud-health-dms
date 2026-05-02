"""Tests for the appointment-reminder Lambda handler (Phase 2)."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.lambda_handlers import appointment_reminder as ar
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User
from app.auth import hash_password


@pytest.fixture
def seeded_db(db):
    """Seed an admin, a patient, a doctor, and 3 appointments at known offsets."""
    admin = User(username="lambda_admin", password_hash=hash_password("x"), full_name="A", role="admin")
    db.add(admin)
    db.flush()
    patient = Patient(name="P1", age=40, gender="M", contact="9", address="A", blood_group="O+", is_active=True)
    db.add(patient)
    doctor_user = User(username="lambda_doc", password_hash=hash_password("x"), full_name="D", role="doctor")
    db.add(doctor_user)
    db.flush()
    doc = Doctor(user_id=doctor_user.id, name="Dr X", specialization="Gen", department="Gen", contact="9")
    db.add(doc)
    db.flush()

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    a_due  = Appointment(patient_id=patient.id, doctor_id=doc.id, date_time=now + timedelta(hours=2),  reason="due", status="scheduled")
    a_far  = Appointment(patient_id=patient.id, doctor_id=doc.id, date_time=now + timedelta(hours=72), reason="far", status="scheduled")
    a_done = Appointment(patient_id=patient.id, doctor_id=doc.id, date_time=now + timedelta(hours=1),  reason="done", status="completed")
    db.add_all([a_due, a_far, a_done])
    db.commit()
    return db


def test_find_due_appointments_filters_window_and_status(seeded_db):
    due = ar.find_due_appointments(seeded_db, hours_ahead=24)
    reasons = sorted(a.reason for a in due)
    assert reasons == ["due"], "only the in-window scheduled appointment should match"


def test_lambda_handler_dry_run_when_no_topic(seeded_db, monkeypatch):
    """No SNS_TOPIC_ARN → handler should still run, returning skipped count."""
    monkeypatch.delenv("SNS_TOPIC_ARN", raising=False)

    # The handler does `from app.database import SessionLocal` lazily, so patch at the source module.
    from tests.conftest import TestSession
    with patch("app.database.SessionLocal", new=TestSession):
        result = ar.lambda_handler({}, None)

    assert result["published"] == 0
    assert result["skipped"] == 1
    assert result["ids"] == []


def test_lambda_handler_publishes_to_sns(seeded_db, monkeypatch):
    """When SNS topic is configured, each due appointment is published."""
    monkeypatch.setenv("SNS_TOPIC_ARN", "arn:aws:sns:ap-south-1:111122223333:reminders")

    fake_sns = MagicMock()
    fake_sns.publish.return_value = {"MessageId": "msg-123"}

    from tests.conftest import TestSession

    with patch("app.database.SessionLocal", new=TestSession), \
         patch("boto3.client", return_value=fake_sns):
        result = ar.lambda_handler({}, None)

    assert result["published"] == 1
    assert result["skipped"] == 0
    assert result["ids"] == ["msg-123"]
    fake_sns.publish.assert_called_once()
    # Ensure the published payload is the expected JSON shape
    args, kwargs = fake_sns.publish.call_args
    assert kwargs["TopicArn"].endswith(":reminders")
    assert "appointment_id" in kwargs["Message"]
