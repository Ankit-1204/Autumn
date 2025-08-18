from typing import Any, Dict, Protocol


class ExecutorResult(Dict):
    """
    Minimal structure returned by executors.
    Keys:
    -status: "success" or "failed"
       - output: arbitrary (e.g., HTTP response body)
      -logs: human-readable log text for this step
    """


class StepExecutor(Protocol):
    def execute(self, step: Dict[str, Any], context: Dict[str, Any]) -> ExecutorResult:
        ...
