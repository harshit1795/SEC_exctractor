# 🚀 Vercel Parallel Deployment Guide

This guide shows you how to create a **new Vercel deployment** for your Render branch while **keeping your existing Railway deployment unchanged**.

## 📋 Overview

You'll have **two separate Vercel deployments**:

1. **Production (Railway)**: `main` branch → Uses Railway backend
2. **Render Branch**: `feature/nexus5.1_c_Rail_alt` → Uses Render backend

Both deployments will be independent and can run simultaneously.

---

## 🎯 Step-by-Step: Create New Vercel Deployment

### Option A: Create New Project (Recommended) ⭐

This creates a completely separate project in Vercel, making it easier to manage.

#### Step 1: Go to Vercel Dashboard

1. Open https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**

#### Step 2: Import Repository

1. **Select your repository**: `SEC_exctractor`
2. Click **"Import"**

#### Step 3: Configure Project

**Project Settings:**
- **Project Name**: `finq-frontend-render` (or any name you prefer)
- **Framework Preset**: Next.js (should auto-detect)
- **Root Directory**: `finq-frontend`
- **Build Command**: `npm run build` (default)
- **Output Directory**: `.next` (default)
- **Install Command**: `npm install` (default)

**Git Settings:**
- **Production Branch**: `feature/nexus5.1_c_Rail_alt` ⚠️ **Important!**
- **Preview Branches**: All branches (or specific ones)

#### Step 4: Set Environment Variables

Click **"Environment Variables"** and add:

**For Render Backend:**
```bash
# Backend API URL (Render)
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api

# Firebase (same as your Railway deployment)
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_storage_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id
```

**Important Notes:**
- ✅ Replace `your-render-service.onrender.com` with your **actual Render service URL**
- ✅ Use the **same Firebase config** as your Railway deployment (they can share Firebase)
- ✅ Set these for **Production, Preview, and Development** environments

#### Step 5: Deploy

1. Click **"Deploy"**
2. Wait for build to complete (2-5 minutes)
3. Your new deployment will be live at: `https://finq-frontend-render.vercel.app` (or your custom domain)

#### Step 6: Update Render CORS

**Important**: Add your new Vercel URL to Render's CORS settings!

1. Go to **Render Dashboard** → Your Service → **Environment**
2. Update `CORS_ORIGINS` to include your new Vercel URL:
   ```
   https://sec-exctractor.vercel.app,https://finq-frontend-render.vercel.app,https://sec-exctractor-git-*.vercel.app
   ```
3. **Redeploy** Render service (or it will auto-update)

---

### Option B: Add Branch to Existing Project

If you prefer to keep everything in one Vercel project, you can configure branch-specific environment variables.

#### Step 1: Go to Project Settings

1. Open your existing Vercel project
2. Go to **Settings** → **Git**

#### Step 2: Configure Branch

1. Under **"Production Branch"**, you can keep it as `main`
2. Vercel will automatically create preview deployments for other branches

#### Step 3: Set Branch-Specific Environment Variables

1. Go to **Settings** → **Environment Variables**
2. For each variable, you can set it for specific environments:
   - **Production** (main branch)
   - **Preview** (all other branches)
   - **Development** (local)

**For Render Branch:**
1. Click **"Add New"**
2. Add `NEXT_PUBLIC_API_URL`
3. Set value: `https://your-render-service.onrender.com/api`
4. Select **"Preview"** environment only (this applies to all non-main branches)
5. Click **"Save"**

**For Railway Branch (keep existing):**
1. Find existing `NEXT_PUBLIC_API_URL`
2. Make sure it's set for **"Production"** environment only
3. Value should be: `https://secexctractor-production-80f5.up.railway.app/api`

**Result:**
- `main` branch → Uses Railway URL (Production env)
- `feature/nexus5.1_c_Rail_alt` → Uses Render URL (Preview env)

#### Step 4: Deploy

1. Push to `feature/nexus5.1_c_Rail_alt` branch
2. Vercel will automatically create a preview deployment
3. Preview URL: `https://sec-exctractor-git-feature-nexus5-1-c-rail-alt-[hash].vercel.app`

---

## 🔍 How to Identify Which Backend You're Using

