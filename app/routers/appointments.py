from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentOut
from app.auth import require_roles

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("/", response_model=list[AppointmentOut])
def list_appointments(
    patient_id: Optional[int] = Query(None),
    doctor_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "doctor", "receptionist")),
):
    query = db.query(Appointment)
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if status:
        query = query.filter(Appointment.status == status)
    return query.order_by(Appointment.date_time.desc()).all()


@router.post("/", response_model=AppointmentOut, status_code=201)
def create_appointment(
    body: AppointmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "receptionist")),
):
    if not db.query(Patient).filter(Patient.id == body.patient_id, Patient.is_active == True).first():
        raise HTTPException(status_code=404, detail="Patient not found")
    if not db.query(Doctor).filter(Doctor.id == body.doctor_id).first():
        raise HTTPException(status_code=404, detail="Doctor not found")
    appt = Appointment(**body.model_dump())
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


@router.patch("/{appointment_id}", response_model=AppointmentOut)
def update_appointment_status(
    appointment_id: int,
    body: AppointmentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "doctor")),
):
    if body.status not in ("scheduled", "completed", "cancelled"):
        raise HTTPException(status_code=400, detail="Invalid status")
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt.status = body.status
    db.commit()
    db.refresh(appt)
    return appt
