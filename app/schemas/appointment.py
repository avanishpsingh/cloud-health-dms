from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date_time: datetime
    reason: str = ""


class AppointmentUpdate(BaseModel):
    status: str  # scheduled, completed, cancelled


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    date_time: datetime
    reason: str
    status: str

    model_config = {"from_attributes": True}
