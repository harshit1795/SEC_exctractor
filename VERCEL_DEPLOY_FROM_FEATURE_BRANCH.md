# 🚀 Deploy Vercel from Feature Branch (When Main Doesn't Have Frontend)

## Problem
- `main` branch = old Streamlit deployment (no `finq-frontend`)
- `feature/nexus5.1_c_test` branch = has `finq-frontend`
- Vercel import only shows `main` branch

## ✅ Solution: Deploy from Feature Branch After Import

### Option 1: Use Deployments Tab (Easiest)

**Step 1: Import Project (Use Any Branch)**
1. Import with `main` branch (it doesn't matter - we'll change it)
2. **Skip Root Directory** for now (or set it to `/` or leave empty)
3. **Skip environment variables** for now (we'll add them after)
4. Click **"Deploy"** - it will fail, but that's okay!

**Step 2: Deploy from Feature Branch**
1. After project is created (even if deployment failed), go to **Deployments** tab
2. Click **"Create Deployment"** or **"Deploy"** button
3. In the deployment dialog:
   - **Branch**: Select `feature/nexus5.1_c_test` (should now be visible!)
   - **Root Directory**: `finq-frontend`
   - **Production**: Check this box
4. Click **"Deploy"**

**Step 3: Add Environment Variables**
1. Go to **Settings** → **Environment Variables**
2. Add all Firebase and API URL variables
3. Vercel will automatically redeploy with new variables

---

### Option 2: Use Vercel CLI (Most Reliable)

This bypasses the UI entirely and works perfectly:

```bash
# Install Vercel CLI (if not installed)
npm i -g vercel

# Login to Vercel
vercel login

# Navigate to frontend directory
cd finq-frontend

# Deploy from feature branch
vercel --prod --branch feature/nexus5.1_c_test
```

**During deployment, Vercel CLI will ask:**
- Link to existing project? → **Yes** (if you already created the project)
- Or create new project? → **Yes** (if starting fresh)
- Root Directory? → `./` (since you're already in `finq-frontend`)
- Environment variables? → Add them via CLI or web UI later

---

### Option 3: Import Then Immediately Redeploy

**Step 1: Import Project**
1. Import with `main` branch
2. Set Root Directory to `/` (or leave empty)
3. Click **"Deploy"** (it will fail - that's expected)

**Step 2: Configure for Feature Branch**
1. Go to **Settings** → **Environments** → **Production**
2. Set **Production Branch** to `feature/nexus5.1_c_test`
3. Go to **Settings** → **General**
4. Set **Root Directory** to `finq-frontend`
5. Add environment variables
6. Go to **Deployments** → **Redeploy** or create new deployment

---

## 🎯 Recommended: Option 2 (Vercel CLI)

**This is the cleanest approach:**

```bash
# 1. Install and login
npm i -g vercel
vercel login

# 2. Navigate to frontend
cd finq-frontend

# 3. Deploy from feature branch
vercel --prod --branch feature/nexus5.1_c_test
```

**Benefits:**
- ✅ Works regardless of UI limitations
- ✅ Deploys directly from your feature branch
- ✅ Sets root directory correctly
- ✅ Can add environment variables via CLI or web UI

---

## 📋 Environment Variables Setup

After deployment (via any method), add these in **Settings** → **Environment Variables**:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=...
NEXT_PUBLIC_API_URL=https://secexctractor-production.up.railway.app/api
```

---

## ✅ Quick Decision

**If you want the easiest path:**
→ Use **Vercel CLI** (Option 2) - it's the most reliable

**If you prefer web UI:**
→ Import with `main` → Deployments tab → Deploy from `feature/nexus5.1_c_test`

---

**I recommend using Vercel CLI - it's the most straightforward for this situation!** 🚀

