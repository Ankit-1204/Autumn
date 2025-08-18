from celery_app import celery_app
from database import SessionLocal
import crud, models
import json
import traceback
import time
import logging
from typing import Any, Dict
from executor.http_executer import execute_http_step
from executor.delay_executer import execute_delay_step

logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)

EXECUTOR_REGISTRY = {
    "http_request": execute_http_step,
    "delay": execute_delay_step,
}
# thes decorator turns the function into a Celery Task.
# it can be called asynchronously nnow (RabbitMQ)
# bind allows it to bind to Celery task instance (use self)
def _execute_step_with_retries(step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a step with its retry/backoff config.
    Returns the final executor result dict.
    """
    retry_conf = step.get("retry", {}) or {}
    max_retries = int(retry_conf.get("count", 0))
    backoff = float(retry_conf.get("backoff", 2))  # multiplier seconds for exponential backoff
    attempt = 0
    last_exception = None

    while True:
        attempt += 1
        try:
            step_type = step.get("type")
            executor = EXECUTOR_REGISTRY.get(step_type)
            if executor is None:
                raise ValueError(f"Unknown step type: {step_type}")

            result = executor(step, context)
            status = result.get("status")
            if status == "success":
                return result
            else:
                # failed but maybe retry
                if attempt <= max_retries:
                    wait = backoff ** (attempt - 1)
                    logger.warning("Step %s failed, retrying in %s seconds (attempt %s/%s)", step.get("id"), wait, attempt, max_retries)
                    time.sleep(wait)
                    continue
                return result
        except Exception as exc:
            last_exception = exc
            logger.exception("Exception while executing step %s (attempt %s)", step.get("id"), attempt)
            if attempt <= max_retries:
                wait = backoff ** (attempt - 1)
                time.sleep(wait)
                continue
            # no retries left, create a failed-like result
            return {"status": "failed", "output": {"error": str(exc)}, "logs": f"Exception: {traceback.format_exc()}"}

@celery_app.task(bind=True,name="execute_workflow")
def execute_workflow(self, run_id: int) -> Dict[str, Any]:
    """
    Celery task that executes a workflow run using simple sequential step execution.
    """
    db = SessionLocal()
    try:
        run = db.get(models.WorkflowRun, run_id)
        if run is None:
            logger.error("Run id %s not found", run_id)
            return {"status": "not_found"}

        workflow = db.get(models.Workflow, run.workflow_id)
        if workflow is None:
            crud.update_run_status(db, run_id, "failed", logs="Workflow not found for run")
            return {"status": "failed", "reason": "workflow_not_found"}

        # parse definition
        try:
            definition = json.loads(workflow.definition)
        except Exception as e:
            msg = f"Failed to parse workflow definition: {e}"
            logger.exception(msg)
            crud.update_run_status(db, run_id, "failed", logs=msg)
            return {"status": "failed", "reason": "bad_definition"}

        steps = definition.get("steps")
        if not isinstance(steps, list):
            msg = "workflow.definition must contain 'steps' as a list"
            logger.error(msg)
            crud.update_run_status(db, run_id, "failed", logs=msg)
            return {"status": "failed", "reason": "bad_definition"}

        # mark running
        crud.update_run_status(db, run_id, "running", logs="Run started", append_logs=True)

        # execution context (can be expanded with inputs, secrets, outputs)
        context: Dict[str, Any] = {"run_id": run_id, "workflow_id": workflow.id}

        overall_logs = []
        for idx, step in enumerate(steps):
            step_id = step.get("id", f"step_{idx}")
            step_name = step.get("name", step_id)
            overall_logs.append(f"==> Starting step {step_name} (id={step_id})")
            result = _execute_step_with_retries(step, context)
            logs_piece = f"Step {step_name} result: {result.get('status')}"
            overall_logs.append(logs_piece)
            detail = result.get("logs")
            if detail:
                overall_logs.append(detail)
            crud.update_run_status(db, run_id, "running", logs="\n".join(overall_logs), append_logs=False)

            if result.get("status") != "success":
                err_msg = f"Step {step_name} failed, aborting run."
                overall_logs.append(err_msg)
                crud.update_run_status(db, run_id, "failed", logs="\n".join(overall_logs), append_logs=False)
                return {"status": "failed", "reason": f"step_failed:{step_id}"}

        # success
        overall_logs.append("Workflow execution finished successfully.")
        crud.update_run_status(db, run_id, "success", logs="\n".join(overall_logs), append_logs=False)
        return {"status": "success"}

    except Exception as exc:
        tb = traceback.format_exc()
        logger.exception("Unhandled exception during execute_workflow")
        try:
            crud.update_run_status(db, run_id, "failed", logs=tb, append_logs=False)
        except Exception:
            logger.exception("Failed to update run status after exception")
        raise
    finally:
        db.close()