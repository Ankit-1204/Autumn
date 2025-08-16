from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# tHE WORKflows are defined once, their instances are run at each trigger.
# response_model => to shape the response accordingly
@app.post("/workflows/", response_model=schemas.WorkflowRead)
def create_workflow(workflow: schemas.WorkflowCreate, db: Session = Depends(get_db)):
    return crud.create_workflow(db, workflow)

@app.get("/workflows/", response_model=list[schemas.WorkflowRead])
def list_workflows(db: Session = Depends(get_db)):
    return crud.get_workflows(db)

