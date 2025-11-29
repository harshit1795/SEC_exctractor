# 🔧 Fix: "uvicorn: command not found" in Railway

## Problem

Railway logs show:
```
/bin/bash: line 1: uvicorn: command not found
```

This means `uvicorn` isn't in the system PATH.

---

## ✅ Solution: Use `python -m uvicorn`

Instead of calling `uvicorn` directly, use Python's module execution:

**Change from:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**To:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Steps to Fix

### Step 1: Update Railway Settings

1. Go to Railway → Your Service → **Settings** → **Deploy** section
2. Find **Start Command** field
3. Change it to:
   ```
   python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. **Save**

### Step 2: Redeploy

1. Go to **Deployments** tab
2. Click **"Redeploy"** on the latest deployment
3. Or push a new commit to trigger redeployment

---

## Alternative: Update Config Files

I've updated these files in your repo:
- `finq-backend/railway.json`
- `railway.toml`
- `finq-backend/nixpacks.toml`
- `finq-backend/Procfile`

**Push these changes:**
```bash
git add finq-backend/railway.json railway.toml finq-backend/nixpacks.toml finq-backend/Procfile
git commit -m "Fix: Use python -m uvicorn for Railway deployment"
git push origin feature/nexus5.1_c_test
```

Railway will auto-detect the updated config files.

---

## Why This Happens

Railway's Python environment might not have `uvicorn` in the system PATH, but it's available as a Python module. Using `python -m uvicorn` ensures Python can find and execute uvicorn correctly.

---

## Verify Fix

After redeploying, check logs for:
- ✅ `Started server process`
- ✅ `Uvicorn running on http://0.0.0.0:PORT`
- ✅ `Application startup complete`
- ❌ No more "command not found" errors

---

**After updating the start command, redeploy and it should work!** 🚀

