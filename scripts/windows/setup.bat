@echo off
cd /d "%~dp0\..\.."

echo [1/3] Creating virtual environment (.venv)...
python -m venv .venv

echo [2/3] Upgrading pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip

echo [3/3] Installing dependencies...
pip install -r requirements.txt
pip install notebook
pip install ipywidgets

echo Setup complete.
echo Next: run scripts\windows\launch.bat
pause
