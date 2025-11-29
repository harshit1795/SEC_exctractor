# 🚀 Phase 4: Production Deployment Guide

**Status**: Ready for Deployment  
**Last Updated**: 2025-11-26

---

## 📋 Pre-Deployment Checklist

### ✅ Application Readiness
- [x] Backend API fully functional (33+ endpoints)
- [x] Frontend Next.js app complete (Dashboard, Nexus, Settings)
- [x] Database models and migrations ready
- [x] Authentication (Firebase) configured
- [x] Environment variables documented
- [x] Security: All API keys in `.gitignore`
- [x] Error handling implemented
- [x] Loading states and user feedback

### 🔒 Security Verification
- [x] No hardcoded API keys in code
- [x] All sensitive files in `.gitignore`
- [x] Environment variables properly configured
- [x] CORS configured correctly
- [x] Firebase credentials managed securely

---

## 🎯 Deployment Architecture

### Recommended Stack

```
┌─────────────────┐
│   Vercel        │  ← Frontend (Next.js)
│   (Free Tier)   │
└────────┬────────┘
         │ HTTPS
         │
┌────────▼────────┐
│   Railway       │  ← Backend (FastAPI)
│   (Starter $5)  │
└────────┬────────┘
         │
┌────────▼────────┐
│   Supabase      │  ← Database (PostgreSQL)
│   (Free Tier)   │
└─────────────────┘
```

**Total Cost**: $0-5/month (starting with free tiers)

---

## 📦 Step 1: Database Setup (Supabase)

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up / Log in
3. Click "New Project"
4. Fill in:
   - **Name**: `finq-production`
   - **Database Password**: (save this securely!)
   - **Region**: Choose closest to your users
5. Wait for project creation (~2 minutes)

### 1.2 Get Connection String

1. Go to **Settings** → **Database**
2. Find **Connection string** section
3. Copy the **URI** connection string:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
4. Save this - you'll need it for Railway

### 1.3 Run Database Migrations

```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

# Navigate to backend
cd finq-backend

# Run migrations
alembic upgrade head

# Verify tables created
# (Check Supabase SQL Editor or use psql)
```

---

## 🚂 Step 2: Backend Deployment (Railway)

### 2.1 Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Authorize Railway to access your repositories

### 2.2 Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `SEC_exctractor`
4. **Note**: Railway may not show branch selection immediately. That's okay - we'll set it in the next step.
5. Continue with project creation (Railway will deploy from `main`/`master` initially)

### 2.3 Configure Build Settings and Branch

**Important**: Set the branch first, then configure build settings.

1. **Set Branch**:
   - Click on your **service** (the deployed app)
   - Go to **Settings** tab
   - Scroll to **"Source"** section
   - Click **Branch** dropdown
   - Select your branch: `feature/nexus5.1_c_test` (or your branch name)
   - Railway will auto-save and trigger a new deployment

2. **Configure Build Settings**:
   - Still in **Settings**, go to **"Build"** section
   - **Root Directory**: `finq-backend` ⚠️ **CRITICAL - Set this first!**
   - **Build Command**: (leave empty - auto-detected)
   
3. **Configure Start Command**:
   - Still in **Settings**, go to **"Deploy"** section
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - ⚠️ **Important**: Don't include `cd finq-backend` - Root Directory handles that

**Note**: If branch dropdown is empty:
- Make sure your branch is pushed to GitHub: `git push origin feature/nexus5.1_c_test`
- Refresh the page or disconnect/reconnect GitHub in Settings
- See `RAILWAY_BRANCH_FIX.md` for detailed troubleshooting

### 2.4 Set Environment Variables

Go to **Variables** tab and add:

```bash
# Database
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# API Keys
GEMINI_API_KEY=your-gemini-api-key
FRED_API_KEY=your-fred-api-key

# Firebase (if backend needs it)
FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}

# CORS (add your Vercel domain after frontend deployment)
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app

# Optional
ENVIRONMENT=production
DEBUG=false
```

### 2.5 Deploy

1. Railway will automatically deploy on push to main branch
2. Or click **"Deploy"** button
3. Wait for build to complete (~3-5 minutes)
4. Get your backend URL: `https://your-app.up.railway.app`

### 2.6 Verify Deployment

```bash
# Test health endpoint
curl https://your-app.up.railway.app/api/health

# Should return:
# {"status":"healthy","service":"FinQ Backend API"}
```

---

## ⚡ Step 3: Frontend Deployment (Vercel)

### 3.1 Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Authorize Vercel to access your repositories

### 3.2 Import Project

1. Click **"Add New..."** → **"Project"**
2. Import your repository: `SEC_exctractor`
3. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `finq-frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

### 3.3 Set Environment Variables

Go to **Settings** → **Environment Variables** and add:

```bash
# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id

