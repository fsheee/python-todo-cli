# Quick Fix for Pydantic Error

**Error:** `TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'`

**Cause:** Python 3.13 incompatibility with Pydantic v2.12.5

---

## 🚀 Quick Fix (Choose One)

### Option 1: Run the Fix Script (Windows)

Double-click `FIX_PYDANTIC.bat` or run:
```cmd
cd phase3-chatbot
FIX_PYDANTIC.bat
```

### Option 2: Manual Commands (Windows)

```cmd
cd phase3-chatbot
venv\Scripts\activate
pip uninstall pydantic pydantic-core pydantic-settings -y
pip install pydantic==1.10.13
```

### Option 3: Manual Commands (Mac/Linux)

```bash
cd phase3-chatbot
source venv/bin/activate
pip uninstall pydantic pydantic-core pydantic-settings -y
pip install pydantic==1.10.13
```

---

## ✅ Verify the Fix

After running the fix, verify Pydantic is v1:

```bash
python -c "import pydantic; print(pydantic.VERSION)"
```

Expected output: `1.10.13`

---

## 🚀 Start the Backend

Once fixed, start the backend:

```bash
cd phase3-chatbot
python -m uvicorn app.main:app --port 8001 --reload
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
🚀 Phase 3 Chatbot starting...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

---

## 🧪 Test the Backend

Open a new terminal and test:

```bash
curl http://localhost:8001/
```

Should return:
```json
{"message": "Phase 3 Chatbot API"}
```

---

## 🎯 Test the Login Page

1. Make sure backend is running on port 8001
2. Make sure frontend is running: `cd frontend && npm run dev`
3. Open http://localhost:3000/login
4. Try logging in - should now connect!

---

## ⚠️ Important Notes

**Issue Location:** The error shows it's coming from a globally installed Pydantic at:
```
C:\Users\Kashif\AppData\Roaming\Python\Python313\site-packages
```

**This means:**
1. Pydantic might be installed globally (outside venv)
2. You may need to ensure venv is activated
3. Or install with `--force-reinstall` flag

**If the above fix doesn't work, try:**

```cmd
cd phase3-chatbot
venv\Scripts\activate
pip install --force-reinstall pydantic==1.10.13
```

Or create a fresh venv:

```cmd
cd phase3-chatbot
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements-py313.txt
```

---

## 🔧 Alternative: Use Python 3.12

If Pydantic v1 doesn't work for some reason, the most reliable solution is to use Python 3.12:

1. Install Python 3.12 from python.org
2. Create new venv: `python3.12 -m venv venv`
3. Install requirements: `pip install -r requirements.txt`
4. Everything will work perfectly

---

## 📞 Need Help?

If you're still having issues:

1. Check if venv is activated (prompt should show `(venv)`)
2. Check Python version: `python --version`
3. Check Pydantic version: `pip show pydantic`
4. Share the output and we'll debug further

---

**Quick Summary:**
- Uninstall Pydantic v2
- Install Pydantic v1.10.13
- Start backend
- Test login page
