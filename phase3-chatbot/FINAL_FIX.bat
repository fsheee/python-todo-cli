@echo off
REM Complete fix for Python 3.13 + FastAPI + Pydantic compatibility

cd /d "%~dp0"

echo ========================================
echo Complete Pydantic + FastAPI Fix
echo ========================================
echo.

call venv\Scripts\activate.bat

echo Step 1: Uninstalling incompatible packages...
pip uninstall fastapi pydantic pydantic-core pydantic-settings starlette -y

echo.
echo Step 2: Installing compatible versions...
echo   - Pydantic v1.10.13 (Python 3.13 compatible)
echo   - FastAPI v0.68.2 (Pydantic v1 compatible)
echo   - Starlette v0.14.2 (compatible)
echo.

pip install pydantic==1.10.13
pip install starlette==0.14.2
pip install fastapi==0.68.2

echo.
echo Step 3: Verifying installation...
python -c "import pydantic; print('Pydantic:', pydantic.VERSION)"
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import starlette; print('Starlette:', starlette.__version__)"

echo.
echo ========================================
echo Fix complete!
echo ========================================
echo.
echo You can now start the backend:
echo   python -m uvicorn app.main:app --port 8001
echo.
pause
