@echo off
cd /d "%~dp0\..\.."

set "PYTHON_CMD=python"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3.12 -c "import sys" >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_CMD=py -3.12"
        echo Using Python 3.12 via py launcher.
    )
)

echo [1/3] Creating virtual environment (.venv)...
%PYTHON_CMD% -m venv .venv

echo [2/3] Upgrading pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip

echo [3/3] Installing dependencies...
pip install -r requirements.txt
pip install notebook
pip install ipywidgets

echo [Bonus] Enabling repository git hooks...
git config core.hooksPath .githooks

echo Setup complete.
echo Next: run scripts\windows\launch.bat
pause
