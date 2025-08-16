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
        
        crud.update_run_status(db, run_id, "running")

        try:
            definition = json.loads(workflow.definition)
        except Exception as e:
            msg = f"Failed to parse workflow definition: {e}"
            logger.exception(msg)
            crud.update_run_status(db, run_id, "failed", logs=msg)
            return {"status": "failed", "reason": "bad_definition"}
        
        logs = []
        steps = definition.get("steps", [])
        for idx, step in enumerate(steps):
            # For now we just log the step execution
            step_name = step.get("name", f"step_{idx}")
            logs.append(f"Executing {step_name}")
            # simulate potential error for demonstration (comment out in real runs)
            # if step.get("type") == "fail":
            #     raise RuntimeError("Step forced failure")

        logs.append("Workflow execution finished (simulated).")
        logs_text = "\n".join(logs)

        # 4. Mark success and write logs
        crud.update_run_status(db, run_id, "success", logs=logs_text)
        return {"status": "success"}
        
    except Exception as exc:
        # Any unexpected exceptions — mark run failed and capture stacktrace
        tb = traceback.format_exc()
        logger.exception("Unhandled exception during execute_workflow")
        try:
            crud.update_run_status(db, run_id, "failed", logs=tb)
        except Exception:
            logger.exception("Failed to update run status after exception")
        raise self.retry(exc=exc, countdown=5, max_retries=3)  # optional automatic retry

    finally:
        db.close()
