from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
import shutil
import subprocess

from autotrain_core.config import ROOT_DIR, settings
from autotrain_core.projects import get_project, get_project_root


class AgentMode(StrEnum):
    PLAN = "plan"
    AUTO = "auto"


@dataclass(frozen=True)
class AgentAdapterDefinition:
    key: str
    name: str
    description: str
    executable: str
    first_class: bool


@dataclass(frozen=True)
class AgentAdapterStatus:
    key: str
    name: str
    available: bool
    executable: str
    resolved_executable: str | None
    version: str | None
    mistral_api_key_configured: bool
    contract_home: str
    runtime_home: str
    config_path: str
    agent_config_path: str
    prompt_path: str
    issues: list[str]


@dataclass(frozen=True)
class AgentLaunchPlan:
    adapter_key: str
    project_key: str
    mode: AgentMode
    command: list[str]
    prompt: str
    workdir: str
    environment: dict[str, str]
    summary: str


AGENT_ADAPTERS: dict[str, AgentAdapterDefinition] = {
    "mistral-vibe": AgentAdapterDefinition(
        key="mistral-vibe",
        name="Mistral Vibe",
        description=(
            "First supported coding-agent adapter for autotrain. It provides a deterministic "
            "bootstrap path without coupling the platform to a single provider or benchmark."
        ),
        executable=settings.mistral_vibe_executable,
        first_class=True,
    )
}


def list_agent_adapters() -> list[AgentAdapterDefinition]:
    return list(AGENT_ADAPTERS.values())


def get_agent_adapter(adapter_key: str) -> AgentAdapterDefinition | None:
    return AGENT_ADAPTERS.get(adapter_key)


def get_vibe_contract_dir() -> Path:
    return ROOT_DIR / ".vibe"


def get_vibe_config_path() -> Path:
    return get_vibe_contract_dir() / "config.toml"


def get_vibe_agent_config_path() -> Path:
    return get_vibe_contract_dir() / "agents" / f"{settings.mistral_vibe_agent_name}.toml"


def get_vibe_prompt_path() -> Path:
    return get_vibe_contract_dir() / "prompts" / "autotrain.md"


def get_vibe_runtime_home() -> Path:
    return Path(settings.mistral_vibe_home)


def get_agent_status(adapter_key: str) -> AgentAdapterStatus:
    adapter = get_agent_adapter(adapter_key)
    if adapter is None:
        raise ValueError(f"Unknown agent adapter '{adapter_key}'")
    if adapter.key != "mistral-vibe":
        raise ValueError(f"Unsupported agent adapter '{adapter_key}'")
    return _get_vibe_status(adapter)


def build_agent_launch_plan(
    *,
    adapter_key: str,
    project_key: str,
    mode: AgentMode | str,
    objective: str | None = None,
    max_turns: int | None = None,
) -> AgentLaunchPlan:
    adapter = get_agent_adapter(adapter_key)
    if adapter is None:
        raise ValueError(f"Unknown agent adapter '{adapter_key}'")
    if adapter.key != "mistral-vibe":
        raise ValueError(f"Unsupported agent adapter '{adapter_key}'")
    normalized_mode = AgentMode(mode)

    project = get_project(project_key)
    if project is None:
        raise ValueError(f"Unknown project '{project_key}'")

    prompt = _build_vibe_prompt(project_key=project_key, mode=normalized_mode, objective=objective)
    command = [
        adapter.executable,
        "--workdir",
        str(ROOT_DIR),
        "--trust",
        "--agent",
        settings.mistral_vibe_agent_name,
    ]
    summary = "Interactive planning session with manual review."

    if normalized_mode == AgentMode.AUTO:
        command.extend(["--prompt", prompt, "--output", "text"])
        summary = "Programmatic autonomous run with auto-approve semantics."
        if max_turns is not None:
            command.extend(["--max-turns", str(max_turns)])

    return AgentLaunchPlan(
        adapter_key=adapter.key,
        project_key=project.key,
        mode=normalized_mode,
        command=command,
        prompt=prompt,
        workdir=str(ROOT_DIR),
        environment={"VIBE_HOME": str(get_vibe_runtime_home())},
        summary=summary,
    )


