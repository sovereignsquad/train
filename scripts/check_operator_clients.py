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
BASE_URL = "http://127.0.0.1:8016"


def request(method: str, path: str) -> dict | list:
    req = urllib.request.Request(f"{BASE_URL}{path}", method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed with {exc.code}: {body}") from exc


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
            ["git", "commit", "-m", "test: snapshot current train worktree"],
            cwd=worktree_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return worktree_dir


def require_keys(payload: dict[str, object], keys: tuple[str, ...], *, context: str) -> None:
    missing = [key for key in keys if key not in payload]
    if missing:
        raise RuntimeError(f"{context} is missing required keys: {', '.join(missing)}")


def main() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="train-operator-smoke-"))
    worktree_dir = create_clean_worktree(temp_dir)
    database_url = f"sqlite:///{temp_dir / 'operator-smoke.db'}"
    log_path = temp_dir / "api.log"
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    env["TRAIN_ENV"] = "local"
    env["APP_PORT"] = "8016"
    env.pop("VIRTUAL_ENV", None)

    log_file = log_path.open("w", encoding="utf-8")
    server = subprocess.Popen(
        [
            "uv",
            "run",
            "uvicorn",
            "train_api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8016",
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
        runs = request("GET", "/v1/runs")
        project_states = request("GET", "/v1/project-states")
        agent_status = request("GET", "/v1/agents/mistral-vibe")
        mistral_provider = request("GET", "/v1/providers/mistral-api")
        ollama_provider = request("GET", "/v1/providers/ollama")
        operator_status = request("GET", "/v1/operator/status")

        require_keys(health, ("status", "service", "environment"), context="/health")
        require_keys(agent_status, ("key", "name", "available", "issues"), context="/v1/agents/mistral-vibe")
        require_keys(mistral_provider, ("key", "base_url", "configured", "reachable", "issues"), context="/v1/providers/mistral-api")
        require_keys(ollama_provider, ("key", "base_url", "configured", "reachable", "issues"), context="/v1/providers/ollama")
        require_keys(operator_status, ("generated_at", "total_runs", "running_runs", "stalled_runs", "recoverable_runs"), context="/v1/operator/status")
        if not isinstance(projects, list) or not isinstance(runs, list) or not isinstance(project_states, list):
            raise RuntimeError("Project, run, and project-state endpoints must return arrays.")

        summary = {
            "health": health,
            "project_count": len(projects),
            "run_count": len(runs),
            "project_state_count": len(project_states),
            "agent_status": {
                "key": agent_status["key"],
                "available": agent_status["available"],
            },
            "providers": {
                "mistral-api": {
                    "configured": mistral_provider["configured"],
                    "reachable": mistral_provider["reachable"],
                },
                "ollama": {
                    "configured": ollama_provider["configured"],
                    "reachable": ollama_provider["reachable"],
                },
            },
            "operator_status": {
                "total_runs": operator_status["total_runs"],
                "stalled_runs": operator_status["stalled_runs"],
            },
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
