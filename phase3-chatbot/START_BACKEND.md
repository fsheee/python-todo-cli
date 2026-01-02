# How to Start the Backend (Step-by-Step)

This guide will help you fix the Pydantic error and start the backend successfully.

---

## 🎯 Step 1: Open Terminal in Project

```cmd
cd F:\claude-code\hackathon-todo\phase3-chatbot
```

---

## 🎯 Step 2: Activate Virtual Environment

**Windows (CMD):**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your prompt.

---

## 🎯 Step 3: Fix Pydantic (One-Time Fix)

**Copy and paste this entire command block:**

```cmd
pip uninstall pydantic pydantic-core pydantic-settings -y && pip install pydantic==1.10.13
```

**Or run line by line:**
```cmd
pip uninstall pydantic pydantic-core pydantic-settings -y
pip install pydantic==1.10.13
```

**Verify it worked:**
```cmd
python -c "import pydantic; print(pydantic.VERSION)"
```

Should output: `1.10.13`

---

## 🎯 Step 4: Start the Backend

```cmd
python -m uvicorn app.main:app --port 8001 --reload
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['F:\\claude-code\\hackathon-todo\\phase3-chatbot']
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🚀 Phase 3 Chatbot starting...
Python version: 3.13.7
Environment: development
✅ File storage ready
✅ Chat router loaded
INFO:     Application startup complete.
```

---

## 🎯 Step 5: Test the Backend

**Open a NEW terminal** and test:

```cmd
curl http://localhost:8001/
```

Or open in browser: http://localhost:8001/

Should see:
```json
{"message":"Phase 3 Chatbot API","version":"1.0.0","status":"running"}
```

---

## 🎯 Step 6: Start the Frontend

**Open ANOTHER terminal:**

```cmd
cd F:\claude-code\hackathon-todo\phase3-chatbot\frontend
npm run dev
```

Should see:
```
  ▲ Next.js 14.2.35
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Ready in 2.1s
```

---

## 🎯 Step 7: Test Login Page

1. Open browser: http://localhost:3000/login
2. Enter credentials:
   - Email: fsheekhi@gmail.com
   - Password: Afsheen123
3. Click "Sign In"

**Expected:**
- ✅ No connection error
- ⚠️ May show "Invalid credentials" (if user doesn't exist)
- ✅ But connection works!

---

## ✅ Success Checklist

- [ ] Virtual environment activated (shows `(venv)`)
- [ ] Pydantic version is 1.10.13
- [ ] Backend starts without errors
- [ ] Backend responds on http://localhost:8001/
- [ ] Frontend runs on http://localhost:3000
- [ ] Login page loads with beautiful UI
- [ ] No "Unable to connect" error

---

## ❌ Troubleshooting

### Error: "No module named 'uvicorn'"

**Fix:**
```cmd
pip install uvicorn
```

### Error: "Port 8001 already in use"

**Fix (Windows):**
```cmd
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### Error: Still getting Pydantic error

**Fix: Force reinstall in venv**
```cmd
venv\Scripts\activate
pip install --force-reinstall --no-cache-dir pydantic==1.10.13
```

### Error: "Cannot activate venv"

**Fix: Recreate venv**
```cmd
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements-py313.txt
```

---

## 📸 Visual Confirmation

### Terminal 1 (Backend):
```
(venv) F:\...\phase3-chatbot> python -m uvicorn app.main:app --port 8001 --reload
INFO:     Uvicorn running on http://127.0.0.1:8001 ✓
```

### Terminal 2 (Frontend):
```
F:\...\phase3-chatbot\frontend> npm run dev
Local:        http://localhost:3000 ✓
```

### Browser:
```
Beautiful login page with:
✨ Gradient background
🔮 Glass morphism card
📧 Email input with icon
🔒 Password input with toggle
🚀 Sign In button
```

---

## 🎉 Done!

You should now have:
- ✅ Backend running on port 8001
- ✅ Frontend running on port 3000
- ✅ Beautiful login page working
- ✅ No connection errors

**Next:** Test the actual authentication with real credentials or create a test user!
