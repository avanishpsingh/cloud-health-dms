from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func

from app.database import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    diagnosis = Column(String(200), nullable=False)
    prescription = Column(Text, default="")
    notes = Column(Text, default="")
    file_path = Column(String(300), default="")  # local path (Phase 1) or S3 key (Phase 2)
    created_at = Column(DateTime, server_default=func.now())
