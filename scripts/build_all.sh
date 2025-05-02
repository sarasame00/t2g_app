#!/bin/bash

# ============================
# Universal Build Script
# For: Python (PyInstaller) + Electron
# ============================

# Absolute paths (relative to this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$ROOT_DIR/venv"
SPEC_FILE="$ROOT_DIR/run.spec"
DIST_BINARY="$ROOT_DIR/dist/run"
ELECTRON_DIR="$ROOT_DIR/electron"
ELECTRON_BINARY="$ELECTRON_DIR/run"


# Colors for output
green="\033[0;32m"
red="\033[0;31m"
nc="\033[0m"

echo -e "${green}Step 1: Activating virtualenv...${nc}"
source "$VENV_PATH/bin/activate" || { echo -e "${red}❌ Failed to activate virtualenv.${nc}"; exit 1; }

echo -e "${green}Step 2: Building Python binary...${nc}"
pyinstaller "$SPEC_FILE" || { echo -e "${red}❌ PyInstaller build failed.${nc}"; exit 1; }

echo -e "${green}Step 3: Copying binary to Electron app...${nc}"
cp "$DIST_BINARY" "$ELECTRON_DIR" || { echo -e "${red}❌ Failed to copy binary.${nc}"; exit 1; }

# Make executable (only on Unix)
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
  chmod +x "$ELECTRON_BINARY"
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
  echo -e "${green}Step 4: Packaging Electron app for macOS (.dmg)...${nc}"
  cd "$ELECTRON_DIR" && npm run dist || { echo -e "${red}❌ Electron build failed.${nc}"; exit 1; }
fi

echo -e "${green}✅ Build complete!${nc}"
