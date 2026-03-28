"""Seed script — populates DB with realistic demo data (100 patients, 10 doctors)."""

import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.auth import hash_password

# ─── Realistic Indian name pools ───
FIRST_MALE = [
    "Aarav", "Arjun", "Rahul", "Vikram", "Rohit", "Aditya", "Siddharth", "Karan",
    "Amit", "Rajesh", "Suresh", "Manish", "Deepak", "Nikhil", "Abhishek", "Gaurav",
    "Varun", "Harsh", "Pranav", "Ishaan", "Yash", "Akash", "Vivek", "Ravi",
    "Neeraj", "Sahil", "Tarun", "Mohit", "Ankit", "Ashwin", "Dhruv", "Kunal",
    "Pankaj", "Sandeep", "Vishal", "Jatin", "Mukesh", "Naveen", "Ramesh", "Sunil",
]
FIRST_FEMALE = [
    "Priya", "Ananya", "Sneha", "Kavya", "Neha", "Pooja", "Riya", "Divya",
    "Sakshi", "Anjali", "Shreya", "Meera", "Kriti", "Nisha", "Aishwarya", "Swati",
    "Pallavi", "Tanvi", "Simran", "Bhavna", "Isha", "Ritika", "Sanya", "Zara",
    "Deepika", "Jyoti", "Komal", "Lavanya", "Mira", "Nikita", "Payal", "Rachna",
    "Shalini", "Tanya", "Uma", "Varsha", "Yamini", "Aditi", "Bhavika", "Chitra",
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Reddy", "Iyer",
    "Nair", "Joshi", "Mehta", "Shah", "Rao", "Das", "Mukherjee", "Chatterjee",
    "Bose", "Pillai", "Menon", "Agarwal", "Chauhan", "Yadav", "Thakur", "Saxena",
    "Malhotra", "Kapoor", "Bansal", "Bhatt", "Mishra", "Pandey", "Tiwari", "Dubey",
]
CITIES = [
    "Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune",
    "Jaipur", "Lucknow", "Ahmedabad", "Chandigarh", "Bhopal", "Indore", "Nagpur",
    "Patna", "Thiruvananthapuram", "Kochi", "Coimbatore", "Visakhapatnam", "Surat",
]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
GENDERS = ["Male", "Female"]

