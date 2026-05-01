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
BASE_URL = "http://127.0.0.1:8013"
MUTABLE_ARTIFACT = Path("projects/reply/train.py")

IMPROVED_ARTIFACT = """from __future__ import annotations

import re


def draft_reply(example: dict[str, str]) -> str:
    language = example["language"]
    intent = example["intent"]
    incoming = _normalize(example["incoming"])

    precise_matches = [
        (
            language == "en"
            and intent == "business_decision"
            and _contains_all(incoming, "launch", "onboarding"),
            "I would delay by one week if onboarding is still shaky. "
            "A clean first experience matters more than an arbitrary date.",
        ),
        (
            language == "en"
            and intent == "neutral"
            and _contains_all(incoming, "review", "tonight"),
            "Perfect, thank you. Review it when you have time and send me your notes after.",
        ),
        (
            language == "en"
            and intent == "personal"
            and _contains_all(incoming, "overthinking", "yesterday"),
            "That is normal. Give it a little distance, then focus on what was actually said "
            "instead of replaying every possibility.",
        ),
        (
            language == "hu"
            and intent == "business_decision"
            and _contains_any(incoming, "felvegyunk", "varjunk"),
            "Én várnék egy hónapot, ha a feladatok még kezelhetők. "
            "Előbb legyen tiszta a prioritás és a terhelés.",
        ),
        (
            language == "hu"
            and intent == "neutral"
            and _contains_all(incoming, "fajlt", "este"),
            "Szuper, köszönöm. Nézd meg nyugodtan este, és utána egyeztessünk róla.",
        ),
        (
            language == "hu"
            and intent == "personal"
            and _contains_any(incoming, "tul sokat gondolkodom", "egeszen"),
            "Ez teljesen rendben van. Adj neki egy kis időt, és inkább a tényekre figyelj, "
            "ne az összes lehetséges forgatókönyvre.",
        ),
    ]

    for matched, reply in precise_matches:
        if matched:
            return reply

    if language == "hu":
        if intent == "business_decision":
            return "Én egy kicsit várnék, és előbb a prioritásokat tisztáznám."
        if intent == "personal":
            return "Ez rendben van, adj magadnak egy kis időt, és nézd meg nyugodtan a tényeket."
        return "Rendben, köszönöm. Nézd meg, és utána beszéljünk róla."

    if intent == "business_decision":
        return "I would wait a bit and make sure the priorities are clear first."
    if intent == "personal":
        return "That is normal. Give it a little time and focus on the facts."
    return "Perfect, thank you. Review it when you can and we will discuss it after."


def score_reply(candidate: str, gold_reply: str) -> float:
    candidate_tokens = _tokenize(candidate)
    gold_tokens = _tokenize(gold_reply)

    if not candidate_tokens or not gold_tokens:
        return 0.0

    overlap = len(candidate_tokens & gold_tokens)
    precision = overlap / len(candidate_tokens)
    recall = overlap / len(gold_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _tokenize(text: str) -> set[str]:
    normalized = re.sub(r"[^\\w\\s]", " ", text.lower(), flags=re.UNICODE)
    return {token for token in normalized.split() if token}


def _normalize(text: str) -> str:
    collapsed = re.sub(r"\\s+", " ", text.strip().lower(), flags=re.UNICODE)
    replacements = str.maketrans(
        {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ö": "o",
            "ő": "o",
            "ú": "u",
            "ü": "u",
            "ű": "u",
        }
    )
    return collapsed.translate(replacements)


def _contains_all(text: str, *needles: str) -> bool:
    return all(needle in text for needle in needles)


def _contains_any(text: str, *needles: str) -> bool:
    return any(needle in text for needle in needles)
"""


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


def apply_candidate_mutation(worktree_dir: Path) -> str:
    artifact_path = worktree_dir / MUTABLE_ARTIFACT
    artifact_path.write_text(IMPROVED_ARTIFACT, encoding="utf-8")
    return run_git(["git", "diff", "--", str(MUTABLE_ARTIFACT)], cwd=worktree_dir)


def main() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="train-reply-proof-"))
    worktree_dir = create_clean_worktree(temp_dir)
    database_url = f"sqlite:///{temp_dir / 'reply-proof.db'}"
    log_path = temp_dir / "api.log"
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    env["TRAIN_ENV"] = "local"
    env["APP_PORT"] = "8013"
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
            "8013",
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
                "project_key": "reply",
                "title": "Reply proof baseline",
                "budget_seconds": 60,
            },
        )
        baseline_id = baseline["id"]
        baseline_result = request("POST", f"/v1/runs/{baseline_id}/execute")
        baseline_ratchet = request("POST", f"/v1/runs/{baseline_id}/ratchet")
        if baseline_ratchet["ratchet_decision"] != "accepted":
            raise RuntimeError("Baseline reply proof run was not accepted")

        head_before_mutation = run_git(["git", "rev-parse", "HEAD"], cwd=worktree_dir)
        candidate_diff = apply_candidate_mutation(worktree_dir)
        pre_candidate_status = run_git(["git", "status", "--short"], cwd=worktree_dir).splitlines()

        candidate = request(
            "POST",
            "/v1/runs",
            {
                "project_key": "reply",
                "title": "Reply proof candidate",
                "budget_seconds": 60,
            },
        )
        candidate_id = candidate["id"]
        candidate_result = request("POST", f"/v1/runs/{candidate_id}/execute")
        candidate_ratchet = request("POST", f"/v1/runs/{candidate_id}/ratchet")
        if candidate_ratchet["ratchet_decision"] != "accepted":
            raise RuntimeError("Candidate reply proof run was not accepted")
        if candidate_ratchet["git_action"] != "committed":
            raise RuntimeError("Candidate reply proof run did not commit the mutable artifact")
        if candidate_result["metric_value"] <= baseline_result["metric_value"]:
            raise RuntimeError("Candidate reply proof run did not improve the benchmark score")

        project_states = request("GET", "/v1/project-states")
        changed_files = run_git(["git", "status", "--short"], cwd=worktree_dir).splitlines()
        head_after = run_git(["git", "rev-parse", "HEAD"], cwd=worktree_dir)
        committed_diff = ""
        if head_after != head_before_mutation:
            committed_diff = run_git(
                ["git", "diff", f"{head_before_mutation}..{head_after}", "--", str(MUTABLE_ARTIFACT)],
                cwd=worktree_dir,
            )

        summary = {
            "baseline": {
                "metric_value": baseline_result["metric_value"],
                "ratchet": baseline_ratchet["ratchet_decision"],
            },
            "candidate": {
                "metric_value": candidate_result["metric_value"],
                "ratchet": candidate_ratchet["ratchet_decision"],
                "git_action": candidate_ratchet["git_action"],
                "delta": round(candidate_result["metric_value"] - baseline_result["metric_value"], 6),
            },
            "project_states": project_states,
            "worktree": {
                "head_before_mutation": head_before_mutation,
                "head_after": head_after,
                "pre_candidate_status": pre_candidate_status,
                "changed_files_after_ratchet": changed_files,
                "candidate_diff": candidate_diff,
                "committed_diff": committed_diff,
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
