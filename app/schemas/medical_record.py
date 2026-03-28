from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MedicalRecordCreate(BaseModel):
    diagnosis: str
    prescription: str = ""
    notes: str = ""


class MedicalRecordOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    diagnosis: str
    prescription: str
    notes: str
    file_path: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
