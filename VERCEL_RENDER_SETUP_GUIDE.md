# 🚀 Vercel Setup for Render Backend - Step-by-Step Guide

This guide will help you create a **new Vercel deployment** specifically for your Render backend, while keeping your existing Railway deployment completely untouched.

---

## 📋 What You'll Have

After setup, you'll have **two independent Vercel deployments**:

1. **Railway Deployment** (existing) → `main` branch → Uses Railway backend ✅ Keep as-is
2. **Render Deployment** (new) → `feature/nexus5.1_c_Rail_alt` branch → Uses Render backend 🆕

Both will run simultaneously and independently!

---

## 🎯 Step-by-Step Setup

### Step 1: Get Your Render Service URL

1. Go to **Render Dashboard**: https://dashboard.render.com
2. Click on your backend service (e.g., `finq-backend`)
3. Copy your service URL (e.g., `https://finq-backend.onrender.com`)
4. **Save this URL** - you'll need it in Step 3

**Your Render URL**: `https://[your-service-name].onrender.com`

---

### Step 2: Create New Vercel Project

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. **Import Repository**:
   - Select: `SEC_exctractor`
   - Click **"Import"**

---

### Step 3: Configure Project Settings

**Basic Configuration:**

- **Project Name**: `finq-frontend-render` (or any name you prefer)
  - This helps distinguish it from your Railway deployment
  
- **Framework Preset**: `Next.js` (should auto-detect ✅)

- **Root Directory**: `finq-frontend` ⚠️ **Important!**

- **Build Command**: `npm run build` (default - should auto-fill)

- **Output Directory**: `.next` (default - should auto-fill)

- **Install Command**: `npm install` (default - should auto-fill)

**Git Configuration:**

- **Production Branch**: You'll see `main` as default - **That's OK!** ✅
  - You can change this later in Settings (see Step 3A below)
  - OR use preview deployments (see Step 3B below - Recommended!)
  - If you want to set it now, click dropdown and select `feature/nexus5.1_c_Rail_alt`
  - If branch doesn't appear, make sure it's pushed to GitHub

---

### Step 4: Set Environment Variables (CRITICAL!)

Click **"Environment Variables"** section and add:

#### 1. Backend API URL (Render)

```bash
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api
```

**Important:**
- Replace `your-render-service.onrender.com` with your **actual Render service URL** from Step 1
- Include `/api` at the end
- Set for: ✅ **Production** ✅ **Preview** ✅ **Development** (all environments)

**Example:**
```
NEXT_PUBLIC_API_URL=https://finq-backend.onrender.com/api
```

#### 2. Firebase Configuration (Same as Railway)

Copy the **exact same Firebase config** from your Railway deployment:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_storage_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id
```

**How to get these values:**
- Go to your **existing Railway Vercel project**
- Settings → Environment Variables
- Copy all `NEXT_PUBLIC_FIREBASE_*` values
- Paste them here

**Set for:** ✅ **Production** ✅ **Preview** ✅ **Development** (all environments)

---

### Step 5: Deploy!

1. **Review your settings** (double-check Root Directory)
2. Click **"Deploy"** (even if branch is `main` - that's fine!)
3. **Wait for build** (2-5 minutes for first deployment)
4. **Watch the build logs** for any errors

**Your new deployment URL**: `https://finq-frontend-render.vercel.app` (or your custom name)

---

### Step 5A: Change Production Branch (After Deployment)

**If you deployed with `main` branch**, you can change it using one of these methods:

**Method 1: Settings → General**
1. **Go to Vercel Dashboard** → Your new project
2. **Settings** → **General** (left sidebar)
3. Scroll to **"Production Branch"** section
4. Click dropdown/edit → Select `feature/nexus5.1_c_Rail_alt`
5. Click **"Save"**

**Method 2: Promote Deployment**
1. **Deployments** tab
2. Find deployment from `feature/nexus5.1_c_Rail_alt` branch
3. Click **"..."** → **"Promote to Production"**

**Note**: If you can't find these options, use **Step 5B (Preview Deployments)** instead - it's easier!

---

