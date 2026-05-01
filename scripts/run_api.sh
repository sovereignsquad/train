#!/usr/bin/env bash
set -euo pipefail

uv run uvicorn train_api.main:app --reload
