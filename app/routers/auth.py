from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import random
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.schemas.user import UserCreate, UserOut, Token, LoginRequest
from app.auth import hash_password, verify_password, create_access_token, require_roles

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": token}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    body: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    if body.role not in ("admin", "doctor", "receptionist"):
        raise HTTPException(status_code=400, detail="Invalid role")
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    return db.query(User).order_by(User.id.desc()).all()


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(require_roles("admin", "doctor", "receptionist"))):
    return current_user


@router.post("/seed")
def seed_database(db: Session = Depends(get_db)):
    """Seed database with demo data if empty. Idempotent."""
    if db.query(User).filter(User.username == "admin").first():
        return {"message": "Database already seeded", "status": "skipped"}
    
    random.seed(42)
    
    # Create demo users
    admin = User(username="admin", password_hash=hash_password("admin123"), full_name="Admin User", role="admin")
    doc_user = User(username="dr_sharma", password_hash=hash_password("doctor123"), full_name="Dr. Priya Sharma", role="doctor")
    recep_user = User(username="reception1", password_hash=hash_password("recep123"), full_name="Ravi Kumar", role="receptionist")
    db.add_all([admin, doc_user, recep_user])
    db.flush()
    
    # Create demo doctors
    doctors_data = [
        ("Dr. Priya Sharma", "General Medicine", "General Medicine", doc_user.id),
        ("Dr. Amit Patel", "Cardiology", "Cardiology", None),
        ("Dr. Sneha Reddy", "Dermatology", "Dermatology", None),
        ("Dr. Rajesh Kumar", "Orthopedics", "Orthopedics", None),
        ("Dr. Kavya Nair", "Pediatrics", "Pediatrics", None),
        ("Dr. Siddharth Joshi", "ENT", "ENT", None),
        ("Dr. Meera Iyer", "Gynecology", "Gynecology", None),
        ("Dr. Arjun Mehta", "Neurology", "Neurology", None),
        ("Dr. Ananya Gupta", "Ophthalmology", "Ophthalmology", None),
        ("Dr. Vikram Rao", "General Surgery", "Surgery", None),
    ]
    
    doctors = []
    for name, spec, dept, uid in doctors_data:
        d = Doctor(user_id=uid, name=name, specialization=spec, department=dept, contact=f"98{random.randint(10000000, 99999999)}")
        db.add(d)
        doctors.append(d)
    db.flush()
    
    # Create demo patients
    patients = []
    for i in range(100):
        p = Patient(
            name=f"Patient {i+1}", age=random.randint(5, 85), gender=random.choice(["Male", "Female"]),
            contact=f"9{random.randint(100000000, 999999999)}", address=random.choice(["Delhi", "Mumbai", "Bangalore"]),
            blood_group=random.choice(["A+", "B+", "O+", "AB+"])
        )
        db.add(p)
        patients.append(p)
    db.flush()
    
    # Create demo appointments
    now = datetime.now()
    for p in patients:
        for _ in range(random.randint(1, 4)):
            dt = now + timedelta(days=random.randint(-30, 15))
            status = "completed" if dt < now else "scheduled"
            a = Appointment(patient_id=p.id, doctor_id=random.choice(doctors).id, date_time=dt, reason="Checkup", status=status)
            db.add(a)
    db.flush()
    
    # Create medical records for completed appointments
    for a in db.query(Appointment).filter(Appointment.status == "completed").all():
        if random.random() < 0.8:
            r = MedicalRecord(patient_id=a.patient_id, doctor_id=a.doctor_id, diagnosis="General checkup", prescription="Advised rest", notes="Normal")
            db.add(r)
    
    db.commit()
    return {"message": "Database seeded successfully", "status": "completed", "default_credentials": "admin / admin123"}
