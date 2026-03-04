@echo off
cd /d "%~dp0\..\.."

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

jupyter notebook fstic_notebook.ipynb
