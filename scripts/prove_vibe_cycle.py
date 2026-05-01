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
BASE_URL = "http://127.0.0.1:8011"


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
            ["git", "commit", "-m", "test: snapshot current train worktree"],
            cwd=worktree_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return worktree_dir


def run_git(args: list[str], *, cwd: Path) -> str:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def main() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="train-proof-"))
    worktree_dir = create_clean_worktree(temp_dir)
    database_url = f"sqlite:///{temp_dir / 'proof.db'}"
    log_path = temp_dir / "api.log"
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    env["TRAIN_ENV"] = "local"
    env["APP_PORT"] = "8011"
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
            "8011",
        ],
        cwd=worktree_dir,
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )

    try:
        wait_for_api(log_path=log_path)
        baseline = request(
            "POST",
            "/v1/runs",
            {
                "project_key": "mythology",
                "title": "Proof baseline",
                "budget_seconds": 300,
            },
        )
        baseline_id = baseline["id"]
        baseline_result = request("POST", f"/v1/runs/{baseline_id}/execute")
        baseline_ratchet = request("POST", f"/v1/runs/{baseline_id}/ratchet")
        head_before_vibe = run_git(["git", "rev-parse", "HEAD"], cwd=worktree_dir)

        vibe_command = [
            "uv",
            "run",
            "python",
            "scripts/run_vibe.py",
            "--project-key",
            "mythology",
            "--mode",
            "auto",
            "--max-turns",
            "6",
            "--objective",
            (
                "Run exactly one small experiment against the mythology benchmark. "
                "Only modify projects/mythology/train.py. Prefer a single simple change "
                "that might lower val_bpb, validate it locally, and then stop."
            ),
        ]
        vibe_completed = subprocess.run(
            vibe_command,
            cwd=worktree_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )
        pre_candidate_status = run_git(["git", "status", "--short"], cwd=worktree_dir).splitlines()
        pre_candidate_train_diff = run_git(
            ["git", "diff", "--", "projects/mythology/train.py"],
            cwd=worktree_dir,
        )

        candidate = request(
            "POST",
            "/v1/runs",
            {
                "project_key": "mythology",
                "title": "Proof candidate",
                "budget_seconds": 300,
            },
        )
        candidate_id = candidate["id"]
        candidate_result = request("POST", f"/v1/runs/{candidate_id}/execute")
        candidate_ratchet = request("POST", f"/v1/runs/{candidate_id}/ratchet")
        project_states = request("GET", "/v1/project-states")

        changed_files = run_git(["git", "status", "--short"], cwd=worktree_dir).splitlines()
        head_after = run_git(["git", "rev-parse", "HEAD"], cwd=worktree_dir)
        committed_train_diff = ""
        if head_after != head_before_vibe:
            committed_train_diff = run_git(
                ["git", "diff", f"{head_before_vibe}..{head_after}", "--", "projects/mythology/train.py"],
                cwd=worktree_dir,
            )

        summary = {
            "baseline": {
                "metric_value": baseline_result["metric_value"],
                "ratchet": baseline_ratchet["ratchet_decision"],
            },
            "vibe": {
                "returncode": vibe_completed.returncode,
                "stdout_tail": vibe_completed.stdout.strip().splitlines()[-20:],
                "stderr_tail": vibe_completed.stderr.strip().splitlines()[-20:],
            },
            "candidate": {
                "metric_value": candidate_result["metric_value"],
                "ratchet": candidate_ratchet["ratchet_decision"],
                "git_action": candidate_ratchet["git_action"],
            },
            "project_states": project_states,
            "worktree": {
                "head_before_vibe": head_before_vibe,
                "head_after": head_after,
                "pre_candidate_status": pre_candidate_status,
                "pre_candidate_train_diff": pre_candidate_train_diff,
                "changed_files": changed_files,
                "committed_train_diff": committed_train_diff,
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