### Step 5B: Alternative - Use Preview Deployments (Easier!)

**Actually, you don't need to change the production branch!** Vercel automatically creates preview deployments for all branches.

**How it works:**
1. **Create project** with `main` branch (default)
2. **Set environment variables** (see Step 4)
3. **Push to your branch**: `feature/nexus5.1_c_Rail_alt`
4. **Vercel automatically creates a preview deployment** for that branch!

**Set Branch-Specific Environment Variables:**

1. Go to **Settings** → **Environment Variables**
2. For `NEXT_PUBLIC_API_URL`:
   - **Value**: `https://your-render-service.onrender.com/api`
   - **Environments**: Select **"Preview"** ✅ (this applies to all non-main branches)
   - Click **"Save"**

3. **For Production branch** (main), you can either:
   - Leave it empty (won't affect main branch)
   - Or set it to Railway URL for Production environment

**Result:**
- **Main branch** → Production deployment (uses Railway if you set Production env vars)
- **feature/nexus5.1_c_Rail_alt** → Preview deployment (uses Render via Preview env vars)

**This approach is recommended** because:
- ✅ No branch switching needed
- ✅ Automatic preview deployments
- ✅ Easy to test multiple branches

---

### Step 6: Update Render CORS (IMPORTANT!)

**Critical**: Add your new Vercel URL to Render's CORS settings!

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click on your backend service**
3. Go to **"Environment"** tab
4. Find `CORS_ORIGINS` variable
5. **Add your new Vercel URL** to the list:

**Current value** (example):
```
https://sec-exctractor.vercel.app,https://sec-exctractor-git-*.vercel.app
```

**Updated value** (add your new URL):
```
https://sec-exctractor.vercel.app,https://finq-frontend-render.vercel.app,https://sec-exctractor-git-*.vercel.app
```

**Important:**
- URLs are **comma-separated** (no spaces after commas)
- Include your **exact Vercel URL** from Step 5
- Render will auto-redeploy after you save

---

### Step 7: Verify Everything Works

#### Test 1: Check Deployment

1. Open your new Vercel URL: `https://finq-frontend-render.vercel.app`
2. Should load without errors ✅

#### Test 2: Check API Connection

1. Open browser **DevTools** (F12)
2. Go to **Network** tab
3. Navigate to Dashboard or try FinQ Chat
4. Check API calls - they should go to your **Render backend**:
   - ✅ `https://finq-backend.onrender.com/api/...`
   - ❌ NOT `https://railway.app/api/...`

#### Test 3: Test FinQ Chat

1. Go to **Dashboard** → **Chatbot Tab**
2. Ask a question: "What is the revenue trend for AAPL?"
3. Should work without database errors! ✅

#### Test 4: Verify Railway Deployment Still Works

1. Open your **existing Railway Vercel deployment**
2. Test that it still works
3. Should still connect to Railway backend ✅

---

## ✅ Verification Checklist

After setup, verify:

- [ ] **New Vercel project created** with correct name
- [ ] **Production branch** set to `feature/nexus5.1_c_Rail_alt`
- [ ] **Root Directory** set to `finq-frontend`
- [ ] **Environment variables set**:
  - [ ] `NEXT_PUBLIC_API_URL` = Render URL
  - [ ] All Firebase variables set
- [ ] **Deployment successful** (no build errors)
- [ ] **Render CORS updated** with new Vercel URL
- [ ] **Frontend loads** correctly
- [ ] **API calls go to Render** (check Network tab)
- [ ] **FinQ Chat works** (no database errors)
- [ ] **Railway deployment still works** (untouched)

---

## 🔍 How to Tell Which Backend You're Using

### Method 1: Check URL

- **Railway deployment**: `https://sec-exctractor.vercel.app` (or your Railway Vercel URL)
- **Render deployment**: `https://finq-frontend-render.vercel.app` (or your new URL)

### Method 2: Check Environment Variables

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Check `NEXT_PUBLIC_API_URL`:
   - Railway: `https://secexctractor-production-80f5.up.railway.app/api`
   - Render: `https://finq-backend.onrender.com/api`

### Method 3: Check Browser Network Tab

1. Open DevTools (F12) → Network tab
2. Look at API requests:
   - Railway: Requests go to `railway.app`
   - Render: Requests go to `onrender.com`

---

## 🔧 Troubleshooting

### Issue 1: Branch Not Showing in Dropdown / Default is Main

**Problem**: Can't select `feature/nexus5.1_c_Rail_alt` branch, or `main` is default

**Solution Option A - Change Branch Later:**
1. Create project with `main` (default) - that's fine!
2. After deployment, go to **Settings** → **Git** → **Production Branch**
3. Change to `feature/nexus5.1_c_Rail_alt`
4. Vercel will auto-redeploy

**Solution Option B - Use Preview Deployments (Recommended):**
1. Create project with `main` (default) - that's fine!
2. Set `NEXT_PUBLIC_API_URL` for **Preview** environment only
3. Push to `feature/nexus5.1_c_Rail_alt` branch
4. Vercel automatically creates preview deployment
5. No branch switching needed!

**Solution Option C - Force Branch Selection:**
1. Make sure branch is pushed to GitHub:
   ```bash
   git push origin feature/nexus5.1_c_Rail_alt
   ```
2. Refresh Vercel page
3. Or disconnect/reconnect GitHub in Vercel Settings
4. Branch should appear in dropdown

### Issue 2: CORS Errors

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
1. Go to Render Dashboard → Environment
2. Add your Vercel URL to `CORS_ORIGINS`
3. Format: `https://your-vercel-url.vercel.app` (comma-separated)
4. Render will auto-redeploy

### Issue 3: Wrong Backend URL

**Problem**: Frontend is calling Railway instead of Render

**Solution**:
1. Check Vercel Environment Variables
2. Verify `NEXT_PUBLIC_API_URL` = Render URL
3. **Redeploy** Vercel (env vars require redeploy)

### Issue 4: Build Fails

**Error**: Build errors in Vercel

**Solution**:
1. Check build logs in Vercel Dashboard
2. Verify `finq-frontend/package.json` exists
3. Verify Root Directory = `finq-frontend`
4. Check for missing dependencies

### Issue 5: FinQ Chat Still Shows Database Error

**Problem**: Chat still fails with database connection error

**Solution**:
1. Verify Render backend is running (check Render Dashboard)
2. Test Render backend directly: `https://your-render-service.onrender.com/api/health`
3. Check Render logs for database connection errors
4. Verify `DATABASE_URL` is set correctly in Render

---

## 📊 Deployment Summary

| Deployment | Branch | Backend | Vercel URL | Status |
|------------|--------|---------|------------|--------|
| **Railway** | `main` | Railway | `https://sec-exctractor.vercel.app` | ✅ Existing |
| **Render** | `feature/nexus5.1_c_Rail_alt` | Render | `https://finq-frontend-render.vercel.app` | 🆕 New |

---

## 🎯 Quick Reference

### Render Service URL
```
https://[your-service-name].onrender.com
```

### Vercel Deployment URLs
- **Railway**: `https://sec-exctractor.vercel.app` (existing)
- **Render**: `https://finq-frontend-render.vercel.app` (new)

### Environment Variables Template
```bash
# Render Backend
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api

# Firebase (same for both)
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=...
```

---

## 🚀 Next Steps

1. ✅ **Test Render deployment thoroughly**
2. ✅ **Compare performance** (Railway vs Render)
3. ✅ **Monitor both deployments** for issues
4. ✅ **Once confirmed working**, you can:
   - Keep both running for testing
   - Switch production to Render (change main branch's API URL)
   - Or keep Railway as production and Render as staging

---

## 💡 Pro Tips

1. **Bookmark both URLs** for easy access
2. **Use different browser profiles** to test both simultaneously
3. **Monitor Render logs** during first few days
4. **Set up Vercel preview deployments** for easy testing
5. **Keep Railway deployment** as backup until Render is fully tested

---

**Need Help?** 
- Vercel Docs: https://vercel.com/docs
- Render Docs: https://render.com/docs
- Check deployment logs in both dashboards

