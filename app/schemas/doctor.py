from pydantic import BaseModel
from typing import Optional


class DoctorCreate(BaseModel):
    name: str
    specialization: str
    department: str
    contact: str
    user_id: Optional[int] = None


class DoctorOut(BaseModel):
    id: int
    name: str
    specialization: str
    department: str
    contact: str
    user_id: Optional[int] = None

    model_config = {"from_attributes": True}
