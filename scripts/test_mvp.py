from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:8000"


def request(method: str, path: str, payload: dict | None = None) -> dict | list:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_api() -> None:
    for _ in range(40):
        try:
            request("GET", "/health")
            return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("API did not become ready")


def main() -> None:
    server = subprocess.Popen(
        [
            "uv",
            "run",
            "uvicorn",
            "autotrain_api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_for_api()
        baseline = request(
            "POST",
            "/v1/runs",
            {
                "project_key": "mythology",
                "title": "MVP smoke baseline",
                "budget_seconds": 100,
            },
        )
        baseline_id = baseline["id"]
        baseline_result = request("POST", f"/v1/runs/{baseline_id}/execute")
        baseline_ratchet = request("POST", f"/v1/runs/{baseline_id}/ratchet")

        improved = request(
            "POST",
            "/v1/runs",
            {
                "project_key": "mythology",
                "title": "MVP smoke improved",
                "budget_seconds": 300,
            },
        )
        improved_id = improved["id"]
        improved_result = request("POST", f"/v1/runs/{improved_id}/execute")
        improved_ratchet = request("POST", f"/v1/runs/{improved_id}/ratchet")

        project_states = request("GET", "/v1/project-states")

        summary = {
            "baseline": {
                "execute": baseline_result["metric_value"],
                "ratchet": baseline_ratchet["ratchet_decision"],
            },
            "improved": {
                "execute": improved_result["metric_value"],
                "ratchet": improved_ratchet["ratchet_decision"],
            },
            "project_states": project_states,
        }
        print(json.dumps(summary, indent=2))
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()


if __name__ == "__main__":
    main()
