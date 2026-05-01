from dataclasses import asdict, dataclass
from enum import StrEnum
import json
from urllib import error, request

from train_core.config import settings


class ProviderKind(StrEnum):
    HOSTED = "hosted"
    LOCAL = "local"


@dataclass(frozen=True)
class ProviderAdapterDefinition:
    key: str
    name: str
    kind: ProviderKind
    description: str
    base_url: str
    requires_api_key: bool


@dataclass(frozen=True)
class ProviderStatus:
    key: str
    name: str
    kind: ProviderKind
    base_url: str
    configured: bool
    reachable: bool
    model_count: int | None
    models: tuple[str, ...]
    issues: list[str]


PROVIDERS: dict[str, ProviderAdapterDefinition] = {
    "mistral-api": ProviderAdapterDefinition(
        key="mistral-api",
        name="Mistral API",
        kind=ProviderKind.HOSTED,
        description="First hosted provider adapter for train.",
        base_url=settings.mistral_api_base_url,
        requires_api_key=True,
    ),
    "ollama": ProviderAdapterDefinition(
        key="ollama",
        name="Ollama",
        kind=ProviderKind.LOCAL,
        description="First local provider adapter for train via the Ollama HTTP API.",
        base_url=settings.ollama_base_url,
        requires_api_key=False,
    ),
}


def list_provider_adapters() -> list[ProviderAdapterDefinition]:
    return list(PROVIDERS.values())


def get_provider_adapter(provider_key: str) -> ProviderAdapterDefinition | None:
    return PROVIDERS.get(provider_key)


def get_provider_status(provider_key: str) -> ProviderStatus:
    provider = get_provider_adapter(provider_key)
    if provider is None:
        raise ValueError(f"Unknown provider adapter '{provider_key}'")

    if provider.key == "mistral-api":
        return _get_mistral_status(provider)
    if provider.key == "ollama":
        return _get_ollama_status(provider)

    raise ValueError(f"Unsupported provider adapter '{provider_key}'")


def serialize_provider_status(status: ProviderStatus) -> dict[str, object]:
    payload = asdict(status)
    payload["kind"] = status.kind.value
    return payload


def _get_mistral_status(provider: ProviderAdapterDefinition) -> ProviderStatus:
    issues: list[str] = []
    if not settings.mistral_api_key:
        issues.append("MISTRAL_API_KEY is not configured.")
        return ProviderStatus(
            key=provider.key,
            name=provider.name,
            kind=provider.kind,
            base_url=provider.base_url,
            configured=False,
            reachable=False,
            model_count=None,
            models=(),
            issues=issues,
        )

    try:
        payload = _fetch_json(
            f"{provider.base_url.rstrip('/')}/v1/models",
            headers={"Authorization": f"Bearer {settings.mistral_api_key}"},
        )
    except RuntimeError as exc:
        issues.append(str(exc))
        return ProviderStatus(
            key=provider.key,
            name=provider.name,
            kind=provider.kind,
            base_url=provider.base_url,
            configured=True,
            reachable=False,
            model_count=None,
            models=(),
            issues=issues,
        )

    models = tuple(sorted(model["id"] for model in payload.get("data", []) if "id" in model))[:10]
    return ProviderStatus(
        key=provider.key,
        name=provider.name,
        kind=provider.kind,
        base_url=provider.base_url,
        configured=True,
        reachable=True,
        model_count=len(payload.get("data", [])),
        models=models,
        issues=issues,
    )


def _get_ollama_status(provider: ProviderAdapterDefinition) -> ProviderStatus:
    issues: list[str] = []
    try:
        payload = _fetch_json(f"{provider.base_url.rstrip('/')}/api/tags")
    except RuntimeError as exc:
        issues.append(str(exc))
        return ProviderStatus(
            key=provider.key,
            name=provider.name,
            kind=provider.kind,
            base_url=provider.base_url,
            configured=True,
            reachable=False,
            model_count=None,
            models=(),
            issues=issues,
        )

    model_names = tuple(sorted(model["name"] for model in payload.get("models", []) if "name" in model))[:10]
    return ProviderStatus(
        key=provider.key,
        name=provider.name,
        kind=provider.kind,
        base_url=provider.base_url,
        configured=True,
        reachable=True,
        model_count=len(payload.get("models", [])),
        models=model_names,
        issues=issues,
    )


def _fetch_json(url: str, headers: dict[str, str] | None = None) -> dict:
    req = request.Request(url, headers=headers or {}, method="GET")
    try:
        with request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{url} returned {exc.code}: {body}") from exc
    except Exception as exc:
        raise RuntimeError(f"{url} could not be reached: {exc}") from exc
