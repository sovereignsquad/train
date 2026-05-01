#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Building Autotrain macOS shell..."
cd "$PROJECT_DIR"
swift build -c release 2>&1 | grep -E "error:|warning:" || echo "Build successful"
