@echo off
REM Check the current setup and diagnose issues

cd /d "%~dp0"

echo ========================================
echo Phase 3 Chatbot Setup Check
echo ========================================
echo.

echo 1. Checking virtual environment...
if exist "venv\Scripts\python.exe" (
    echo    [OK] Virtual environment exists
) else (
    echo    [ERROR] Virtual environment NOT found
    echo    Please create it: python -m venv venv
    goto :end
)

echo.
echo 2. Checking Python version in venv...
venv\Scripts\python.exe --version

echo.
echo 3. Checking global Python (what 'python' command uses)...
python --version

echo.
echo 4. Checking Pydantic in venv...
venv\Scripts\python.exe -m pip show pydantic | findstr "Version Location"

echo.
echo 5. Checking Pydantic globally...
python -m pip show pydantic | findstr "Version Location"

echo.
echo 6. Checking if FastAPI is installed...
venv\Scripts\python.exe -c "import fastapi; print('FastAPI:', fastapi.__version__)" 2>nul && echo    [OK] FastAPI installed || echo    [ERROR] FastAPI not found

echo.
echo 7. Checking if uvicorn is installed...
venv\Scripts\python.exe -c "import uvicorn; print('Uvicorn:', uvicorn.__version__)" 2>nul && echo    [OK] Uvicorn installed || echo    [ERROR] Uvicorn not found

echo.
echo ========================================
echo Diagnosis:
echo ========================================

venv\Scripts\python.exe -c "import pydantic; v = pydantic.VERSION; print('\nPydantic version in venv:', v); print('Status: OK - Using v1' if v.startswith('1.') else 'Status: ERROR - Need v1, got v' + v)"

echo.
echo ========================================
echo Recommendation:
echo ========================================
echo.
echo If Pydantic version is NOT 1.10.13:
echo   1. Run: venv\Scripts\activate
echo   2. Run: pip install pydantic==1.10.13
echo.
echo To start backend:
echo   - Double-click: start_backend.bat
echo   - Or run: venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
echo.

:end
pause
