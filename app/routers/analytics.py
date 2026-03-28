from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.user import User
from app.auth import require_roles

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    total_patients = db.query(func.count(Patient.id)).filter(Patient.is_active == True).scalar()
    total_doctors = db.query(func.count(Doctor.id)).scalar()
    total_appointments = db.query(func.count(Appointment.id)).scalar()
    scheduled = db.query(func.count(Appointment.id)).filter(Appointment.status == "scheduled").scalar()
    completed = db.query(func.count(Appointment.id)).filter(Appointment.status == "completed").scalar()
    cancelled = db.query(func.count(Appointment.id)).filter(Appointment.status == "cancelled").scalar()

    # Department-wise patient count (via doctors → appointments)
    dept_stats = (
        db.query(Doctor.department, func.count(func.distinct(Appointment.patient_id)))
        .join(Appointment, Appointment.doctor_id == Doctor.id)
        .group_by(Doctor.department)
        .all()
    )

    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "appointments_by_status": {
            "scheduled": scheduled,
            "completed": completed,
            "cancelled": cancelled,
        },
        "patients_by_department": {dept: count for dept, count in dept_stats},
    }
