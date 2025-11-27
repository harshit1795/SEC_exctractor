# 🔧 Railway Deployment Fix: "No start command found"

## Problem

Railway shows: `✖ No start command was found`

This happens because Railway needs to know:
1. **Root Directory**: Where your backend code is (`finq-backend`)
2. **Start Command**: How to run your app

---

## ✅ Solution: Configure in Railway Dashboard

### Step 1: Set Root Directory

**Note**: Railway's UI may show this as "Root Directory", "Working Directory", or it might be in a different location.

1. Go to your Railway project
2. Click on your **service** (the deployed app)
3. Go to **Settings** tab
4. Scroll to **"Build"** section
5. Look for one of these fields:
   - **Root Directory** (most common)
   - **Working Directory**
   - **Base Directory**
6. Set the value to: `finq-backend` (without leading slash)
7. Save

**If you don't see Root Directory but see "Watch Paths"**:
- Watch Paths is different - it's for triggering redeployments
- Root Directory might be in a different section or named differently
- Try looking in the **"Deploy"** section as well
- Alternatively, use the `railway.json` file method (see below)

### Step 2: Set Start Command

1. Still in **Settings** → **"Deploy"** section
2. Set **Start Command**: 
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Save

### Step 3: Redeploy

1. Go to **Deployments** tab
2. Click **"Redeploy"** or **"Deploy"**
3. Railway will use your configured settings

---

## ✅ Alternative: Use Configuration Files

I've created configuration files that Railway will auto-detect:

### Files Created:
- `finq-backend/railway.toml` - **Primary config** - Sets root directory and start command
- `finq-backend/railway.json` - Alternative Railway config format
- `finq-backend/nixpacks.toml` - Tells Railway how to build and run
- `finq-backend/Procfile` - Heroku/Railway standard

**These files are already in your repo**, so Railway should detect them automatically.

**Important**: The `railway.toml` file in `finq-backend/` sets:
- `root = "finq-backend"` - But this is relative to where the file is located
- Since the file is IN `finq-backend/`, Railway will use that directory as root

**If Railway still can't find the root**, you may need to:
1. Move `railway.toml` to the **repository root** (not in `finq-backend/`)
2. Or set Root Directory manually in Railway dashboard

---

## 🔍 Verify Configuration

After setting up, check:

1. **Settings → Build**:
   - Root Directory: `finq-backend` ✅

2. **Settings → Deploy**:
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` ✅

3. **Deployment Logs**:
   - Should show: `Starting: uvicorn app.main:app...`
   - Should show: `Application startup complete`

---

## 🐛 If Still Not Working

### Check 1: Root Directory Path

Make sure Root Directory is set to `finq-backend` (not `./finq-backend` or `/finq-backend`)

### Check 2: Start Command Format

The start command should be exactly:
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Not**:
- `python -m uvicorn...` (Railway handles this)
- `cd finq-backend && uvicorn...` (Root directory handles this)

### Check 3: Requirements File

Make sure `finq-backend/requirements.txt` exists and has all dependencies.

### Check 4: Main Module

Verify `finq-backend/app/main.py` exists and has the FastAPI app.

---

## 📋 Quick Checklist

- [ ] Root Directory set to `finq-backend` in Settings → Build
- [ ] Start Command set in Settings → Deploy
- [ ] Branch selected correctly (Settings → Source)
- [ ] Environment variables set (Variables tab)
- [ ] Redeployed after configuration changes

---

## 🚀 Expected Deployment Flow

Once configured correctly, you should see:

```
↳ Detected Python
↳ Using pip
↳ Installing dependencies...
↳ Starting: uvicorn app.main:app --host 0.0.0.0 --port $PORT
✓ Application startup complete
```

---

**After setting Root Directory and Start Command, click "Redeploy" and it should work!** 🎉

