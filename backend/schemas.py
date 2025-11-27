from pydantic import BaseModel
from datetime import date, time

#Input Schema for Medication Plan
class MedicationPlanCreate(BaseModel):
    patient_id: int
    medication_name: str
    dosage: str
    schedule_time: time

#Output Schema for Medication Plan (inkl. ID)
class MedicationPlanResponse(MedicationPlanCreate):
    id: int

    class Config:
        from_attributes = True

#Input Schema for Patient
class PatientCreate(BaseModel):
    name: str
    dob: date

#Output Schema for Patient (inkl. ID og planer)
class PatientResponse(PatientCreate):
    id: int
    plans: list[MedicationPlanResponse] = []

    class Config:
        from_attributes = True