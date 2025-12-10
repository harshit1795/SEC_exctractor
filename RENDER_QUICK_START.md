# 🚀 Render Quick Start - 5 Minute Setup

## Step 1: Sign Up (1 min)
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub

## Step 2: Create Service (2 min)
1. Click **"New +"** → **"Web Service"**
2. Connect repository: `SEC_exctractor`
3. Select branch: `feature/nexus5.1_c_Rail_alt`
4. Render will auto-detect `render.yaml` ✅

## Step 3: Set Environment Variables (1 min)
Go to **Environment** tab, add:

```bash
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require
GEMINI_API_KEY=your_key_here
CORS_ORIGINS=https://sec-exctractor.vercel.app,https://sec-exctractor-git-*.vercel.app
```

## Step 4: Deploy (1 min)
1. Click **"Create Web Service"**
2. Wait 2-5 minutes for first build
3. Copy your service URL: `https://finq-backend.onrender.com`

## Step 5: Update Vercel (1 min)
1. Vercel Dashboard → Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL` to your Render URL
3. Redeploy frontend

## ✅ Done!
Test: `https://your-service.onrender.com/api/health`

---

**Your Render Service URL**: `https://[service-name].onrender.com`

