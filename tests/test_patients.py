from tests.conftest import auth_header


PATIENT = {"name": "Test Patient", "age": 30, "gender": "Male", "contact": "9999999999", "address": "Test City", "blood_group": "O+"}


def test_create_patient(client, admin_token):
    resp = client.post("/patients/", json=PATIENT, headers=auth_header(admin_token))
    assert resp.status_code == 201
    assert resp.json()["name"] == "Test Patient"


def test_list_patients(client, admin_token):
    client.post("/patients/", json=PATIENT, headers=auth_header(admin_token))
    resp = client.get("/patients/", headers=auth_header(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_patient(client, admin_token):
    create = client.post("/patients/", json=PATIENT, headers=auth_header(admin_token))
    pid = create.json()["id"]
    resp = client.get(f"/patients/{pid}", headers=auth_header(admin_token))
    assert resp.status_code == 200
    assert resp.json()["id"] == pid


def test_update_patient(client, admin_token):
    create = client.post("/patients/", json=PATIENT, headers=auth_header(admin_token))
    pid = create.json()["id"]
    resp = client.put(f"/patients/{pid}", json={"name": "Updated"}, headers=auth_header(admin_token))
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


def test_delete_patient_soft(client, admin_token):
    create = client.post("/patients/", json=PATIENT, headers=auth_header(admin_token))
    pid = create.json()["id"]
    resp = client.delete(f"/patients/{pid}", headers=auth_header(admin_token))
    assert resp.status_code == 204
    # Should not appear in list anymore
    resp = client.get("/patients/", headers=auth_header(admin_token))
    assert len(resp.json()) == 0


def test_search_patients(client, admin_token):
    client.post("/patients/", json=PATIENT, headers=auth_header(admin_token))
    client.post("/patients/", json={**PATIENT, "name": "Another Person"}, headers=auth_header(admin_token))
    resp = client.get("/patients/?search=Test", headers=auth_header(admin_token))
    assert len(resp.json()) == 1


def test_doctor_cannot_create_patient(client, doctor_token):
    resp = client.post("/patients/", json=PATIENT, headers=auth_header(doctor_token))
    assert resp.status_code == 403
