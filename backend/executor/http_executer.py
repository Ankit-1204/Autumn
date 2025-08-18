from typing import Any,Dict
import requests
import logging

logger = logging.getLogger(__name__)

# backend/executor/http_executor.py
from typing import Any, Dict
import requests
import logging

logger = logging.getLogger(__name__)


def execute_http_step(step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute an http_request step.

    Expected step shape:
    {
        "id": "s1",
        "type": "http_request",
        "name": "call_example",
        "config": {
            "method": "GET",
            "url": "https://httpbin.org/get",
            "headers": {"Accept": "application/json"},
            "json": {"foo": "bar"},
            "params": {"q": "x"},
            "timeout": 5
        }
    }
    """
    conf = step.get("config", {})
    method = (conf.get("method") or "GET").upper()
    url = conf.get("url")
    if not url:
        raise ValueError("http_request step requires config.url")

    timeout = conf.get("timeout", 10)
    headers = conf.get("headers")
    params = conf.get("params")
    json_body = conf.get("json")
    data = conf.get("data")

    try:
        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_body,
            data=data,
            timeout=timeout,
        )
        content_type = resp.headers.get("Content-Type", "")
        try:
            if "application/json" in content_type:
                body = resp.json()
            else:
                body = resp.text[:4000]  # truncate to 4k chars
        except Exception:
            body = resp.text[:4000]

        logs = f"HTTP {method} {url} -> status {resp.status_code}"
        if resp.status_code >= 400:
            return {"status": "failed", "output": {"status_code": resp.status_code, "body": body}, "logs": logs}
        return {"status": "success", "output": {"status_code": resp.status_code, "body": body}, "logs": logs}
    except requests.RequestException as exc:
        logger.exception("HTTP request failed: %s", exc)
        return {"status": "failed", "output": {"error": str(exc)}, "logs": f"HTTP request failed: {exc}"}
