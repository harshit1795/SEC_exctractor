# ⚡ Vercel Branch Deployment - Quick Start

## 🎯 Goal
Create a new Vercel deployment for `feature/nexus5.1_c_Rail_alt` branch that uses Render backend.

## ⚡ 5-Minute Setup

### Step 1: Create New Project (2 min)
1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import `SEC_exctractor` repository
4. **Project Name**: `finq-frontend-render`
5. **Root Directory**: `finq-frontend`
6. **Production Branch**: `feature/nexus5.1_c_Rail_alt` ⚠️

### Step 2: Set Environment Variables (2 min)
Click **"Environment Variables"** and add:

```bash
# Render Backend
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api

# Firebase (copy from your Railway deployment)
NEXT_PUBLIC_FIREBASE_API_KEY=[same as Railway]
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=[same as Railway]
NEXT_PUBLIC_FIREBASE_PROJECT_ID=[same as Railway]
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=[same as Railway]
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=[same as Railway]
NEXT_PUBLIC_FIREBASE_APP_ID=[same as Railway]
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=[same as Railway]
```

**Set for**: Production, Preview, Development

### Step 3: Deploy (1 min)
1. Click **"Deploy"**
2. Wait for build
3. Done! 🎉

### Step 4: Update Render CORS
1. Render Dashboard → Your Service → Environment
2. Add to `CORS_ORIGINS`: `https://finq-frontend-render.vercel.app`
3. Redeploy Render

## ✅ Verify

1. Open: `https://finq-frontend-render.vercel.app`
2. Check Network tab → Should see calls to Render backend
3. Test FinQ Chat → Should work with Render

## 📊 Result

- ✅ **Railway deployment**: Still works at `https://sec-exctractor.vercel.app`
- ✅ **Render deployment**: New at `https://finq-frontend-render.vercel.app`
- ✅ **Both independent**: Can run simultaneously

---

**That's it!** You now have parallel deployments. 🚀


