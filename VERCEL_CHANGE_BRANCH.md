# 🌿 How to Change Branch in Vercel (When Production Branch Option Not Visible)

## Problem: Don't see "Production Branch" in Settings → Git

Vercel's UI can vary. Here are alternative ways to change the branch:

---

## ✅ Method 1: Deploy from Branch (Recommended)

### Step 1: Go to Deployments
1. In your Vercel project, click **"Deployments"** tab
2. You'll see a list of deployments

### Step 2: Create New Deployment from Branch
1. Click **"Create Deployment"** or **"Deploy"** button (usually top right)
2. You'll see options:
   - **Branch**: Select `feature/nexus5.1_c_test`
   - **Production**: Check this box if you want it as production
3. Click **"Deploy"**

This will deploy from your branch and set it as the active deployment.

---

## ✅ Method 2: Settings → Git → Connected Repository

1. Go to **Settings** → **Git**
2. Look for **"Connected Git Repository"** section
3. You might see:
   - **"Change Branch"** or **"Edit"** button
   - Click it to change the branch
4. Or you might see the branch listed - click to change it

---

## ✅ Method 3: Use Vercel CLI

If the UI doesn't work, use CLI:

```bash
# Install Vercel CLI (if not installed)
npm i -g vercel

# Login
vercel login

# Navigate to frontend directory
cd finq-frontend

# Link to your project (if not already linked)
vercel link

# Deploy from specific branch as production
vercel --prod --branch feature/nexus5.1_c_test
```

---

## ✅ Method 4: Delete and Re-import Project

If nothing else works:

1. **Delete the current project** in Vercel:
   - Settings → General → Delete Project
2. **Re-import** the project:
   - Add New → Project
   - Select repository
   - **This time, try refreshing or waiting a moment** - branches might load
   - Select `feature/nexus5.1_c_test` if it appears
   - If not, proceed with `main` and use Method 1 above

---

## ✅ Method 5: Check Deployments Tab

1. Go to **Deployments** tab
2. Look at existing deployments
3. You might see branch names next to each deployment
4. Click on a deployment from `main`
5. Look for **"Redeploy"** or **"Deploy from Branch"** option
6. Select `feature/nexus5.1_c_test` when redeploying

---

## 🎯 Quick Solution: Deploy from Branch

**Easiest method** - Use the Deployments tab:

1. **Deployments** tab → **"Create Deployment"** or **"Deploy"**
2. Select branch: `feature/nexus5.1_c_test`
3. Check **"Production"** checkbox
4. Deploy

This will create a new deployment from your branch and make it production.

---

## 📍 Where to Find Branch Settings

The branch setting might be in different places depending on Vercel's UI:

- **Settings → Git** → Look for branch dropdown or "Change" button
- **Deployments** → "Create Deployment" → Branch selector
- **Project Overview** → Branch indicator (might be clickable)

---

## 🔍 If Still Can't Find It

**Use Vercel CLI** - it's the most reliable method:

```bash
cd finq-frontend
vercel --prod --branch feature/nexus5.1_c_test
```

This will:
- Deploy from your branch
- Set it as production
- Work regardless of UI changes

---

**Try Method 1 (Deployments → Create Deployment) first - it's usually the easiest!** 🚀

