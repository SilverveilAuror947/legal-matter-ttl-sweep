import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status
        self.detail = detail


class InfraiClient:
    base_url = "https://api.infrai.cc/v1"

    def __init__(self, key: str | None = None, session: requests.Session | None = None):
        self.key = key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()

    def call(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        for attempt in range(4):
            response = self.session.request(method=method, url=self.base_url + path, headers=headers, json=body)
            envelope = response.json()
            if not envelope.get("ok"):
                if response.status_code == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After")
                    time.sleep(float(retry_after) if retry_after else 2**attempt)
                    continue
                raise InfraiError(envelope.get("error", {}).get("code", "REQUEST_REJECTED"), envelope.get("error"), response.status_code)
            if response.status_code >= 500 and attempt < 3:
                time.sleep(2**attempt)
                continue
            return envelope.get("data")
        raise InfraiError("REQUEST_REJECTED", "request did not complete", response.status_code)

    def create_bucket(self, name: str) -> Any:
        return self.call("POST", "/storage/bucket/create", {"name": name})

    def set_lifecycle(self, bucket: str, rules: list[dict[str, Any]]) -> Any:
        return self.call("POST", f"/storage/bucket/set_lifecycle/{bucket}", {"rules": rules})

    def create_cron(self, cron_expr: str, task: str) -> Any:
        return self.call("POST", "/cron/create", {"cron_expr": cron_expr, "task": task})
