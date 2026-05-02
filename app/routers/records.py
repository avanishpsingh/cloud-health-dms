from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordOut
from app.auth import require_roles
from app.storage import save_medical_record_file
from app.storage import get_storage

router = APIRouter(tags=["Medical Records"])


@router.get("/patients/{patient_id}/records", response_model=list[MedicalRecordOut])
def get_patient_records(
    patient_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "doctor")),
):
    if not db.query(Patient).filter(Patient.id == patient_id).first():
        raise HTTPException(status_code=404, detail="Patient not found")
    return db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).order_by(MedicalRecord.created_at.desc()).all()


@router.post("/patients/{patient_id}/records", response_model=MedicalRecordOut, status_code=201)
def create_record(
    patient_id: int,
    body: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("doctor")),
):
    if not db.query(Patient).filter(Patient.id == patient_id, Patient.is_active == True).first():
        raise HTTPException(status_code=404, detail="Patient not found")
    # Find the doctor linked to this user
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=400, detail="No doctor profile linked to this user")
    record = MedicalRecord(
        patient_id=patient_id,
        doctor_id=doctor.id,
        diagnosis=body.diagnosis,
        prescription=body.prescription,
        notes=body.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/upload/{record_id}", status_code=200)
def upload_file(
    record_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("doctor", "admin")),
):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")

    # Validate size
    contents = file.file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    # This helper keeps local uploads working today and switches cleanly to S3 later.
    record.file_path = save_medical_record_file(contents, file.filename)
    db.commit()
    return {
        "message": "File uploaded",
        "file_path": record.file_path,
        "storage_mode": "s3" if settings.USE_S3_UPLOADS else "local",
    }
