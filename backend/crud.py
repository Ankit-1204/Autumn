from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy.exc import IntegrityError

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
