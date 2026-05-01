from __future__ import annotations

import json
import subprocess
import tempfile
import time
import urllib.request
import os
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


def wait_for_api(*, log_path: Path | None = None) -> None:
    for _ in range(120):
        try:
            request("GET", "/health")
            return
        except Exception:
            time.sleep(0.25)
    log_tail = ""
    if log_path and log_path.exists():
        log_tail = log_path.read_text(encoding="utf-8", errors="replace")[-4000:]
    raise RuntimeError(f"API did not become ready\n\n{log_tail}".strip())


def create_clean_worktree(temp_dir: Path) -> Path:
    worktree_dir = temp_dir / "worktree"
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree_dir), "HEAD"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    rsync_command = [
        "rsync",
        "-a",
        "--delete",
        "--exclude",
        ".git",
        "--exclude",
        ".venv",
        "--exclude",
        "__pycache__",
        "--exclude",
        "*.pyc",
        "--exclude",
        ".pytest_cache",
        "--exclude",
        ".ruff_cache",
        "--exclude",
        "*.egg-info",
        "--exclude",
        "node_modules",
        "--exclude",
        ".next",
        "--exclude",
        "dist",
        "--exclude",
        "coverage",
        "--exclude",
        "artifacts",
        "--exclude",
        "logs",
        "--exclude",
        "*.sqlite3",
        "--exclude",
        "*.db",
        f"{ROOT}/",
        f"{worktree_dir}/",
    ]
    subprocess.run(
        rsync_command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(["git", "add", "-A"], cwd=worktree_dir, check=True, stdout=subprocess.DEVNULL)
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=worktree_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    if status.stdout.strip():
        subprocess.run(
            ["git", "commit", "-m", "test: snapshot current autotrain worktree"],
            cwd=worktree_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return worktree_dir


def main() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="autotrain-mvp-"))
    worktree_dir = create_clean_worktree(temp_dir)
    database_url = f"sqlite:///{temp_dir / 'mvp.db'}"
    log_path = temp_dir / "api.log"
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    env["AUTOTRAIN_ENV"] = "local"

    log_file = log_path.open("w", encoding="utf-8")
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
        cwd=worktree_dir,
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )

    try:
        wait_for_api(log_path=log_path)
        health = request("GET", "/health")
        projects = request("GET", "/v1/projects")
        agent_status = request("GET", "/v1/agents/mistral-vibe")

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
            "health": health,
            "projects": [project["key"] for project in projects],
            "agent": {
                "key": agent_status["key"],
                "available": agent_status["available"],
            },
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
        log_file.close()
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_dir)],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


if __name__ == "__main__":
    main()
