#!/bin/bash
set -uo pipefail

cd "$(dirname "$0")"

if [ -f ".venv/bin/activate" ]; then
  . .venv/bin/activate
fi

python student_gui.py
gui_status=$?
if [ "$gui_status" -ne 0 ]; then
  echo "GUI failed to launch (exit $gui_status). Falling back to notebook..."
  if command -v jupyter >/dev/null 2>&1; then
    jupyter notebook fstic_notebook.ipynb
  else
    echo "Notebook fallback unavailable: jupyter is not installed."
    echo "Run ./setup_student.command first, then retry."
    exit "$gui_status"
  fi
fi