def prepare_vibe_runtime_home() -> Path:
    runtime_home = get_vibe_runtime_home()
    runtime_home.mkdir(parents=True, exist_ok=True)

    shutil.copy2(get_vibe_config_path(), runtime_home / "config.toml")
    _copy_contract_directory(get_vibe_contract_dir() / "agents", runtime_home / "agents")
    _copy_contract_directory(get_vibe_contract_dir() / "prompts", runtime_home / "prompts")
    return runtime_home


def serialize_agent_status(status: AgentAdapterStatus) -> dict[str, object]:
    return asdict(status)


def serialize_launch_plan(plan: AgentLaunchPlan) -> dict[str, object]:
    payload = asdict(plan)
    payload["mode"] = plan.mode.value
    return payload


def _get_vibe_status(adapter: AgentAdapterDefinition) -> AgentAdapterStatus:
    resolved_executable = shutil.which(adapter.executable)
    version = _read_vibe_version(resolved_executable) if resolved_executable else None

    issues: list[str] = []
    if resolved_executable is None:
        issues.append("Vibe executable is not installed or not available on PATH.")
    if not settings.mistral_api_key:
        issues.append("MISTRAL_API_KEY is not configured in the process environment.")
    if not get_vibe_config_path().exists():
        issues.append("Repo-local .vibe/config.toml is missing.")
    if not get_vibe_agent_config_path().exists():
        issues.append("Repo-local Vibe agent configuration is missing.")
    if not get_vibe_prompt_path().exists():
        issues.append("Repo-local Vibe system prompt is missing.")

    return AgentAdapterStatus(
        key=adapter.key,
        name=adapter.name,
        available=resolved_executable is not None,
        executable=adapter.executable,
        resolved_executable=resolved_executable,
        version=version,
        mistral_api_key_configured=bool(settings.mistral_api_key),
        contract_home=str(get_vibe_contract_dir()),
        runtime_home=str(get_vibe_runtime_home()),
        config_path=str(get_vibe_config_path()),
        agent_config_path=str(get_vibe_agent_config_path()),
        prompt_path=str(get_vibe_prompt_path()),
        issues=issues,
    )


def _read_vibe_version(resolved_executable: str) -> str | None:
    try:
        completed = subprocess.run(
            [resolved_executable, "--version"],
            capture_output=True,
            check=False,
            text=True,
            timeout=10,
        )
    except OSError:
        return None

    output = (completed.stdout or completed.stderr).strip()
    if completed.returncode != 0 or not output:
        return None
    return output


def _copy_contract_directory(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def _build_vibe_prompt(*, project_key: str, mode: AgentMode, objective: str | None) -> str:
    project = get_project(project_key)
    if project is None:
        raise ValueError(f"Unknown project '{project_key}'")

    project_root = get_project_root(project)
    objective_text = objective or (
        "Improve the benchmark honestly under the project contract and the automated metric."
    )

    lines = [
        "Follow the autotrain project contract strictly.",
        f"Project key: {project.key}",
        f"Project root: {project_root}",
        f"Mutable artifact: {ROOT_DIR / project.mutable_artifact}",
        f"Metric: {project.metric_name} ({project.metric_direction.value})",
        f"Budget seconds: {project.default_budget_seconds}",
        f"Objective: {objective_text}",
        "Read these files first:",
        f"- @{project_root / 'program.md'}",
        f"- @{ROOT_DIR / project.mutable_artifact}",
        f"- @{ROOT_DIR / project.execution_entrypoint}",
    ]

    if mode == AgentMode.PLAN:
        lines.extend(
            [
                "Stay in planning mode only.",
                "Do not edit files and do not run commands.",
                "Return a concise readiness check, risks, and the first bounded experiment plan.",
            ]
        )
    else:
        lines.extend(
            [
                "Begin with setup validation against the documented contract.",
                "Then run exactly one bounded experiment cycle.",
                "Do not modify files outside the declared mutable artifact.",
                "Do not stop to ask for confirmation once execution begins.",
                "Leave the repository state aligned with the measured result.",
            ]
        )

    return "\n".join(lines)
