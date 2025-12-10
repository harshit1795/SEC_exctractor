# 🚀 Railway to Render Migration Guide

This guide will help you migrate your FinQ backend from Railway to Render.

## ✅ Prerequisites

1. **Render Account**: Sign up at https://render.com (free tier available)
2. **GitHub Repository**: Your code should be in GitHub
3. **Environment Variables**: Note down all your Railway environment variables

## 📋 Step-by-Step Migration

### Step 1: Prepare Your Repository

1. **Switch to your branch**:
   ```bash
   git checkout feature/nexus5.1_c_Rail_alt
   ```

2. **Verify files are in place**:
   - ✅ `render.yaml` (created in repo root)
   - ✅ `finq-backend/requirements.txt`
   - ✅ `finq-backend/app/main.py`

### Step 2: Create Render Account & Service

1. **Sign up/Login to Render**:
   - Go to https://render.com
   - Click "Get Started for Free"
   - Sign up with GitHub (recommended)

2. **Create New Web Service**:
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Select your repository: `SEC_exctractor`
   - Select branch: `feature/nexus5.1_c_Rail_alt`

### Step 3: Configure Service Settings

**Basic Settings:**
- **Name**: `finq-backend` (or your preferred name)
- **Region**: `Oregon (US West)` (or closest to your users)
- **Branch**: `feature/nexus5.1_c_Rail_alt`
- **Root Directory**: `finq-backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**OR use the render.yaml file:**
- Render will auto-detect `render.yaml` in your repo
- Click **"Apply"** to use the blueprint configuration

### Step 4: Set Environment Variables

In Render Dashboard → Your Service → **Environment** tab, add:

#### Required Variables:

```bash
# Database (Supabase)
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# CORS Origins (add all your Vercel URLs)
CORS_ORIGINS=https://sec-exctractor.vercel.app,https://sec-exctractor-git-featu-9f4636-harshit-golas-projects-ef9cdcc7.vercel.app,https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app

# App Configuration
APP_NAME=FinQ Backend API
API_PREFIX=/api
DEBUG=false
```

#### Optional Variables:

```bash
# Firebase (if you're using it)
FIREBASE_CREDENTIALS_B64=your_base64_encoded_credentials

# Health Check
HEALTH_CHECK_PATH=/api/health
```

**Important Notes:**
- ✅ Use **port 5432** (direct connection) - Render supports IPv4, so this should work!
- ✅ If you still have issues, try Supabase connection pooler (port 6543)
- ✅ Add ALL your Vercel deployment URLs to `CORS_ORIGINS` (comma-separated)

### Step 5: Deploy

1. **Click "Create Web Service"**
2. **Wait for deployment** (first build takes 2-5 minutes)
3. **Check build logs** for any errors
4. **Test the service**:
   - Your service URL will be: `https://finq-backend.onrender.com` (or your custom name)
   - Test: `https://your-service.onrender.com/api/health`

### Step 6: Update Vercel Frontend

1. **Go to Vercel Dashboard**
2. **Select your project**
3. **Go to Settings → Environment Variables**
4. **Update `NEXT_PUBLIC_API_URL`**:
   ```
   https://finq-backend.onrender.com
   ```
   (Replace with your actual Render service URL)

5. **Redeploy** your Vercel frontend

### Step 7: Test Everything

1. **Health Check**:
   ```bash
   curl https://your-service.onrender.com/api/health
   ```

2. **Test API Endpoints**:
   - `/api/health` - Should return `{"status": "healthy"}`
   - `/api/financial/tickers/available` - Should return ticker list
   - `/docs` - Should show Swagger UI

3. **Test Frontend**:
   - Open your Vercel deployment
   - Check if data loads correctly
   - Test FinQ Chat functionality

## 🔧 Troubleshooting

### Issue: Build Fails

**Error**: `ModuleNotFoundError: No module named 'psycopg2'`

**Solution**: 
- Check `requirements.txt` has `psycopg2-binary>=2.9.9`
- Render should install it automatically

### Issue: Database Connection Fails

**Error**: `connection to server... Network is unreachable`

**Solution**:
1. **Try connection pooler** (port 6543):
   ```
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.tdebmqhaoiexsdhxwung.supabase.co:6543/postgres?connect_timeout=10&sslmode=require
   ```

2. **Check Supabase Network Restrictions**:
   - Go to Supabase Dashboard → Settings → Database
   - Ensure "Network Restrictions" allows all IPs

3. **Verify connection string**:
   - Make sure password has no special characters that need URL encoding
   - Use `%40` for `@`, `%3A` for `:`, etc. if needed

### Issue: CORS Errors

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
1. Add your Vercel URL to `CORS_ORIGINS` in Render
2. Format: `https://domain1.com,https://domain2.com` (comma-separated, no spaces)
3. Redeploy after updating environment variables

### Issue: Service Sleeps (Free Tier)

**Problem**: Free tier services sleep after 15 minutes of inactivity

**Solutions**:
1. **Upgrade to Starter** ($7/month) - Always on
2. **Use a ping service** (like UptimeRobot) to keep it awake
3. **Accept the cold start** (first request after sleep takes 30-60 seconds)

## 📊 Render vs Railway Comparison

| Feature | Railway | Render |
|---------|---------|--------|
| **Free Tier** | 500 hours/month | 750 hours/month |
| **IPv4 Support** | ❌ Limited | ✅ Full |
| **Sleep on Free** | ❌ No | ✅ Yes (15 min) |
| **Always-On Option** | ✅ $5/mo | ✅ $7/mo |
| **Auto-Deploy** | ✅ Yes | ✅ Yes |
| **Custom Domains** | ✅ Yes | ✅ Yes |
| **PostgreSQL** | ✅ Built-in | ✅ Built-in |

## 🎯 Next Steps After Migration

1. ✅ **Test all endpoints** thoroughly
2. ✅ **Monitor logs** in Render Dashboard
3. ✅ **Set up alerts** (Render → Settings → Notifications)
4. ✅ **Update documentation** with new URLs
5. ✅ **Consider upgrading** to Starter plan ($7/mo) for always-on service

## 🔗 Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **Your Service Logs**: Render Dashboard → Your Service → Logs
- **Environment Variables**: Render Dashboard → Your Service → Environment

## ✅ Migration Checklist

- [ ] Created Render account
- [ ] Created new Web Service
- [ ] Set all environment variables
- [ ] Deployed successfully
- [ ] Tested health endpoint
- [ ] Updated Vercel `NEXT_PUBLIC_API_URL`
- [ ] Tested frontend connection
- [ ] Tested FinQ Chat
- [ ] Verified database connection
- [ ] Checked CORS configuration
- [ ] Updated any documentation

---

**Need Help?** Check Render's documentation or their support chat in the dashboard.

