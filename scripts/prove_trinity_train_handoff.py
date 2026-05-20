from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
TRINITY_ROOT = ROOT.parent / "trinity"
BASE_URL = "http://127.0.0.1:8015"


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


def main() -> None:
    if not TRINITY_ROOT.exists():
        raise RuntimeError(f"Expected local Trinity checkout at {TRINITY_ROOT}")

    temp_dir = Path(tempfile.mkdtemp(prefix="train-trinity-proof-"))
    worktree_dir = create_clean_worktree(temp_dir)
    database_url = f"sqlite:///{temp_dir / 'proof.db'}"
    log_path = temp_dir / "api.log"
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    env["TRAIN_ENV"] = "local"
    env["APP_PORT"] = "8015"
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
            "8015",
        ],
        cwd=worktree_dir,
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )

    try:
        wait_for_api(log_path=log_path)

        sys.path.insert(0, str(TRINITY_ROOT / "core"))
        from trinity_core.ops.train_client import propose_reply_policy_via_train_api
        from trinity_core.ops.cycle_store import RuntimeCyclePaths, RuntimeCycleStore
        from trinity_core.reply_runtime import ReplyRuntime
        from trinity_core.schemas import (
            DraftOutcomeDisposition,
            DraftOutcomeEvent,
            ThreadMessageRole,
            ThreadMessageSnapshot,
            ThreadSnapshot,
            TrainingBundleType,
        )

        runtime_root = temp_dir / "trinity-runtime"
        runtime = ReplyRuntime(
            store=RuntimeCycleStore(
                RuntimeCyclePaths(
                    adapter_name="reply",
                    root_dir=runtime_root,
                    cycles_dir=runtime_root / "cycles",
                    exports_dir=runtime_root / "exports",
                )
            )
        )
        runtime.store.paths.cycles_dir.mkdir(parents=True, exist_ok=True)
        runtime.store.paths.exports_dir.mkdir(parents=True, exist_ok=True)

        snapshot = ThreadSnapshot(
            company_id=uuid4(),
            thread_ref="reply:linkedin:alice",
            channel="linkedin",
            contact_handle="linkedin://alice",
            latest_inbound_text="Can you send the updated numbers today?",
            requested_at=datetime(2026, 5, 1, 12, 0, tzinfo=UTC),
            messages=(
                ThreadMessageSnapshot(
                    message_id="msg-1",
                    role=ThreadMessageRole.CONTACT,
                    text="Can you send the updated numbers today?",
                    occurred_at=datetime(2026, 5, 1, 11, 59, tzinfo=UTC),
                    channel="linkedin",
                    source="linkedin",
                    handle="linkedin://alice",
                ),
            ),
        )
        ranked = runtime.suggest(snapshot)
        runtime.record_outcome(
            DraftOutcomeEvent(
                company_id=snapshot.company_id,
                cycle_id=ranked.cycle_id,
                thread_ref=snapshot.thread_ref,
                channel=snapshot.channel,
                candidate_id=ranked.drafts[0].candidate_id,
                disposition=DraftOutcomeDisposition.SENT_AS_IS,
                occurred_at=datetime(2026, 5, 1, 12, 1, tzinfo=UTC),
                original_draft_text=ranked.drafts[0].draft_text,
                final_text=ranked.drafts[0].draft_text,
                edit_distance=0.0,
                latency_ms=1000,
                send_result="ok",
            )
        )
        exported = runtime.export_training_bundle(
            ranked.cycle_id,
            bundle_type=TrainingBundleType.TONE_LEARNING,
        )

        proposal_path = temp_dir / "proposal.json"
        eval_path = temp_dir / "eval.json"
        train_result = propose_reply_policy_via_train_api(
            learner_kind="tone",
            bundle_files=[exported["bundle_path"]],
            train_api_base_url=BASE_URL,
            proposal_output_path=proposal_path,
            eval_output_path=eval_path,
        )

        summary = {
            "health": request("GET", "/health"),
            "trinity_bundle_path": exported["bundle_path"],
            "trinity_bundle_exists": Path(exported["bundle_path"]).exists(),
            "train_result": train_result,
            "proposal_path": str(proposal_path),
            "proposal_exists": proposal_path.exists(),
            "eval_path": str(eval_path),
            "eval_exists": eval_path.exists(),
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
