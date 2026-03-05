#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "[1/3] Creating virtual environment (.venv)..."
python3 -m venv .venv

echo "[2/3] Upgrading pip..."
. .venv/bin/activate
python -m pip install --upgrade pip

echo "[3/3] Installing dependencies..."
pip install -r requirements.txt
pip install notebook
pip install ipywidgets

echo "[Bonus] Enabling repository git hooks..."
git config core.hooksPath .githooks

echo "Setup complete."
echo "Next: run scripts/mac/launch.command"
