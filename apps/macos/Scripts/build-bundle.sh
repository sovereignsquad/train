#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="Autotrain"
BUILD_DIR="$PROJECT_DIR/.build/release"
BUNDLE_DIR="$PROJECT_DIR/dist"

echo "Building and bundling $APP_NAME..."
cd "$PROJECT_DIR"
swift build -c release > /dev/null

rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR/$APP_NAME.app/Contents/MacOS"
mkdir -p "$BUNDLE_DIR/$APP_NAME.app/Contents/Resources"

cp "$BUILD_DIR/$APP_NAME" "$BUNDLE_DIR/$APP_NAME.app/Contents/MacOS/"
chmod +x "$BUNDLE_DIR/$APP_NAME.app/Contents/MacOS/$APP_NAME"
cp "$PROJECT_DIR/Info.plist" "$BUNDLE_DIR/$APP_NAME.app/Contents/"
echo -n "APPL????" > "$BUNDLE_DIR/$APP_NAME.app/Contents/PkgInfo"

codesign --force --deep --sign - "$BUNDLE_DIR/$APP_NAME.app" >/dev/null 2>&1 || true

echo "Bundle ready at $BUNDLE_DIR/$APP_NAME.app"
