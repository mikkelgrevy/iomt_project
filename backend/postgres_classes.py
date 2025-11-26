from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    dob = Column(Date)

    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}', dob='{self.dob}')>"