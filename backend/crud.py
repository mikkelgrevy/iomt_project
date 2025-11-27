from sqlalchemy.orm import Session
import models, schemas

def get_patient(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patients(db: Session):
    return db.query(models.Patient).all()

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(name=patient.name, dob=patient.dob)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def create_plan(db: Session, plan: schemas.MedicationPlanCreate):
    db_plan = models.MedicationPlan(
        patient_id=plan.patient_id,
        medication_name=plan.medication_name,
        dosage=plan.dosage,
        schedule_time=plan.schedule_time
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan