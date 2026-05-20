from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import importlib.util
import json
import platform
from pathlib import Path
from urllib import request

from train_core.agents import get_agent_status
from train_core.config import ROOT_DIR
from train_core.model_resolution import ModelResolutionError, get_models_root, resolve_model_ref
from train_core.providers import get_provider_status, list_provider_adapters


DEFAULT_TRAIN_API_BASE_URL = "http://127.0.0.1:8000"


@dataclass(frozen=True)
class HealthCheckResult:
    key: str
    status: str
    summary: str
    details: dict[str, object]
    remediation: str | None = None


@dataclass(frozen=True)
class HealthReport:
    workflow: str
    generated_at: str
    overall_status: str
    ok: bool
    warning_count: int
    failure_count: int
    checks: tuple[HealthCheckResult, ...]

    def to_payload(self) -> dict[str, object]:
        payload = asdict(self)
        payload["checks"] = [asdict(check) for check in self.checks]
        return payload


class TrainingReadinessError(ValueError):
    """Raised when the local environment is not ready for the offline training lane."""


def build_doctor_report(
    *,
    workflow: str = "default",
    api_base_url: str | None = None,
    trinity_root: str | Path | None = None,
) -> HealthReport:
    checks: list[HealthCheckResult] = []
    checks.append(check_train_api(api_base_url=api_base_url))
    checks.append(check_mistral_vibe())
    checks.extend(check_provider_relations())
    checks.append(check_trinity_repo_presence(trinity_root=trinity_root))
    checks.append(check_training_lane_readiness(required=workflow == "training"))

    statuses = [check.status for check in checks]
    failure_count = sum(1 for status in statuses if status == "fail")
    warning_count = sum(1 for status in statuses if status == "warn")
    overall_status = "fail" if failure_count else "warn" if warning_count else "pass"
    return HealthReport(
        workflow=workflow,
        generated_at=datetime.now(UTC).isoformat(),
        overall_status=overall_status,
        ok=failure_count == 0,
        warning_count=warning_count,
        failure_count=failure_count,
        checks=tuple(checks),
    )


def check_train_api(*, api_base_url: str | None = None) -> HealthCheckResult:
    base_url = str(api_base_url or DEFAULT_TRAIN_API_BASE_URL).rstrip("/")
    health_url = f"{base_url}/health"
    try:
        req = request.Request(health_url, method="GET")
        with request.urlopen(req, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return HealthCheckResult(
            key="train-api",
            status="fail",
            summary=f"{health_url} could not be reached.",
            details={"base_url": base_url, "error": str(exc)},
            remediation="Start the local train API or point the doctor command at a reachable base URL.",
        )

    service = str(payload.get("service") or "")
    status = str(payload.get("status") or "")
    if status != "ok":
        return HealthCheckResult(
            key="train-api",
            status="fail",
            summary=f"{health_url} returned an unhealthy payload.",
            details={"base_url": base_url, "payload": payload},
            remediation="Inspect the local API logs and fix the health endpoint failure before continuing.",
        )
    return HealthCheckResult(
        key="train-api",
        status="pass",
        summary=f"{service or 'train-api'} responded successfully.",
        details={"base_url": base_url, "payload": payload},
    )


def check_mistral_vibe() -> HealthCheckResult:
    status = get_agent_status("mistral-vibe")
    missing = [issue for issue in status.issues if "missing" in issue.lower() or "not configured" in issue.lower()]
    if status.available and not missing:
        return HealthCheckResult(
            key="mistral-vibe",
            status="pass",
            summary="Mistral Vibe is installed and its repo-local contract files are present.",
            details={
                "resolved_executable": status.resolved_executable,
                "version": status.version,
                "contract_home": status.contract_home,
                "runtime_home": status.runtime_home,
            },
        )
    return HealthCheckResult(
        key="mistral-vibe",
        status="fail",
        summary="Mistral Vibe is not ready for bounded agent runs.",
        details={
            "available": status.available,
            "resolved_executable": status.resolved_executable,
            "issues": status.issues,
        },
        remediation="Install the vibe executable, configure MISTRAL_API_KEY, and restore the repo-local .vibe contract files.",
    )


def check_provider_relations() -> tuple[HealthCheckResult, ...]:
    results: list[HealthCheckResult] = []
    for provider in list_provider_adapters():
        status = get_provider_status(provider.key)
        if status.configured and status.reachable:
            results.append(
                HealthCheckResult(
                    key=provider.key,
                    status="pass",
                    summary=f"{provider.name} is reachable.",
                    details={
                        "base_url": status.base_url,
                        "model_count": status.model_count,
                        "models": list(status.models),
                    },
                )
            )
            continue
        results.append(
            HealthCheckResult(
                key=provider.key,
                status="fail",
                summary=f"{provider.name} is not reachable.",
                details={
                    "base_url": status.base_url,
                    "configured": status.configured,
                    "reachable": status.reachable,
                    "issues": status.issues,
                },
                remediation=(
                    "Configure credentials or start the local provider service before using provider-backed flows."
                ),
            )
        )
    return tuple(results)


def check_trinity_repo_presence(*, trinity_root: str | Path | None = None) -> HealthCheckResult:
    root = _resolve_trinity_root(trinity_root)
    if root.exists():
        return HealthCheckResult(
            key="trinity-repo",
            status="pass",
            summary=f"Local Trinity checkout is present at {root}.",
            details={"root": str(root)},
        )
    return HealthCheckResult(
        key="trinity-repo",
        status="warn",
        summary="Local Trinity checkout is not present at the expected path.",
        details={"root": str(root)},
        remediation="Clone or point to the sibling Trinity checkout before running cross-repo handoff proofs.",
    )


def check_training_lane_readiness(*, required: bool, spec=None) -> HealthCheckResult:
    details: dict[str, object] = {
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "models_root": str(get_models_root()),
        "mlx_lm_installed": importlib.util.find_spec("mlx_lm") is not None,
    }
    problems: list[str] = []

    if platform.system() != "Darwin" or platform.machine() not in {"arm64", "aarch64"}:
        problems.append("The active mlx-lm lane is Apple-Silicon-only.")
    if importlib.util.find_spec("mlx_lm") is None:
        problems.append("mlx_lm is not installed in the current Python environment.")

    if spec is not None:
        details["training_spec_ref"] = spec.ref
        details["base_model_source_kind"] = spec.base_model_source_kind
        details["base_model_ref"] = spec.base_model_ref
        try:
            resolved = resolve_model_ref(spec.base_model_ref, source_kind=spec.base_model_source_kind)
        except ModelResolutionError as exc:
            problems.append(str(exc))
        else:
            details["resolved_base_model_ref"] = resolved.resolved_ref
            details["resolved_base_model_path"] = resolved.resolved_path
            if spec.base_model_source_kind == "local-path":
                models_root = get_models_root()
                if not models_root.exists():
                    problems.append(
                        f"TRAIN_MODELS_ROOT '{models_root}' does not exist for a local-path training spec."
                    )
                resolved_path = Path(resolved.resolved_path or "")
                if not resolved_path.exists():
                    problems.append(
                        f"Resolved local model path '{resolved_path}' does not exist."
                    )
        output_dir = Path(spec.output_dir)
        details["output_dir"] = str(output_dir)
        if not output_dir.exists():
            problems.append(f"Training output_dir '{output_dir}' does not exist.")

    if not problems:
        return HealthCheckResult(
            key="offline-training",
            status="pass",
            summary="The offline mlx-lm training lane looks ready.",
            details=details,
        )

    return HealthCheckResult(
        key="offline-training",
        status="fail" if required or spec is not None else "warn",
        summary="The offline mlx-lm training lane is not ready.",
        details={**details, "problems": problems},
        remediation=(
            "Install mlx-lm, use an Apple-Silicon machine, and verify TRAIN_MODELS_ROOT plus any local-path model refs before starting training."
        ),
    )


def assert_training_lane_ready(*, spec) -> None:
    check = check_training_lane_readiness(required=True, spec=spec)
    if check.status != "pass":
        problems = check.details.get("problems") or ()
        rendered = "; ".join(str(problem) for problem in problems) or check.summary
        raise TrainingReadinessError(rendered)


def render_health_report(report: HealthReport) -> str:
    lines = [
        f"workflow: {report.workflow}",
        f"overall_status: {report.overall_status}",
        f"warnings: {report.warning_count}",
        f"failures: {report.failure_count}",
    ]
    for check in report.checks:
        lines.append(f"{check.key}: {check.status} - {check.summary}")
        if check.remediation:
            lines.append(f"  remediation: {check.remediation}")
    return "\n".join(lines)


def _resolve_trinity_root(trinity_root: str | Path | None) -> Path:
    if trinity_root is not None:
        return Path(trinity_root).expanduser().resolve()
    configured = Path(ROOT_DIR).parent / "trinity"
    return configured.resolve()
