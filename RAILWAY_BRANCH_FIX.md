# 🔧 Railway Branch Selection - Step by Step

## Problem: Branch Selection Not Showing

If Railway doesn't show branch selection after selecting your repo, follow these steps:

---

## Solution: Set Branch After Project Creation

### Step 1: Create Project (Any Branch Works Initially)

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `SEC_exctractor`
5. **Don't worry about branch yet** - just continue and create the project
6. Railway will deploy from `main` or `master` by default

### Step 2: Change Branch in Settings

After the project is created:

1. **Click on your service** (the deployed app card)
2. Go to **Settings** tab (gear icon or "Settings" button)
3. Scroll down to **"Source"** section
4. You'll see:
   - **Repository**: Your GitHub repo
   - **Branch**: Dropdown with available branches
5. **Click the Branch dropdown**
6. Select your branch: `feature/nexus5.1_c_test`
7. **Save** or Railway will auto-save

### Step 3: Railway Will Auto-Redeploy

- Railway will automatically detect the branch change
- It will trigger a new deployment from your selected branch
- Watch the deployment logs to confirm it's using the correct branch

---

## Alternative: Using Railway CLI (More Control)

If the web UI doesn't work, use Railway CLI:

### Install Railway CLI

```bash
npm i -g @railway/cli
```

### Login and Link

```bash
# Login to Railway
railway login

# Navigate to your backend directory
cd finq-backend

# Link to Railway project (will prompt you to select project)
railway link

# Switch to your branch locally
git checkout feature/nexus5.1_c_test

# Deploy from current branch
railway up
```

This will deploy whatever branch you're currently on.

---

## Verify Branch is Set Correctly

### Method 1: Check Settings

1. Go to your service → Settings → Source
2. Verify the branch shows: `feature/nexus5.1_c_test`

### Method 2: Check Deployment Logs

1. Go to your service → **Deployments** tab
2. Click on the latest deployment
3. Check the logs - it should show which branch was used
4. Look for: `Cloning from branch: feature/nexus5.1_c_test`

### Method 3: Check Build Logs

In the deployment logs, you should see:
```
Cloning repository...
Checking out branch: feature/nexus5.1_c_test
```

---

## Troubleshooting

### Branch Still Not Showing

**Issue**: Branch dropdown is empty or doesn't show your branch

**Solutions**:

1. **Make sure branch is pushed to GitHub**:
   ```bash
   git push origin feature/nexus5.1_c_test
   ```

2. **Refresh Railway connection**:
   - Go to Settings → Source
   - Click "Disconnect" (if available)
   - Reconnect GitHub
   - Branch list should refresh

3. **Wait a moment**: Sometimes Railway needs a few seconds to fetch branches

4. **Check branch name**: Make sure it matches exactly (case-sensitive)

### Railway Deploying Wrong Branch

**Solution**:
1. Go to Settings → Source
2. Manually select your branch again
3. Trigger a new deployment (Settings → Redeploy, or push a commit)

### Can't Find Settings Tab

**Solution**:
- Click on your **service** (not the project)
- Settings should be in the top menu or sidebar
- Look for gear icon ⚙️ or "Settings" text

---

## Quick Reference

**Path to Branch Setting**:
```
Railway Dashboard → Your Project → Your Service → Settings → Source → Branch
```

**Current Branch**: `feature/nexus5.1_c_test`

**What to Set**:
- Root Directory: `finq-backend`
- Branch: `feature/nexus5.1_c_test`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## Recommended Workflow

1. **Create project** in Railway (deploys from main/master)
2. **Set branch** in Settings → Source → Branch
3. **Set root directory** in Settings → Build → Root Directory: `finq-backend`
4. **Add environment variables** in Variables tab
5. **Verify deployment** uses correct branch from logs

---

**Once the branch is set, Railway will automatically deploy from that branch whenever you push to it!** 🚀