# Backend API URL (use Railway URL from Step 2.6)
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app/api
```

### 3.4 Deploy

1. Click **"Deploy"**
2. Wait for build (~2-3 minutes)
3. Get your frontend URL: `https://your-app.vercel.app`

### 3.5 Update Backend CORS

After getting Vercel URL, update Railway environment variable:

```bash
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

Redeploy backend (Railway auto-redeploys on env var changes)

---

## 🔗 Step 4: Connect Services

### 4.1 Update Frontend API URL

If you need to change the API URL after deployment:

1. Go to Vercel → Your Project → **Settings** → **Environment Variables**
2. Update `NEXT_PUBLIC_API_URL` to your Railway backend URL
3. Redeploy (Vercel will auto-redeploy)

### 4.2 Test Full Stack

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Sign in with Firebase
3. Test dashboard functionality
4. Test Nexus community features
5. Verify data loading from backend

---

## 📊 Step 5: Monitoring & Maintenance

### 5.1 Set Up Monitoring

**Railway (Backend)**:
- View logs in Railway dashboard
- Set up alerts for errors
- Monitor resource usage

**Vercel (Frontend)**:
- View analytics in Vercel dashboard
- Monitor build logs
- Check function execution times

**Supabase (Database)**:
- Monitor database size
- Check query performance
- Set up backup schedule

### 5.2 Database Backups

Supabase automatically backs up daily (free tier). For manual backups:

```bash
# Using pg_dump
pg_dump $DATABASE_URL > backup.sql

# Or use Supabase dashboard
# Settings → Database → Backups
```

### 5.3 Update Process

1. **Code Changes**: Push to GitHub
2. **Backend**: Railway auto-deploys
3. **Frontend**: Vercel auto-deploys
4. **Database Migrations**: Run manually:
   ```bash
   alembic upgrade head
   ```

---

## 🐛 Troubleshooting

### Backend Not Starting

**Check Railway Logs**:
1. Go to Railway → Your Project → **Deployments**
2. Click on latest deployment
3. Check logs for errors

**Common Issues**:
- Missing environment variables
- Database connection failed
- Port binding issues (should use `$PORT`)

### Frontend Build Fails

**Check Vercel Build Logs**:
1. Go to Vercel → Your Project → **Deployments**
2. Click on failed deployment
3. Check build logs

**Common Issues**:
- Missing environment variables
- TypeScript errors
- Build timeout (increase in settings)

### Database Connection Issues

**Verify Connection String**:
```bash
# Test connection
psql $DATABASE_URL -c "SELECT version();"
```

**Check Supabase**:
- Database is running
- IP allowlist (if enabled)
- Connection pool limits

---

## 💰 Cost Estimation

### Free Tier (Starting)

| Service | Cost | Limits |
|---------|------|--------|
| Railway | $0 | 500 hrs/month, sleeps after inactivity |
| Supabase | $0 | 500MB database, 2GB bandwidth |
| Vercel | $0 | 100GB bandwidth/month |
| **Total** | **$0/month** | Good for testing/small usage |

### Starter Tier (Recommended)

| Service | Cost | Why Upgrade |
|---------|------|-------------|
| Railway Starter | $5/month | No sleep, better performance |
| Supabase | $0 | Still sufficient |
| Vercel | $0 | Still sufficient |
| **Total** | **$5/month** | Production-ready for small apps |

### Growth Tier (If Needed)

| Service | Cost | When Needed |
|---------|------|-------------|
| Railway Pro | $10/month | Higher traffic |
| Supabase Pro | $25/month | >500MB database |
| Vercel Pro | $20/month | >100GB bandwidth |
| **Total** | **$55/month** | Growing user base |

---

## ✅ Post-Deployment Checklist

- [ ] Backend health endpoint responding
- [ ] Frontend loads correctly
- [ ] Authentication working (Firebase)
- [ ] Dashboard data loading
- [ ] Nexus community features working
- [ ] Database migrations applied
- [ ] Environment variables set correctly
- [ ] CORS configured properly
- [ ] HTTPS enabled (automatic on Vercel/Railway)
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up
- [ ] Backup strategy in place

---

## 🎉 Phase 4 Complete!

Once deployed, your application will be:
- ✅ **Live and accessible** worldwide
- ✅ **Scalable** and ready for growth
- ✅ **Secure** with HTTPS and proper authentication
- ✅ **Monitored** with logging and analytics
- ✅ **Maintainable** with easy update process

**Next Steps**:
1. Share your deployed URL
2. Gather user feedback
3. Monitor usage and performance
4. Iterate and improve!

---

## 📞 Support Resources

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Firebase Docs**: https://firebase.google.com/docs

---

**Ready to deploy? Follow the steps above and your application will be live! 🚀**

