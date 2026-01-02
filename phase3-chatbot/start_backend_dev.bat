@echo off
REM Start Backend WITH auto-reload using watchfiles (better than default reload)

cd /d "%~dp0"

echo ========================================
echo Starting Phase 3 Chatbot Backend
echo (Dev Mode - Auto-Reload Enabled)
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo Checking for watchfiles package...
venv\Scripts\python.exe -c "import watchfiles" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Watchfiles not installed. Installing now...
    venv\Scripts\python.exe -m pip install watchfiles
    echo.
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
echo Auto-reload ENABLED - Server will restart on code changes
echo Using watchfiles for reliable file watching
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start with watchfiles for better reload support
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

pause
