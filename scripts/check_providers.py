from __future__ import annotations

import json

from autotrain_core.providers import get_provider_status, list_provider_adapters, serialize_provider_status


def main() -> None:
    payload = {
        "providers": [
            serialize_provider_status(get_provider_status(provider.key))
            for provider in list_provider_adapters()
        ]
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
