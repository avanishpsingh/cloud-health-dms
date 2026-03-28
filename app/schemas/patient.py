from pydantic import BaseModel
from typing import Optional


class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    contact: str
    address: str = ""
    blood_group: str = ""


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None


class PatientOut(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    contact: str
    address: str
    blood_group: str
    is_active: bool

    model_config = {"from_attributes": True}
