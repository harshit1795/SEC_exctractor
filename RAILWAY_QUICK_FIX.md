# ⚡ Railway 502 Error - Quick Fix Checklist

## 🎯 Most Common Issue: Railway Dashboard Overrides Config Files

**Railway Dashboard settings take priority over config files!**

### ✅ Fix Step 1: Update Start Command in Railway Dashboard

1. Go to **Railway** → Your Service → **Settings** → **Deploy** section
2. Find **"Start Command"** field
3. **Set it to exactly:**
   ```
   python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. **Click "Save"**
5. Go to **Deployments** → Click **"Redeploy"**

---

## 🔍 Step 2: Check Railway Logs

**This will tell you exactly what's wrong!**

1. Railway → Service → **Deployments** → Latest deployment
2. Click **"Logs"** tab
3. Scroll to the **bottom** (most recent logs)
4. Look for:

### ✅ Good Signs:
- `Started server process`
- `Uvicorn running on http://0.0.0.0:PORT`
- `Application startup complete`

### ❌ Bad Signs (copy these errors):
- `ModuleNotFoundError: No module named 'X'`
- `OperationalError: could not connect to server`
- `ImportError: cannot import name 'X'`
- `Application startup failed`
- Any Python traceback

**Share the error message you see!**

---

## 🔧 Step 3: Verify Critical Settings

### A. Root Directory
- Railway → Settings → **Build** section
- **Root Directory** should be: `finq-backend`

### B. Environment Variables
- Railway → **Variables** tab
- **Must have:** `DATABASE_URL` (required!)
- Format: `postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres`
- **No quotes** in Railway dashboard

### C. Start Command (in Dashboard)
- Railway → Settings → **Deploy** section
- Should be: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 🚀 Step 4: Push Updated Config Files

I've updated these files:
- ✅ `finq-backend/railway.json`
- ✅ `railway.toml` (root)
- ✅ `finq-backend/railway.toml`
- ✅ `finq-backend/nixpacks.toml`

**Push them:**
```bash
git add finq-backend/railway.json railway.toml finq-backend/railway.toml finq-backend/nixpacks.toml
git commit -m "Fix: Update Railway start command to python -m uvicorn"
git push origin feature/nexus5.1_c_test
```

---

## 📋 Quick Diagnostic Commands

**Test if backend is responding:**
```bash
curl https://secexctractor-production.up.railway.app/api/health
```

**Expected:** `{"status":"healthy","database_configured":true}`

**If you get 502:** App is not running (check logs)
**If you get 500:** App is running but has an error (check logs)

---

## 🎯 Most Likely Issues (in order)

1. **Start command in Railway dashboard is wrong** ← **Check this first!**
2. **DATABASE_URL missing or incorrect** ← **Second most common!**
3. **App crashing on startup** ← **Check logs for traceback**
4. **Dependencies not installed** ← **Check build logs**

---

## 💡 Pro Tip

**Railway Dashboard settings override config files!**

Even if config files are correct, if the dashboard has a different start command, it will use the dashboard setting.

**Solution:** Either:
- Set it correctly in the dashboard, OR
- Clear/delete the start command in dashboard (let config files handle it)

---

**After updating the dashboard start command and redeploying, check the logs to see if it's working!** 🔍

