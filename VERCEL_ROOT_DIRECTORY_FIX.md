# 🔧 Fix: "No Next.js version detected" in Vercel

## Problem
Vercel error: "No Next.js version detected. Make sure your package.json has 'next' in either 'dependencies' or 'devDependencies'. Also check your Root Directory setting matches the directory of your package.json file."

**Root Cause**: Vercel is looking for `package.json` in the repo root, but it's actually in `finq-frontend/` directory.

---

## ✅ Solution: Set Root Directory in Vercel

### Step 1: Go to Project Settings

1. In Vercel, go to your project
2. Click **Settings** tab
3. Click **General** (in left sidebar)

### Step 2: Set Root Directory

1. Scroll down to **"Root Directory"** section
2. Click **"Edit"** or the field
3. Enter: `finq-frontend`
4. Click **"Save"**

### Step 3: Redeploy

1. Go to **Deployments** tab
2. Click **"Redeploy"** on the latest deployment
3. Or create a new deployment

Vercel will now look for `package.json` in `finq-frontend/` directory!

---

## Alternative: Set During Deployment

If you're creating a new deployment:

1. Go to **Deployments** tab
2. Click **"Create Deployment"** or **"Deploy"**
3. In the deployment dialog:
   - **Branch**: `feature/nexus5.1_c_test`
   - **Root Directory**: `finq-frontend` ⚠️ **Set this!**
   - **Production**: ✅ Check
4. Deploy

---

## Verify Root Directory

After setting, verify:
1. **Settings** → **General** → **Root Directory** should show: `finq-frontend`
2. The path should be relative to repo root (not absolute)

---

## Expected Build Log After Fix

After setting Root Directory correctly, you should see:
```
Installing dependencies...
Found Next.js version: 16.0.3
Running "next build"
```

Instead of:
```
Error: No Next.js version detected
```

---

## 📋 Quick Checklist

- [ ] Go to Settings → General
- [ ] Set Root Directory to `finq-frontend`
- [ ] Save
- [ ] Redeploy or create new deployment
- [ ] Build should now find Next.js

---

**Set Root Directory to `finq-frontend` in Settings → General, then redeploy!** 🚀