### Check Environment Variable

In your Vercel deployment:
1. Go to **Settings** → **Environment Variables**
2. Check `NEXT_PUBLIC_API_URL` value
3. Railway: `https://secexctractor-production-80f5.up.railway.app/api`
4. Render: `https://your-render-service.onrender.com/api`

### Check in Browser Console

1. Open your deployed frontend
2. Open browser DevTools (F12)
3. Go to **Console** tab
4. Type: `console.log(process.env.NEXT_PUBLIC_API_URL)`
5. Or check Network tab to see API calls going to which backend

---

## 📊 Deployment Comparison

| Deployment | Branch | Backend | URL Pattern |
|------------|--------|---------|-------------|
| **Production (Railway)** | `main` | Railway | `https://sec-exctractor.vercel.app` |
| **Render Preview** | `feature/nexus5.1_c_Rail_alt` | Render | `https://sec-exctractor-git-feature-nexus5-1-c-rail-alt-[hash].vercel.app` |
| **Render Production** (if new project) | `feature/nexus5.1_c_Rail_alt` | Render | `https://finq-frontend-render.vercel.app` |

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] **New Vercel deployment created**
- [ ] **Environment variables set correctly**
  - [ ] `NEXT_PUBLIC_API_URL` points to Render
  - [ ] Firebase config is set
- [ ] **Render CORS updated** with new Vercel URL
- [ ] **Deployment successful** (no build errors)
- [ ] **Frontend loads** correctly
- [ ] **API calls work** (check Network tab in DevTools)
- [ ] **FinQ Chat works** (test with Render backend)
- [ ] **Existing Railway deployment still works** (verify it wasn't affected)

---

## 🔧 Troubleshooting

### Issue: CORS Errors on New Deployment

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
1. Go to Render Dashboard → Environment
2. Add your new Vercel URL to `CORS_ORIGINS`
3. Format: `https://your-new-vercel-url.vercel.app`
4. Redeploy Render service

### Issue: Wrong Backend URL

**Problem**: Frontend is calling wrong backend

**Solution**:
1. Check Vercel Environment Variables
2. Verify `NEXT_PUBLIC_API_URL` is set correctly
3. **Redeploy** Vercel (environment variables require redeploy to take effect)

### Issue: Build Fails

**Error**: Build errors in Vercel

**Solution**:
1. Check build logs in Vercel Dashboard
2. Verify `finq-frontend/package.json` exists
3. Verify `finq-frontend/next.config.ts` is valid
4. Check if all dependencies are in `package.json`

### Issue: Preview Deployment Uses Wrong Environment

**Problem**: Preview deployment uses Production environment variables

**Solution**:
1. Go to Vercel → Settings → Environment Variables
2. For each variable, check which environments it's set for
3. Make sure `NEXT_PUBLIC_API_URL` is set for **Preview** environment for Render branch

---

## 🎯 Recommended Approach

**I recommend Option A (New Project)** because:

✅ **Clear separation**: Easy to see which is which
✅ **Independent management**: Can delete/modify one without affecting the other
✅ **Different domains**: Easier to test and compare
✅ **Production-ready**: Can promote Render deployment to production later

---

## 📝 Quick Reference

### Render Service URL
```
https://your-service-name.onrender.com
```

### Vercel Deployment URLs
- **Railway (Production)**: `https://sec-exctractor.vercel.app`
- **Render (New)**: `https://finq-frontend-render.vercel.app` (or preview URL)

### Environment Variables to Set
```bash
# Render deployment
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api

# Firebase (same for both)
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
# ... (all other Firebase vars)
```

---

## 🚀 Next Steps

1. ✅ **Create new Vercel deployment** (follow steps above)
2. ✅ **Set environment variables** (Render URL + Firebase)
3. ✅ **Update Render CORS** (add new Vercel URL)
4. ✅ **Test deployment** (verify everything works)
5. ✅ **Compare both deployments** (Railway vs Render)

Once you confirm Render deployment works well, you can:
- Switch production to Render (change main branch's `NEXT_PUBLIC_API_URL`)
- Or keep both running for A/B testing

---

**Need Help?** Check Vercel docs: https://vercel.com/docs


