from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordOut
from app.auth import require_roles
from app.storage import get_storage

router = APIRouter(tags=["Medical Records"])


@router.get("/records/{record_id}/file-link")
def get_record_file_link(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "doctor")),
):
    """Return link metadata used by the dashboard to open uploaded files."""
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    if not record.file_path:
        raise HTTPException(status_code=404, detail="No file uploaded for this record")

    # Always proxy through app API so GUI uses one stable, authenticated path.
    return {"mode": "proxy", "url": f"/records/{record_id}/file"}


@router.get("/records/{record_id}/file")
def get_record_file(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "doctor")),
):
    """Serve uploaded file bytes for both local storage and S3 storage."""
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    if not record.file_path:
        raise HTTPException(status_code=404, detail="No file uploaded for this record")

    backend = (getattr(settings, "STORAGE_BACKEND", "local") or "local").lower()

    if backend == "s3":
        import boto3  # type: ignore

        bucket = settings.S3_BUCKET
        if not bucket:
            raise HTTPException(status_code=500, detail="S3 bucket is not configured")

        client = boto3.client("s3", region_name=settings.AWS_REGION)
        try:
            obj = client.get_object(Bucket=bucket, Key=record.file_path)
        except client.exceptions.NoSuchKey:
            raise HTTPException(status_code=404, detail="Uploaded file not found")
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Failed to fetch file from S3: {exc}")

        content_type = obj.get("ContentType") or "application/octet-stream"
        filename = Path(record.file_path).name
        headers = {"Content-Disposition": f'inline; filename="{filename}"'}
        return StreamingResponse(obj["Body"], media_type=content_type, headers=headers)

    storage = get_storage()
    file_url = storage.url(record.file_path)

    local_file = Path(file_url)
    if not local_file.exists():
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    return FileResponse(path=str(local_file), filename=local_file.name)


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

    # Save via the configured backend (LocalStorage in Phase 1, S3Storage in Phase 2)
    storage = get_storage()
    key = storage.save(file.filename, contents, content_type=file.content_type or "application/octet-stream")

    record.file_path = key
    db.commit()
    return {"message": "File uploaded", "file_path": key, "backend": settings.STORAGE_BACKEND}


@router.post("/appointments/{appointment_id}/records", response_model=MedicalRecordOut, status_code=201)
def create_record_from_appointment(
    appointment_id: int,
    diagnosis: str = Form(...),
    prescription: str = Form(""),
    notes: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("doctor", "admin")),
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if not db.query(Patient).filter(Patient.id == appointment.patient_id, Patient.is_active == True).first():
        raise HTTPException(status_code=404, detail="Patient not found")

    # Doctor can add records only for their own appointments.
    if current_user.role == "doctor":
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor:
            raise HTTPException(status_code=400, detail="No doctor profile linked to this user")
        if doctor.id != appointment.doctor_id:
            raise HTTPException(status_code=403, detail="You can only add records for your own appointments")

    # Validate upload
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")
    contents = file.file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    storage = get_storage()
    key = storage.save(file.filename, contents, content_type=file.content_type or "application/octet-stream")

    record = MedicalRecord(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        diagnosis=diagnosis,
        prescription=prescription,
        notes=notes,
        file_path=key,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
