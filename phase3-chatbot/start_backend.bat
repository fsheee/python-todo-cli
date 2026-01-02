@echo off
REM Start Backend with correct Python from venv
REM This ensures we use the venv's Python, not the global one

cd /d "%~dp0"

echo ========================================
echo Starting Phase 3 Chatbot Backend
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please create it first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements-py313.txt
    pause
    exit /b 1
)

REM Display Python and Pydantic versions
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
echo Press Ctrl+C to stop the server
echo.

REM Start uvicorn with venv's Python
REM Note: --reload removed to avoid Python 3.13 multiprocessing errors
REM Use start_backend_dev.bat if you need auto-reload with watchfiles
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001

pause
