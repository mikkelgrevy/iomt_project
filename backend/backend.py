from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import crud, models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World, Database is connected!"}

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