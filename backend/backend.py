from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload
import crud, models, schemas
from database import engine, get_db
from datetime import datetime
import yaml # HUSK AT INSTALLERE: pip install PyYAML

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World, Database is connected!"}

@app.get("/time")
def get_current_time():
    now = datetime.now()
    return {
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "weekday": now.weekday(),
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second
    }

@app.post("/patients/", response_model=schemas.PatientResponse, status_code=201)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    return crud.create_patient(db=db, patient=patient)

@app.get("/patients/", response_model=list[schemas.PatientResponse])
def read_patients(db: Session = Depends(get_db)):
    return crud.get_patients(db=db)

@app.post("/plans/", response_model=schemas.MedicationPlanResponse, status_code=201)
def create_plan(plan: schemas.MedicationPlanCreate, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=plan.patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.create_plan(db=db, plan=plan)

@app.post("/dispenser/log/", response_model=schemas.MedicationLogResponse, status_code=201)
def dispenser_log(log_data: schemas.DispenserLogCreate, db: Session = Depends(get_db)):
    db_plan = db.query(models.MedicationPlan).filter(models.MedicationPlan.id == log_data.plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Medication plan not found")

    return crud.create_medication_log(db=db, log_data=log_data)

@app.get("/dispenser/config/{patient_id}", response_model=schemas.ESP32ConfigResponse)
def get_dispenser_config(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return crud.get_patient_config(db, patient_id)

@app.get("/stats/{patient_id}")
def get_patient_stats(patient_id: int, db: Session = Depends(get_db)):
    logs = db.query(models.MedicationLog).options(joinedload(models.MedicationLog.plan)).join(models.MedicationPlan).filter(models.MedicationPlan.patient_id == patient_id).all()
    
    total_dispensed = 0
    total_taken = 0
    sensor_errors = 0
    
    log_data = []
    
    for log in logs:
        medication_name = log.plan.medication_name if log.plan else "Ukendt"

        if log.dispensed:
            total_dispensed += 1
        if log.taken:
            total_taken += 1
        if log.sensor_error:
            sensor_errors += 1
            
        log_data.append({
            "timestamp": log.timestamp.isoformat(),
            "medication": medication_name,
            "dispensed": log.dispensed,
            "taken": log.taken,
            "error": log.sensor_error
        })

    compliance = 0
    if total_dispensed > 0:
        compliance = round((total_taken / total_dispensed) * 100, 1)

    return {
        "patient_id": patient_id,
        "compliance_percentage": compliance,
        "total_dispensed": total_dispensed,
        "total_taken": total_taken,
        "sensor_errors": sensor_errors,
        "logs": log_data
    }

@app.get("/export/yaml")
def export_data_as_yaml(db: Session = Depends(get_db)):
    patients = crud.get_patients(db)
    
    export_data = {"patients": []}
    
    for p in patients:
        p_data = {
            "id": p.id,
            "name": p.name,
            "dob": str(p.dob),
            "plans": []
        }
        for plan in p.plans:
            plan_data = {
                "id": plan.id,
                "medication": plan.medication_name,
                "dosage": plan.dosage,
                "time": str(plan.schedule_time)
            }
            p_data["plans"].append(plan_data)
            
        export_data["patients"].append(p_data)

    yaml_content = yaml.dump(export_data, sort_keys=False, allow_unicode=True)
    
    return Response(content=yaml_content, media_type="application/x-yaml", headers={"Content-Disposition": "attachment; filename=backup.yaml"})
