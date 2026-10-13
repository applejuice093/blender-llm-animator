#!/usr/bin/env bash
# Linux/macOS counterpart of scripts/setup_env.ps1.
# Creates backend/venv and installs the backend requirements.
#
# Usage: scripts/setup_env.sh [--dev] [--finetune]
#   --dev       also install pytest/httpx (requirements-dev.txt)
#   --finetune  also install the Unsloth training stack (requirements-finetune.txt)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"
PYTHON="${PYTHON:-python3}"

REQ_FILES=("requirements.txt")
for arg in "$@"; do
  case "$arg" in
    --dev) REQ_FILES+=("requirements-dev.txt") ;;
    --finetune) REQ_FILES+=("requirements-finetune.txt") ;;
    -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "error: $PYTHON not found. Install Python 3.10+ or set PYTHON=/path/to/python." >&2
  exit 1
fi

cd "$BACKEND_DIR"
echo "Setting up Python virtual environment in $BACKEND_DIR..."
if [ ! -d venv ]; then
  "$PYTHON" -m venv venv
  echo "Virtual environment created."
else
  echo "Virtual environment already exists."
fi

# shellcheck disable=SC1091
source venv/bin/activate
python -m pip install --upgrade pip
for req in "${REQ_FILES[@]}"; do
  echo "Installing $req..."
  python -m pip install -r "$req"
done

echo "Backend environment setup complete!"
echo "Activate it with: source backend/venv/bin/activate"
