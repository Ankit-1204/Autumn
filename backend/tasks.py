from .celery_app import celery_app
from .database import SessionLocal
from . import crud, models
import json
import traceback
import logging
from typing import Any

logger=logging.getLogger(__name__)

# the decorator turns the function into a Celery Task.
# it can be called asynchronously nnow (RabbitMQ)
# bind allows it to bind to Celery task instance (use self)
@celery_app.task(bind=True,name="execute_workflow")
def execute_workflow(self,run_id:int)->dict[str,Any]:

    db = SessionLocal()

    try:
        run = db.get(models.WorkflowRun, run_id)
        if run is None:
            logger.error("Run id %s not found", run_id)
            return {"status": "not_found"}
        workflow=db.get(models.Workflow,run.workflow_id)
        if workflow is None:
            crud.update_run_status(db, run_id, "failed", logs="Workflow not found for run")
            return {"status": "failed", "reason": "workflow_not_found"}
    except:
