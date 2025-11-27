# 🐛 Railway "Application failed to respond" - Troubleshooting

## Problem: "Application failed to respond"

This error means Railway can't reach your app. Let's debug step by step.

---

## Step 1: Check Deployment Logs

1. Go to Railway → Your Service → **Deployments** tab
2. Click on the **latest deployment**
3. Scroll through the logs and look for:

### ✅ Good Signs:
- `Application startup complete`
- `Uvicorn running on http://0.0.0.0:PORT`
- `Started server process`
- No error messages

### ❌ Bad Signs:
- `ModuleNotFoundError`
- `ImportError`
- `Database connection failed`
- `Port already in use`
- `Application startup failed`

**Copy the error messages you see** - this will tell us what's wrong!

---

## Step 2: Verify Start Command

1. Go to Railway → Your Service → **Settings** → **Deploy** section
2. Check **Start Command** is exactly:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Make sure there's NO `cd finq-backend` in the command (Root Directory handles that)

---

## Step 3: Check Root Directory

1. Go to Railway → Your Service → **Settings** → **Build** section
2. Verify **Root Directory** is set to: `finq-backend`
3. If it's empty or wrong, set it to `finq-backend`

---

## Step 4: Check Environment Variables

1. Go to Railway → Your Service → **Variables** tab
2. Verify these are set:
   - ✅ `DATABASE_URL` (required!)
   - ✅ `GEMINI_API_KEY` (if using chat)
   - ✅ `FRED_API_KEY` (if using FRED)
   - ✅ `CORS_ORIGINS` (can be `*` for testing)

**Missing `DATABASE_URL` will cause the app to crash on startup!**

---

## Step 5: Common Issues & Fixes

### Issue 1: Database Connection Error

**Symptoms**: Logs show `OperationalError` or `Connection refused`

**Fix**:
1. Verify `DATABASE_URL` is set correctly in Variables
2. Check Supabase database is running
3. Test connection string format:
   ```
   postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```

### Issue 2: Missing Dependencies

**Symptoms**: Logs show `ModuleNotFoundError: No module named 'X'`

**Fix**:
1. Check `finq-backend/requirements.txt` has all dependencies
2. Verify `psycopg2-binary` is in requirements.txt (for PostgreSQL)
3. Redeploy to reinstall dependencies

### Issue 3: Port Binding Issue

**Symptoms**: Logs show `Address already in use` or port errors

**Fix**:
1. Make sure start command uses `--port $PORT` (not a hardcoded port)
2. Make sure host is `0.0.0.0` (not `127.0.0.1` or `localhost`)

### Issue 4: App Crashes on Startup

**Symptoms**: Logs show Python traceback or `Application startup failed`

**Fix**:
1. Check logs for the specific error
2. Common causes:
   - Missing environment variables
   - Database connection failed
   - Import errors
   - Syntax errors in code

---

## Step 6: Test Locally First

Before deploying, test your app locally with Railway's port:

```bash
cd finq-backend

# Set DATABASE_URL (use your Supabase URL)
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

# Set other required env vars
export GEMINI_API_KEY="your-key"
export FRED_API_KEY="your-key"
export CORS_ORIGINS="*"

# Run with Railway's typical port
PORT=8000 uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

If this works locally, the issue is with Railway configuration.

---

## Step 7: Check Railway Service Status

1. Go to Railway → Your Service
2. Check the status indicator:
   - 🟢 **Active** = Service is running
   - 🟡 **Deploying** = Still building
   - 🔴 **Failed** = Deployment failed

---

## Step 8: Redeploy from Scratch

If nothing works, try a fresh deployment:

1. **Delete and recreate** (if possible):
   - Delete the service
   - Create a new service
   - Reconnect to GitHub
   - Set Root Directory: `finq-backend`
   - Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add all environment variables
   - Deploy

2. **Or force redeploy**:
   - Go to Deployments tab
   - Click "Redeploy" on latest deployment

---

## 🔍 Debug Checklist

- [ ] Checked deployment logs for errors
- [ ] Verified Start Command is correct
- [ ] Verified Root Directory is `finq-backend`
- [ ] Verified `DATABASE_URL` is set
- [ ] Verified other required env vars are set
- [ ] Tested app locally with same config
- [ ] Service status shows "Active"
- [ ] No port conflicts in logs

---

## 📋 What to Share for Help

If you're still stuck, share:
1. **Deployment logs** (last 50-100 lines)
2. **Start Command** from Settings
3. **Root Directory** from Settings
4. **Environment Variables** (names only, not values)
5. **Service Status** (Active/Failed/Deploying)

---

**Most common issue: Missing `DATABASE_URL` or incorrect database connection string!** 🔑

