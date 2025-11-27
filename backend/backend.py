from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
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