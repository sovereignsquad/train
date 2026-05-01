from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

from autotrain_core.config import settings
from autotrain_core.agents import (
    AgentMode,
    build_agent_launch_plan,
    get_agent_status,
    prepare_vibe_runtime_home,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the canonical Mistral Vibe flow for autotrain.")
    parser.add_argument("--project-key", default="mythology")
    parser.add_argument("--mode", choices=[mode.value for mode in AgentMode], default=AgentMode.PLAN.value)
    parser.add_argument("--objective")
    parser.add_argument("--max-turns", type=int)
    parser.add_argument("--print-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status = get_agent_status("mistral-vibe")
    plan = build_agent_launch_plan(
        adapter_key="mistral-vibe",
        project_key=args.project_key,
        mode=args.mode,
        objective=args.objective,
        max_turns=args.max_turns,
    )

    payload = {
        "status": {
            "available": status.available,
            "resolved_executable": status.resolved_executable,
            "version": status.version,
            "mistral_api_key_configured": status.mistral_api_key_configured,
            "issues": status.issues,
        },
        "plan": {
            "mode": plan.mode.value,
            "command": plan.command,
            "prompt": plan.prompt,
            "environment": plan.environment,
            "summary": plan.summary,
        },
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Mode: {plan.mode.value}")
        print(f"Command: {' '.join(plan.command)}")
        print(f"VIBE_CONTRACT_HOME={status.contract_home}")
        print(f"VIBE_HOME={plan.environment['VIBE_HOME']}")
        print("Prompt:")
        print(plan.prompt)
        if status.issues:
            print("Issues:")
            for issue in status.issues:
                print(f"- {issue}")

    if args.print_only:
        return 0

    if not status.available:
        print("Vibe is not installed. Install it with: uv tool install mistral-vibe", file=sys.stderr)
        return 1
    if not status.mistral_api_key_configured:
        print("MISTRAL_API_KEY is not configured for the current process.", file=sys.stderr)
        return 1

    env = os.environ.copy()
    prepare_vibe_runtime_home()
    env.update(plan.environment)
    if settings.mistral_api_key:
        env.setdefault("MISTRAL_API_KEY", settings.mistral_api_key)
    completed = subprocess.run(plan.command, cwd=plan.workdir, env=env, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
