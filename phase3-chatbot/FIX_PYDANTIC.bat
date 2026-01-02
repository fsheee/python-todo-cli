@echo off
REM Fix Pydantic compatibility issue for Python 3.13
REM This script downgrades Pydantic to v1.10.13

echo ========================================
echo Fixing Pydantic Compatibility Issue
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Could not activate virtual environment
    echo Please make sure venv exists: python -m venv venv
    pause
    exit /b 1
)

echo Step 2: Uninstalling Pydantic v2...
pip uninstall pydantic pydantic-core pydantic-settings -y

echo.
echo Step 3: Installing Pydantic v1 (Python 3.13 compatible)...
pip install pydantic==1.10.13

echo.
echo Step 4: Verifying installation...
python -c "import pydantic; print(f'Pydantic version: {pydantic.VERSION}')"

echo.
echo ========================================
echo Fix complete!
echo ========================================
echo.
echo You can now start the backend with:
echo   python -m uvicorn app.main:app --port 8001 --reload
echo.
pause
