from __future__ import annotations

import argparse
import json
import plistlib
from pathlib import Path
import sys
from urllib import error, request


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_packaged_release_contract",
        description="Validate the packaged macOS updater contract against Info.plist and GitHub Releases.",
    )
    parser.add_argument(
        "--info-plist",
        default="/Users/Shared/Projects/train/apps/macos/Info.plist",
        help="Absolute path to the macOS app Info.plist to validate.",
    )
    parser.add_argument(
        "--allow-missing-release",
        action="store_true",
        help="Treat a missing published GitHub release as a warning instead of a failure.",
    )
    args = parser.parse_args(argv)

    info_plist_path = Path(args.info_plist).expanduser().resolve()
    if not info_plist_path.exists():
        raise SystemExit(f"Info.plist was not found at {info_plist_path}")

    payload = _build_report(info_plist_path=info_plist_path, allow_missing_release=args.allow_missing_release)
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if payload["ok"] else 1


def _build_report(*, info_plist_path: Path, allow_missing_release: bool) -> dict[str, object]:
    info = plistlib.loads(info_plist_path.read_bytes())
    source = str(info.get("TRAINReleaseSource") or "")
    owner = str(info.get("TRAINReleaseRepositoryOwner") or "")
    name = str(info.get("TRAINReleaseRepositoryName") or "")

    problems: list[str] = []
    warnings: list[str] = []
    if source != "github-releases":
        problems.append("TRAINReleaseSource must be 'github-releases'.")
    if not owner:
        problems.append("TRAINReleaseRepositoryOwner is missing.")
    if not name:
        problems.append("TRAINReleaseRepositoryName is missing.")

    endpoint = (
        f"https://api.github.com/repos/{owner}/{name}/releases/latest"
        if owner and name
        else None
    )
    release_status: dict[str, object] = {
        "endpoint": endpoint,
        "reachable": False,
        "published_release_found": False,
    }

    if endpoint is not None:
        req = request.Request(endpoint, method="GET")
        try:
            with request.urlopen(req, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
                release_status["reachable"] = True
                release_status["published_release_found"] = True
                release_status["release_tag"] = payload.get("tag_name")
                release_status["release_url"] = payload.get("html_url")
        except error.HTTPError as exc:
            release_status["status_code"] = exc.code
            release_status["reachable"] = True
            if exc.code == 404:
                message = "No published GitHub release exists for the configured repository."
                # Keep the warning mode for bootstrap or recovery checks where the
                # repository configuration should still validate even before the
                # first release is published.
                if allow_missing_release:
                    warnings.append(message)
                else:
                    problems.append(message)
            else:
                problems.append(f"GitHub release endpoint returned HTTP {exc.code}.")
        except Exception as exc:
            problems.append(f"GitHub release endpoint could not be reached: {exc}")

    return {
        "ok": not problems,
        "info_plist_path": str(info_plist_path),
        "release_source": source,
        "repository_owner": owner,
        "repository_name": name,
        "release_status": release_status,
        "warnings": warnings,
        "problems": problems,
    }


if __name__ == "__main__":
    raise SystemExit(main())