# ─── Doctor data ───
DOCTORS = [
    ("Dr. Priya Sharma", "General Medicine", "General Medicine", "dr_sharma"),
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

REASONS = [
    "Routine checkup", "Fever and cold", "Persistent headache", "Back pain",
    "Skin rash", "Chest discomfort", "Eye irritation", "Follow-up visit",
    "Joint pain", "Difficulty breathing", "Stomach ache", "Ear infection",
    "High blood pressure review", "Diabetes management", "Allergy symptoms",
    "Vaccination", "Pregnancy checkup", "Lab results review", "Cough and sore throat",
    "Knee pain", "Dizziness", "Fatigue", "Weight loss consultation",
    "Dental referral follow-up", "Post-surgery review", "Annual physical",
]

DIAGNOSES = [
    "Upper respiratory tract infection", "Mild hypertension", "Type 2 Diabetes (controlled)",
    "Vitamin D deficiency", "Iron deficiency anemia", "Acute gastritis",
    "Lumbar strain", "Contact dermatitis", "Allergic rhinitis", "Migraine",
    "Conjunctivitis", "Otitis media", "Osteoarthritis", "GERD",
    "Urinary tract infection", "Bronchitis", "Cervical spondylosis",
    "Hypothyroidism", "Anxiety disorder", "Mild angina",
]

PRESCRIPTIONS = [
    "Paracetamol 500mg TDS x 5 days", "Amoxicillin 500mg TDS x 7 days",
    "Omeprazole 20mg OD x 14 days", "Metformin 500mg BD",
    "Amlodipine 5mg OD", "Vitamin D3 60000 IU weekly x 8 weeks",
    "Iron tablets OD x 30 days", "Cetirizine 10mg OD x 10 days",
    "Ibuprofen 400mg BD x 5 days", "Pantoprazole 40mg OD x 14 days",
    "Levothyroxine 50mcg OD", "Aspirin 75mg OD", "Atorvastatin 10mg OD",
    "Azithromycin 500mg OD x 3 days", "Cough syrup 10ml TDS x 5 days",
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).filter(User.username == "admin").first():
        print("Database already seeded. Skipping.")
        db.close()
        return

    random.seed(42)  # Reproducible data

    # ─── Users ───
    admin = User(username="admin", password_hash=hash_password("admin123"),
                 full_name="Admin User", role="admin")
    doc_user = User(username="dr_sharma", password_hash=hash_password("doctor123"),
                    full_name="Dr. Priya Sharma", role="doctor")
    recep_user = User(username="reception1", password_hash=hash_password("recep123"),
                      full_name="Ravi Kumar", role="receptionist")
    db.add_all([admin, doc_user, recep_user])
    db.flush()

    # ─── 10 Doctors ───
    doctors = []
    for name, spec, dept, uname in DOCTORS:
        uid = doc_user.id if uname == "dr_sharma" else None
        d = Doctor(
            user_id=uid, name=name, specialization=spec,
            department=dept, contact=f"98{random.randint(10000000, 99999999)}"
        )
        db.add(d)
        doctors.append(d)
    db.flush()
    print(f"  Created {len(doctors)} doctors")

    # ─── 100 Patients ───
    patients = []
    for i in range(100):
        gender = random.choice(GENDERS)
        first = random.choice(FIRST_MALE if gender == "Male" else FIRST_FEMALE)
        last = random.choice(LAST_NAMES)
        p = Patient(
            name=f"{first} {last}",
            age=random.randint(5, 85),
            gender=gender,
            contact=f"9{random.randint(100000000, 999999999)}",
            address=random.choice(CITIES),
            blood_group=random.choice(BLOOD_GROUPS),
        )
        db.add(p)
        patients.append(p)
    db.flush()
    print(f"  Created {len(patients)} patients")

    # ─── ~200 Appointments (2 per patient avg, spread over past 30 days + next 15 days) ───
    now = datetime.now()
    appointments = []
    statuses_past = ["completed", "completed", "completed", "cancelled"]  # 75% completed for past
    statuses_future = ["scheduled"]

    for p in patients:
        num_appts = random.randint(1, 4)
        for _ in range(num_appts):
            days_offset = random.randint(-30, 15)
            dt = now + timedelta(days=days_offset, hours=random.randint(8, 17), minutes=random.choice([0, 15, 30, 45]))
            is_past = days_offset < 0
            status = random.choice(statuses_past) if is_past else random.choice(statuses_future)
            a = Appointment(
                patient_id=p.id,
                doctor_id=random.choice(doctors).id,
                date_time=dt,
                reason=random.choice(REASONS),
                status=status,
            )
            db.add(a)
            appointments.append(a)
    db.flush()
    print(f"  Created {len(appointments)} appointments")

    # ─── Medical records for completed appointments ───
    records_count = 0
    for a in appointments:
        if a.status == "completed" and random.random() < 0.8:  # 80% of completed get a record
            r = MedicalRecord(
                patient_id=a.patient_id,
                doctor_id=a.doctor_id,
                diagnosis=random.choice(DIAGNOSES),
                prescription=random.choice(PRESCRIPTIONS),
                notes=random.choice([
                    "Patient responding well to treatment",
                    "Follow-up in 2 weeks recommended",
                    "Lab tests ordered — CBC, LFT, KFT",
                    "Vitals normal. Continue current medication",
                    "Referred to specialist for further evaluation",
                    "Patient advised lifestyle modifications",
                    "Symptoms improved since last visit",
                    "X-ray results normal. Rest advised",
                    "Blood sugar levels within range",
                    "Blood pressure stable on current dosage",
                ]),
            )
            db.add(r)
            records_count += 1

    db.commit()
    db.close()

    print(f"  Created {records_count} medical records")
    print()
    print("Database seeded successfully!")
    print("  Admin login:       admin / admin123")
    print("  Doctor login:      dr_sharma / doctor123")
    print("  Receptionist:      reception1 / recep123")
    print(f"  Total: {len(patients)} patients, {len(doctors)} doctors, {len(appointments)} appointments, {records_count} records")


if __name__ == "__main__":
    seed()
