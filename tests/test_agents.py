from train_core.agents import AgentMode, build_agent_launch_plan, get_agent_status
from train_core.config import ROOT_DIR


def test_plan_launch_is_interactive() -> None:
    plan = build_agent_launch_plan(
        adapter_key="mistral-vibe",
        project_key="mythology",
        mode=AgentMode.PLAN,
    )

    assert plan.mode is AgentMode.PLAN
    assert plan.command[:5] == ["vibe", "--workdir", str(ROOT_DIR), "--trust", "--agent"]
    assert "--prompt" not in plan.command
    assert "Stay in planning mode only." in plan.prompt


def test_auto_launch_uses_programmatic_prompt() -> None:
    plan = build_agent_launch_plan(
        adapter_key="mistral-vibe",
        project_key="mythology",
        mode="auto",
        max_turns=4,
    )

    assert plan.mode is AgentMode.AUTO
    assert "--prompt" in plan.command
    assert plan.command[-2:] == ["--max-turns", "4"]
    assert "Do not stop to ask for confirmation once execution begins." in plan.prompt


def test_vibe_status_uses_repo_local_contract_files() -> None:
    status = get_agent_status("mistral-vibe")

    assert status.key == "mistral-vibe"
    assert status.contract_home.endswith("/.vibe")
    assert status.runtime_home.endswith("/artifacts/local/vibe-home")
    assert status.config_path.endswith("/.vibe/config.toml")
    assert status.agent_config_path.endswith("/.vibe/agents/train.toml")
    assert status.prompt_path.endswith("/.vibe/prompts/train.md")
