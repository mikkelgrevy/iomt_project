from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime, Time, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    dob = Column(Date)

    plans = relationship("MedicationPlan", back_populates="patient")

    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}', dob='{self.dob}')>"

class MedicationPlan(Base):
    __tablename__ = "medication_plans"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))

    medication_name = Column(String)
    dosage = Column(String)
    schedule_time = Column(Time)

    patient = relationship("Patient", back_populates="plans")
    logs = relationship("MedicationLog", back_populates="plan")

class MedicationLog(Base):
    __tablename__ = "medication_logs"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("medication_plans.id"))

    timestamp = Column(DateTime, default=datetime.utcnow)

    dispensed = Column(Boolean, default=False)
    taken = Column(Boolean, default=False)
    sensor_error = Column(Boolean, default=False)

    plan = relationship("MedicationPlan", back_populates="logs")