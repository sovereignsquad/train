#!/usr/bin/env bash
set -euo pipefail

uv run uvicorn autotrain_api.main:app --reload
