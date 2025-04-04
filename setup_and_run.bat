@echo off
REM Change to the project directory (optional if already there)
cd /d "%~dp0"

REM Create virtual environment if it does not exist
if not exist ".venv\Scripts\activate" (
    echo Creating virtual environment with Python 3.11...
    py -3.11 -m venv .venv
)

REM Activate the virtual environment
call .venv\Scripts\activate

REM Upgrade pip
pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

REM Execute the hydration script
python hydrate_twikit.py

pause
