@echo off
REM Start Backend WITHOUT reload (stable, no multiprocessing errors)

cd /d "%~dp0"

echo ========================================
echo Starting Phase 3 Chatbot Backend
echo (Stable Mode - No Auto-Reload)
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo Using Python from venv...
venv\Scripts\python.exe --version

echo.
echo Checking Pydantic version...
venv\Scripts\python.exe -c "import pydantic; print(f'Pydantic: {pydantic.VERSION}')"

echo.
echo ========================================
echo Starting FastAPI server on port 8001...
echo ========================================
echo.
echo NOTE: Auto-reload is DISABLED to avoid multiprocessing errors
echo To restart after code changes, press Ctrl+C and run this script again
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start without --reload to avoid multiprocessing errors
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001

pause
