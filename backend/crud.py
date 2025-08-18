from multiprocessing import synchronize
from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update
from sqlalchemy.sql import func
from typing import Any,Optional,List

def create_workflow(db: Session, workflow: schemas.WorkflowCreate):
    payload = workflow.model_dump()
    db_workflow = models.Workflow(**payload)
    db.add(db_workflow)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # re-raise a domain-specific error or return None; in FastAPI route raise HTTPException(409)
        raise
    db.refresh(db_workflow)
    return db_workflow

def get_workflows(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Workflow).offset(skip).limit(limit).all()

def get_workflow(db: Session, workflow_id: int):
    return db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()

def create_workflowRun(db: Session, workflow_id:int):
    run=models.WorkflowRun(workflow_id=workflow_id,status='pending')
    db.add(run)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # re-raise a domain-specific error or return None; in FastAPI route raise HTTPException(409)
        raise
    db.refresh(run)
    return run


def update_run_status(db: Session, run_id: int, status: str, logs: Optional[str] = None, append_logs: bool = False):
    """
    Update run status. If append_logs True, append 'logs' to existing logs.
    If status is 'success' or 'failed', completed_at is set to now().
    """
    # fetch current run to append logs if necessary
    run = db.get(models.WorkflowRun, run_id)
    if run is None:
        return

    new_logs = logs
    if append_logs and logs:
        existing = run.logs or ""
        if existing:
            new_logs = existing + "\n" + logs
        else:
            new_logs = logs

    values = {"status": status}
    if new_logs is not None:
        values["logs"] = new_logs
    if status in ("success", "failed"):
        values["completed_at"] = func.now()

    stmt = update(models.WorkflowRun).where(models.WorkflowRun.id == run_id).values(**values).execution_options(synchronize_session="fetch")
    db.execute(stmt)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # re-raise a domain-specific error or return None; in FastAPI route raise HTTPException(409)
        raise
    
