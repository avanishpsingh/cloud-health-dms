from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func

from app.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    contact = Column(String(15), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
