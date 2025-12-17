from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import datetime, date
import models, schemas

def get_patient(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patients(db: Session):
    return db.query(models.Patient).options(joinedload(models.Patient.plans)).all()

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(name=patient.name, dob=patient.dob)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def create_plan(db: Session, plan: schemas.MedicationPlanCreate):
    existing_plan = db.query(models.MedicationPlan).filter(models.MedicationPlan.patient_id == plan.patient_id).first()
    
    if existing_plan:
        existing_plan.medication_name = plan.medication_name
        existing_plan.dosage = plan.dosage
        existing_plan.schedule_time = plan.schedule_time
        db.commit()
        db.refresh(existing_plan)
        return existing_plan
    else:
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

def create_medication_log(db: Session, log_data: schemas.DispenserLogCreate):
    today = date.today()
    existing_log = db.query(models.MedicationLog).filter(
        and_(
            models.MedicationLog.plan_id == log_data.plan_id,
            models.MedicationLog.timestamp >= datetime.combine(today, datetime.min.time()),
            models.MedicationLog.timestamp <= datetime.combine(today, datetime.max.time()),
        )
    ).first()

    if existing_log:
        existing_log.dispensed = log_data.dispensed or existing_log.dispensed
        existing_log.taken = log_data.taken or existing_log.taken
        existing_log.sensor_error = log_data.sensor_error or existing_log.sensor_error
        existing_log.timestamp = datetime.utcnow()
        db.commit()
        db.refresh(existing_log)
        return existing_log
    else:
        db_log = models.MedicationLog(
            plan_id=log_data.plan_id,
            dispensed=log_data.dispensed,
            taken=log_data.taken,
            sensor_error=log_data.sensor_error,
            timestamp=datetime.utcnow()
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

def get_patient_config(db: Session, patient_id: int):
    plans = db.query(models.MedicationPlan).filter(models.MedicationPlan.patient_id == patient_id).all()

    config_items = []
    for plan in plans:
        item = schemas.ESP32PlanItem(
            plan_id=plan.id,
            hour=plan.schedule_time.hour,
            minute=plan.schedule_time.minute,
            dosage=plan.dosage
        )
        config_items.append(item)

    return schemas.ESP32ConfigResponse(
        patient_id=patient_id,
        plans=config_items
    )

def get_patient_logs(db: Session, patient_id: int):
    return db.query(models.MedicationLog).join(models.MedicationPlan).filter(models.MedicationPlan.patient_id == patient_id).all()