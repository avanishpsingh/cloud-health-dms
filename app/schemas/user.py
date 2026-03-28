from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "receptionist"


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str
