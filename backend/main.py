from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import models, schemas,crud
from db.database import SessionLocal, engine
from celery_app import celery_app
import logging
from notifications import router as notifications_router
from auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)
app = FastAPI(title="Autumn")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(notifications_router)
app.include_router(auth_router)

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

@app.post("/workflows/{workflow_id}/runs",response_model=schemas.WorkflowRunRead,status_code=status.HTTP_201_CREATED)
def start_run(workflow_id:int,payload: schemas.WorkflowRunCreate = None,db: Session = Depends(get_db)):
    workflow=crud.get_workflow(db,workflow_id);
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    run=crud.create_workflowRun(db,workflow_id)
    celery_app.send_task("execute_workflow",args=(run.id,),kwargs={})

    logger.info("Enqueued execute_workflow for run_id=%s", run.id)

    return run

@app.get("/workflows/{workflow_id}/runs/{run_id}", response_model=schemas.WorkflowRunRead)
def get_run(workflow_id: int, run_id: int, db: Session = Depends(get_db)):
    run = db.get(models.WorkflowRun, run_id)
    if not run or run.workflow_id != workflow_id:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


