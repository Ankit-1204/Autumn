from celery_app import celery_app
from db.database import SessionLocal
from db import models,crud
import json
import traceback
import time
import logging
from settings import settings
from typing import Any, Dict
from executor.http_executer import execute_http_step
from executor.delay_executer import execute_delay_step
import redis

logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
EXECUTOR_REGISTRY = {
    "http_request": execute_http_step,
    "delay": execute_delay_step,
}


def publish_event(run_id: int, payload: Dict[str, Any]):
    """
    Publish a JSON payload to the run channel so websocket subscribers can receive it.
    """
    channel = f"run:{run_id}"
    try:
        redis_client.publish(channel, json.dumps(payload))
    except Exception as exc:
        logger.exception("Failed to publish run event to redis: %s", exc)


# thes decorator turns the function into a Celery Task.
# it can be called asynchronously nnow (RabbitMQ)
# bind allows it to bind to Celery task instance (use self)
def _execute_step_with_retries_and_record(db, run_id: int, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a StepInstance, execute step with retries, update StepInstance and publish updates.
    """
    step_id = step.get("id", f"step_{int(time.time()*1000)}")
    step_name = step.get("name")
    # create DB record
    si = crud.create_step_instance(db, run_id, step_id, step_name)
    publish_event(run_id, {"type": "step.created", "step_instance": {"id": si.id, "step_id": si.step_id, "name": si.name}})

    retry_conf = step.get("retry", {}) or {}
    max_retries = int(retry_conf.get("count", 0))
    backoff = float(retry_conf.get("backoff", 2))
    attempt = 0

    while True:
        attempt += 1
        crud.update_step_instance(db, si.id, status="running", logs=f"Attempt {attempt}")
        publish_event(run_id, {"type": "step.started", "step_instance": {"id": si.id, "attempt": attempt}})

        try:
            step_type = step.get("type")
            executor = EXECUTOR_REGISTRY.get(step_type)
            if executor is None:
                raise ValueError(f"Unknown step type: {step_type}")

            result = executor(step, context)
            status = result.get("status")
            logs = result.get("logs")
            output = result.get("output")

            crud.update_step_instance(db, si.id, status=status, logs=logs or "", output=output)
            publish_event(run_id, {"type": "step.finished", "step_instance": {"id": si.id, "status": status, "output": output, "logs": logs}})
            if status == "success":
                return result
            # failed
            if attempt <= max_retries:
                wait = backoff ** (attempt - 1)
                crud.update_step_instance(db, si.id, logs=f"Retrying in {wait}s (attempt {attempt}/{max_retries})")
                publish_event(run_id, {"type": "step.retrying", "step_instance": {"id": si.id, "attempt": attempt, "wait": wait}})
                time.sleep(wait)
                continue
            return result

        except Exception as exc:
            tb = traceback.format_exc()
            logger.exception("Exception while executing step %s", step_id)
            crud.update_step_instance(db, si.id, status="failed", logs=tb)
            publish_event(run_id, {"type": "step.error", "step_instance": {"id": si.id, "error": str(exc), "trace": tb}})
            if attempt <= max_retries:
                wait = backoff ** (attempt - 1)
                time.sleep(wait)
                continue
            return {"status": "failed", "output": {"error": str(exc)}, "logs": tb}

@celery_app.task(bind=True,name="execute_workflow")
def execute_workflow(self, run_id: int) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        run = db.get(models.WorkflowRun, run_id)
        if run is None:
            logger.error("Run id %s not found", run_id)
            return {"status": "not_found"}
        workflow = db.get(models.Workflow, run.workflow_id)
        if workflow is None:
            crud.update_run_status(db, run_id, "failed", logs="Workflow not found for run")
            publish_event(run_id, {"type":"run.failed", "reason":"workflow_not_found"})
            return {"status": "failed"}

        try:
            definition = json.loads(workflow.definition)
        except Exception as e:
            msg = f"Failed to parse workflow definition: {e}"
            crud.update_run_status(db, run_id, "failed", logs=msg)
            publish_event(run_id, {"type":"run.failed", "reason":"bad_definition", "message":str(e)})
            return {"status": "failed"}

        steps = definition.get("steps", [])
        crud.update_run_status(db, run_id, "running", logs="Run started", append_logs=False)
        publish_event(run_id, {"type":"run.started", "run_id": run_id})

        context: Dict[str, Any] = {"run_id": run_id, "workflow_id": workflow.id}

        for step in steps:
            publish_event(run_id, {"type":"step.queueing", "step": {"id": step.get("id"), "name": step.get("name")}})
            result = _execute_step_with_retries_and_record(db, run_id, step, context)
            if result.get("status") != "success":
                crud.update_run_status(db, run_id, "failed", logs=f"Step {step.get('id')} failed", append_logs=True)
                publish_event(run_id, {"type":"run.failed", "run_id": run_id, "reason": f"step_failed:{step.get('id')}"})
                return {"status": "failed"}

        crud.update_run_status(db, run_id, "success", logs="Workflow finished successfully", append_logs=False)
        publish_event(run_id, {"type":"run.finished", "run_id": run_id, "status":"success"})
        return {"status": "success"}

    except Exception:
        tb = traceback.format_exc()
        logger.exception("Unhandled exception during execute_workflow")
        try:
            crud.update_run_status(db, run_id, "failed", logs=tb, append_logs=False)
            publish_event(run_id, {"type":"run.failed", "run_id": run_id, "error": tb})
        except Exception:
            logger.exception("Failed to update run status after exception")
        raise
    finally:
        db.close()