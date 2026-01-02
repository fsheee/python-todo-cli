# Which Script Should I Use?

## 🎯 Quick Answer

**For most users:** Double-click `start_backend.bat`

---

## 📋 All Available Scripts

### 1. `start_backend.bat` ⭐ **RECOMMENDED**

**When to use:** Always (most stable)

**Features:**
- ✅ No multiprocessing errors
- ✅ Works reliably every time
- ✅ Uses correct Python (venv)
- ⚠️ No auto-reload (must restart manually after code changes)

**Command:**
```cmd
venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
```

---

### 2. `start_backend_stable.bat`

**When to use:** Same as `start_backend.bat`, just another name

**Features:**
- Same as above
- Explicitly named "stable" to be clear about what it does

---

### 3. `start_backend_dev.bat` 🔄

**When to use:** When actively developing (changing code frequently)

**Features:**
- ✅ Auto-reload on code changes
- ✅ Automatically installs watchfiles if needed
- ✅ More reliable than default --reload
- ⚠️ Slightly slower startup

**Requirements:**
- Installs `watchfiles` package (done automatically)

---

### 4. `check_setup.bat` 🔍

**When to use:** When something isn't working

**Features:**
- Shows which Python is being used
- Shows Pydantic versions (venv vs global)
- Diagnoses common issues
- Gives recommendations

---

### 5. `FIX_PYDANTIC.bat` 🔧

**When to use:** When you get Pydantic errors

**Features:**
- Uninstalls Pydantic v2
- Installs Pydantic v1 (Python 3.13 compatible)
- Verifies installation

---

## 📊 Comparison Table

| Script | Stability | Auto-Reload | Speed | Best For |
|--------|-----------|-------------|-------|----------|
| start_backend.bat | ⭐⭐⭐⭐⭐ | ❌ | Fast | **Production, Testing** |
| start_backend_stable.bat | ⭐⭐⭐⭐⭐ | ❌ | Fast | Same as above |
| start_backend_dev.bat | ⭐⭐⭐⭐ | ✅ | Medium | **Active Development** |
| check_setup.bat | N/A | N/A | Fast | **Diagnostics** |
| FIX_PYDANTIC.bat | N/A | N/A | Fast | **Fixing Errors** |

---

## 🎯 Decision Tree

```
Are you getting errors?
├─ YES → Run check_setup.bat
│         ├─ Pydantic error? → Run FIX_PYDANTIC.bat
│         └─ Other error? → Check error message
│
└─ NO → Do you need auto-reload?
          ├─ YES (actively coding) → Use start_backend_dev.bat
          └─ NO (just testing) → Use start_backend.bat ⭐
```

---

## 💡 Typical Workflow

### First Time Setup
1. Run `check_setup.bat` - Check everything is OK
2. If Pydantic errors: Run `FIX_PYDANTIC.bat`
3. Start with `start_backend.bat`

### Daily Development
1. Double-click `start_backend_dev.bat` (auto-reload)
2. Make code changes
3. Server restarts automatically
4. Test changes

### Testing/Demo
1. Double-click `start_backend.bat` (stable)
2. Test the application
3. Stop with Ctrl+C

---

## ⚡ Quick Start Commands

**Stable (no reload):**
```cmd
cd phase3-chatbot
venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
```

**Dev (with reload):**
```cmd
cd phase3-chatbot
venv\Scripts\python.exe -m pip install watchfiles
venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --reload
```

---

## 🐛 Troubleshooting

**Issue:** Multiprocessing errors with --reload

**Solution:** Use `start_backend.bat` (no reload) or `start_backend_dev.bat` (watchfiles)

**Issue:** Still getting Pydantic errors

**Solution:** Run `FIX_PYDANTIC.bat` then use `start_backend.bat`

**Issue:** Don't know what's wrong

**Solution:** Run `check_setup.bat` - it will tell you

---

## ✅ Recommended: Use start_backend.bat

For most use cases, `start_backend.bat` is the best choice:
- Most stable
- No multiprocessing issues
- Fast startup
- Works every time

Just restart it manually when you change code (Ctrl+C, then run again).

---

**Bottom Line:** When in doubt, use `start_backend.bat`! 🎯
