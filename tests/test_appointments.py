from datetime import datetime, timedelta

from app.models.patient import Patient
from app.models.doctor import Doctor
from tests.conftest import auth_header


def _create_patient_and_doctor(db):
    p = Patient(name="P1", age=30, gender="Male", contact="111")
    d = Doctor(name="D1", specialization="General", department="General", contact="222")
    db.add_all([p, d])
    db.commit()
    return p.id, d.id


def test_create_appointment(client, admin_token, db):
    pid, did = _create_patient_and_doctor(db)
    resp = client.post(
        "/appointments/",
        json={"patient_id": pid, "doctor_id": did, "date_time": (datetime.now() + timedelta(days=1)).isoformat(), "reason": "Checkup"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "scheduled"


def test_list_appointments_filter(client, admin_token, db):
    pid, did = _create_patient_and_doctor(db)
    client.post(
        "/appointments/",
        json={"patient_id": pid, "doctor_id": did, "date_time": datetime.now().isoformat(), "reason": "A"},
        headers=auth_header(admin_token),
    )
    resp = client.get(f"/appointments/?patient_id={pid}", headers=auth_header(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_update_appointment_status(client, admin_token, db):
    pid, did = _create_patient_and_doctor(db)
    create = client.post(
        "/appointments/",
        json={"patient_id": pid, "doctor_id": did, "date_time": datetime.now().isoformat(), "reason": "A"},
        headers=auth_header(admin_token),
    )
    aid = create.json()["id"]
    resp = client.patch(f"/appointments/{aid}", json={"status": "completed"}, headers=auth_header(admin_token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


def test_invalid_appointment_status(client, admin_token, db):
    pid, did = _create_patient_and_doctor(db)
    create = client.post(
        "/appointments/",
        json={"patient_id": pid, "doctor_id": did, "date_time": datetime.now().isoformat(), "reason": "A"},
        headers=auth_header(admin_token),
    )
    aid = create.json()["id"]
    resp = client.patch(f"/appointments/{aid}", json={"status": "invalid"}, headers=auth_header(admin_token))
    assert resp.status_code == 400
