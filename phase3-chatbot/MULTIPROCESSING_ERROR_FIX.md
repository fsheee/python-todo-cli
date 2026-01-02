# Multiprocessing Error Fix

**Error:** `SpawnProcess-1: Traceback... uvicorn._subprocess.py`

**Cause:** Python 3.13 with uvicorn's `--reload` flag has multiprocessing issues on Windows

---

## 🎯 Quick Fix (Remove --reload flag)

### Option 1: Start Without Reload

**Instead of:**
```cmd
venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --reload
```

**Use this:**
```cmd
venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
```

---

### Option 2: Use Different Reload Method

**Use watchfiles instead:**
```cmd
venv\Scripts\python.exe -m pip install watchfiles
venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --reload --reload-dir ./app
```

---

### Option 3: Disable Multiprocessing

**Single worker mode:**
```cmd
venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --reload --workers 1
```

---

## ✅ Updated Startup Scripts

I'll update the startup scripts to avoid this error.

### For Development (Manual Restart)
```cmd
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Pros:
- ✅ No multiprocessing errors
- ✅ Works reliably
- ⚠️ Must manually restart after code changes

### For Development (With Watch)
```cmd
venv\Scripts\python.exe -m pip install watchfiles
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Pros:
- ✅ Auto-reload on code changes
- ✅ More reliable than default reload
- ⚠️ Requires watchfiles package

---

## 🔧 Technical Details

### What's Happening

The error occurs in `uvicorn._subprocess.py` when uvicorn tries to spawn a subprocess for hot-reloading. Python 3.13 on Windows has stricter multiprocessing requirements.

**The problematic line:**
```python
File "uvicorn\_subprocess.py", line 78, in subprocess_started
    target(sockets=sockets)
```

**Why it fails:**
- Python 3.13 changed multiprocessing behavior
- Windows uses "spawn" method (not fork)
- Uvicorn's reload mechanism conflicts with this

---

## 📋 Solution Comparison

| Method | Auto-Reload | Stability | Setup |
|--------|-------------|-----------|-------|
| No --reload | ❌ No | ✅ Perfect | Easy |
| --reload removed | ❌ No | ✅ Perfect | Easy |
| watchfiles | ✅ Yes | ✅ Good | Need install |
| Manual restart | ❌ No | ✅ Perfect | Easy |

---

## ⚡ Recommended Approach

**For now (quick fix):**
```cmd
venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
```

**For development (better):**
```cmd
# Install watchfiles
venv\Scripts\python.exe -m pip install watchfiles

# Start with better reload
venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --reload
```

**For production:**
```cmd
# No reload needed in production
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

---

## 🔄 Alternative: Use nodemon (Node.js)

If you have Node.js installed:

```bash
npm install -g nodemon
nodemon --exec "venv/Scripts/python.exe -m uvicorn app.main:app --port 8001" --watch app
```

This watches for changes and restarts the server automatically.

---

## ✅ Updated start_backend.bat

The startup script has been updated to avoid this error by default.
