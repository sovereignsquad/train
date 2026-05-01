#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="Train"
BUILD_DIR="$PROJECT_DIR/.build/release"
BUNDLE_DIR="$PROJECT_DIR/dist"
ICON_SOURCE_DIR="$PROJECT_DIR/.build/icon-assets"
ICONSET_DIR="$ICON_SOURCE_DIR/AppIcon.iconset"
ICON_PNG="$ICON_SOURCE_DIR/app-icon-1024.png"
ICON_ICNS="$ICON_SOURCE_DIR/$APP_NAME.icns"

echo "Building and bundling $APP_NAME..."
cd "$PROJECT_DIR"
swift build -c release > /dev/null

rm -rf "$ICONSET_DIR"
mkdir -p "$ICONSET_DIR"
swift Scripts/generate_app_icon.swift "$ICON_PNG"

for size in 16 32 128 256 512; do
  sips -z "$size" "$size" "$ICON_PNG" --out "$ICONSET_DIR/icon_${size}x${size}.png" >/dev/null
  retina_size=$((size * 2))
  sips -z "$retina_size" "$retina_size" "$ICON_PNG" --out "$ICONSET_DIR/icon_${size}x${size}@2x.png" >/dev/null
done

iconutil -c icns "$ICONSET_DIR" -o "$ICON_ICNS"

rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR/$APP_NAME.app/Contents/MacOS"
mkdir -p "$BUNDLE_DIR/$APP_NAME.app/Contents/Resources"

cp "$BUILD_DIR/$APP_NAME" "$BUNDLE_DIR/$APP_NAME.app/Contents/MacOS/"
chmod +x "$BUNDLE_DIR/$APP_NAME.app/Contents/MacOS/$APP_NAME"
cp "$PROJECT_DIR/Info.plist" "$BUNDLE_DIR/$APP_NAME.app/Contents/"
cp "$ICON_ICNS" "$BUNDLE_DIR/$APP_NAME.app/Contents/Resources/"
echo -n "APPL????" > "$BUNDLE_DIR/$APP_NAME.app/Contents/PkgInfo"

codesign --force --deep --sign - "$BUNDLE_DIR/$APP_NAME.app" >/dev/null 2>&1 || true

echo "Bundle ready at $BUNDLE_DIR/$APP_NAME.app"
