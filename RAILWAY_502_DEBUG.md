# 🔍 Railway 502 Error - Comprehensive Debugging Guide

## Current Status
- ✅ Config files updated to use `python -m uvicorn`
- ❌ Still getting 502 error on Railway

## Step-by-Step Debugging

### Step 1: Verify Changes Were Deployed

**Check if the new start command is actually being used:**

1. Go to Railway → Your Service → **Deployments** → Latest deployment
2. Look at the **deployment metadata** or **logs**
3. Check what start command Railway is actually using
4. It should show: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**If it still shows the old command:**
- The changes haven't been deployed yet
- **Solution:** Push the changes and trigger a new deployment

---

### Step 2: Check Railway Dashboard Settings

**Railway Dashboard settings can override config files!**

1. Go to Railway → Your Service → **Settings** → **Deploy** section
2. Check the **Start Command** field
3. **If it's set in the dashboard, it overrides config files!**

**Fix:**
- Either:
  - **Option A:** Set it in dashboard to: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - **Option B:** Clear/delete the start command in dashboard (let config files handle it)

---

### Step 3: Check Railway Logs for Errors

**This is the most important step!**

1. Go to Railway → Your Service → **Deployments** → Latest → **Logs**
2. Scroll through ALL the logs
3. Look for these specific errors:

#### Common Error #1: Module Not Found
```
ModuleNotFoundError: No module named 'uvicorn'
ModuleNotFoundError: No module named 'fastapi'
```
**Fix:** Dependencies not installed properly

#### Common Error #2: Database Connection
```
OperationalError: could not connect to server
Connection refused
```
**Fix:** `DATABASE_URL` missing or incorrect

#### Common Error #3: Import Error
```
ImportError: cannot import name 'X' from 'app.Y'
```
**Fix:** Code error or missing dependency

#### Common Error #4: Port Already in Use
```
Address already in use
```
**Fix:** Port conflict (shouldn't happen with `$PORT`)

#### Common Error #5: App Crashes on Startup
```
Application startup failed
Traceback (most recent call last):
```
**Fix:** Check the traceback for the specific error

---

### Step 4: Verify Environment Variables

1. Go to Railway → Your Service → **Variables** tab
2. **Verify these are set:**

#### Required Variables:
- ✅ `DATABASE_URL` - **CRITICAL!** Must be set or app will crash
  - Format: `postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
  - **No quotes needed** in Railway dashboard

#### Optional but Recommended:
- `CORS_ORIGINS` - Should include your Vercel domain
- `GEMINI_API_KEY` - If using chat features
- `FRED_API_KEY` - If using FRED data
- `FIREBASE_CREDENTIALS_B64` - For Firebase admin

**Test DATABASE_URL:**
If `DATABASE_URL` is missing or wrong, the app will crash immediately on startup.

---

### Step 5: Check Root Directory

1. Go to Railway → Your Service → **Settings** → **Build** section
2. Verify **Root Directory** is set to: `finq-backend`
3. **If it's empty or wrong, the app won't find the code!**

---

### Step 6: Check Build Logs

1. Go to Railway → Your Service → **Deployments** → Latest
2. Look at the **Build** phase logs
3. Check for:
   - ✅ `Successfully installed uvicorn`
   - ✅ `Successfully installed fastapi`
   - ✅ `Successfully installed psycopg2-binary`
   - ❌ Any `ERROR` or `FAILED` messages

---

### Step 7: Test the Health Endpoint Directly

**If the app is running but returning 502, try:**

```bash
curl https://secexctractor-production.up.railway.app/api/health
```

**Expected response:**
```json
{"status":"healthy","database_configured":true}
```

**If you get:**
- `502 Bad Gateway` → App not running or crashed
- `Connection refused` → App not listening on port
- `404 Not Found` → Wrong URL or routing issue
- `500 Internal Server Error` → App running but has an error

---

### Step 8: Check Service Status

1. Go to Railway → Your Service
2. Look at the status indicator:
   - 🟢 **Active** = Should be working
   - 🟡 **Deploying** = Still building/deploying
   - 🔴 **Failed** = Deployment failed
   - ⚪ **Stopped** = Service stopped

---

## Quick Fixes to Try

### Fix 1: Force Redeploy

1. Railway → Deployments → Latest
2. Click **"Redeploy"**
3. Wait for deployment to complete
4. Check logs again

### Fix 2: Update Start Command in Dashboard

1. Railway → Settings → Deploy
2. Set **Start Command** to:
   ```
   python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. **Save**
4. Redeploy

### Fix 3: Verify DATABASE_URL

1. Railway → Variables
2. Check `DATABASE_URL` is set
3. Format should be:
   ```
   postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres
   ```
4. **No quotes** around the value in Railway

### Fix 4: Check for Python Version Issues

Railway might be using a different Python version. Check:
1. Railway → Deployments → Latest → Build logs
2. Look for: `Python 3.x.x`
3. If it's Python 3.13, make sure all dependencies are compatible

---

## Most Likely Causes (in order)

1. **Start command not updated in Railway dashboard** (overrides config files)
2. **DATABASE_URL missing or incorrect** (app crashes on startup)
3. **Dependencies not installed** (ModuleNotFoundError)
4. **App crashes on startup** (check logs for traceback)
5. **Port binding issue** (unlikely with `$PORT`)

---

## What to Share for Help

If you're still stuck, share:

1. **Railway Logs** (last 50-100 lines)
2. **Start Command** from Railway Settings
3. **Environment Variables** (names only, not values)
4. **Root Directory** setting
5. **Service Status** (Active/Deploying/Failed)

---

## Next Steps

1. **Check Railway logs** - This will tell us exactly what's wrong
2. **Verify start command in dashboard** - Make sure it matches our fix
3. **Verify DATABASE_URL** - Most common cause of crashes
4. **Share the error logs** - So we can pinpoint the exact issue

**The logs will tell us exactly what's wrong!** 🔍

