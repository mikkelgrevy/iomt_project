from pydantic import BaseModel
from datetime import date, time, datetime

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

  #Input fra dispenseren om log status
class DispenserLogCreate(BaseModel):
    plan_id: int
    dispensed: bool = False
    taken: bool = False
    sensor_error: bool = False

  #Output for log (hvis vi vil returnere den oprettede log)
class MedicationLogResponse(DispenserLogCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

  #NYE SCHEMAS TIL ESP32 CONFIG
class ESP32PlanItem(BaseModel):
    plan_id: int
    hour: int
    minute: int
    dosage: str

class ESP32ConfigResponse(BaseModel):
    patient_id: int
    plans: list[ESP32PlanItem]