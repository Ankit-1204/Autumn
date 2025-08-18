# backend/executor/delay_executor.py
from typing import Any, Dict
import time
import logging

logger = logging.getLogger(__name__)


def execute_delay_step(step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a delay step.

    Expected config: {"seconds": 2}
    """
    conf = step.get("config", {})
    seconds = float(conf.get("seconds", 1.0))
    seconds = max(0.0, seconds)
    logger.info("Delay for %s seconds", seconds)
    time.sleep(seconds)
    return {"status": "success", "output": {"slept": seconds}, "logs": f"Slept for {seconds} seconds"}
