from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:8012"


def request(method: str, path: str, payload: dict | None = None) -> dict | list:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed with {exc.code}: {body}") from exc


def wait_for_api(*, log_path: Path | None = None) -> None:
    for _ in range(160):
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
    temp_dir = Path(tempfile.mkdtemp(prefix="autotrain-second-proof-"))
    worktree_dir = create_clean_worktree(temp_dir)
    database_url = f"sqlite:///{temp_dir / 'second-proof.db'}"
    log_path = temp_dir / "api.log"
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    env["AUTOTRAIN_ENV"] = "local"
    env["APP_PORT"] = "8012"
    env.pop("VIRTUAL_ENV", None)

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
            "8012",
        ],
        cwd=worktree_dir,
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )

    try:
        wait_for_api(log_path=log_path)
        projects = request("GET", "/v1/projects")
        provider = request("GET", "/v1/providers/ollama")
        created = request(
            "POST",
            "/v1/runs",
            {
                "project_key": "helpdesk",
                "title": "Second proof baseline",
                "budget_seconds": 60,
            },
        )
        run_id = created["id"]
        executed = request("POST", f"/v1/runs/{run_id}/execute")
        ratcheted = request("POST", f"/v1/runs/{run_id}/ratchet")
        states = request("GET", "/v1/project-states")

        summary = {
            "projects": [project["key"] for project in projects],
            "provider": {
                "key": provider["key"],
                "reachable": provider["reachable"],
                "model_count": provider["model_count"],
            },
            "helpdesk": {
                "metric_name": executed["metric_name"],
                "metric_direction": executed["metric_direction"],
                "metric_value": executed["metric_value"],
                "ratchet": ratcheted["ratchet_decision"],
            },
            "project_states": states,
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
