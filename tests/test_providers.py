from autotrain_core.providers import get_provider_adapter, list_provider_adapters


def test_provider_registry_has_hosted_and_local_paths() -> None:
    providers = list_provider_adapters()
    keys = {provider.key for provider in providers}

    assert "mistral-api" in keys
    assert "ollama" in keys


def test_provider_definitions_expose_expected_defaults() -> None:
    mistral = get_provider_adapter("mistral-api")
    ollama = get_provider_adapter("ollama")

    assert mistral is not None
    assert ollama is not None
    assert mistral.requires_api_key is True
    assert ollama.requires_api_key is False
    assert mistral.base_url.startswith("https://")
    assert ollama.base_url.startswith("http://")
