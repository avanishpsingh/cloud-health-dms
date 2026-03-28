from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.doctor import DoctorCreate, DoctorOut
from app.auth import require_roles

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/", response_model=list[DoctorOut])
def list_doctors(
    search: Optional[str] = Query(None, description="Search by name, specialization, or department"),
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "doctor", "receptionist")),
):
    query = db.query(Doctor)
    if search:
        query = query.filter(
            Doctor.name.ilike(f"%{search}%")
            | Doctor.specialization.ilike(f"%{search}%")
            | Doctor.department.ilike(f"%{search}%")
        )
    if department:
        query = query.filter(Doctor.department.ilike(f"%{department}%"))
    return query.order_by(Doctor.id.desc()).all()


@router.post("/", response_model=DoctorOut, status_code=201)
def create_doctor(
    body: DoctorCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    doctor = Doctor(**body.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "doctor", "receptionist")),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor
