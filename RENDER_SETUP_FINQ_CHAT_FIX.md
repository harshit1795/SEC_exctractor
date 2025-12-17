# 🚀 Render Setup Guide - Fix FinQ Chat Database Issue

This guide will help you deploy your backend to Render to fix the FinQ Chat database connection issue (IPv6 problem on Railway).

---

## 🎯 Why Render?

- ✅ **Full IPv4 Support** - Unlike Railway, Render properly supports IPv4 connections
- ✅ **Free Tier Available** - 750 hours/month free
- ✅ **Always-On Option** - $7/month for no sleep
- ✅ **Easy Setup** - Auto-detects `render.yaml` configuration

---

## 📋 Step-by-Step Setup

### Step 1: Sign Up for Render (1 min)

1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. **Sign up with GitHub** (recommended - easier integration)
4. Authorize Render to access your repositories

---

### Step 2: Create New Web Service (2 min)

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. **Connect your GitHub repository**:
   - If not connected, click "Connect GitHub" and authorize
   - Select repository: `SEC_exctractor`
3. **Select branch**: `feature/nexus5.1_c_Rail_alt` (or your current branch)
4. Click **"Continue"**

---

### Step 3: Configure Service (Render Auto-Detects `render.yaml`)

Render will automatically detect your `render.yaml` file! ✅

**Verify these settings** (should be auto-filled):

- **Name**: `finq-backend` (or your preferred name)
- **Region**: `Oregon (US West)` (or closest to you)
- **Branch**: `feature/nexus5.1_c_Rail_alt`
- **Root Directory**: `finq-backend` ✅
- **Runtime**: `Python 3` ✅
- **Build Command**: `pip install -r requirements.txt` ✅
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` ✅

**If settings are not auto-filled**, manually enter them above.

---

### Step 4: Set Environment Variables (CRITICAL!)

Click **"Advanced"** → **"Environment Variables"** (or wait until after creation)

Add these **required** variables:

#### 1. Database Connection (MOST IMPORTANT)

```bash
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require
```

**Replace `[YOUR_PASSWORD]`** with your actual Supabase password.

**Important Notes:**
- ✅ Use **port 5432** (direct connection) - Render supports IPv4!
- ✅ Include `?connect_timeout=10&sslmode=require` at the end
- ✅ No square brackets `[]` around password in Render
- ✅ If password has special characters, URL-encode them:
  - `@` → `%40`
  - `:` → `%3A`
  - `/` → `%2F`
  - `#` → `%23`

**Example** (if password is `Supabasefinq`):
```
DATABASE_URL=postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require
```

#### 2. Gemini API Key

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

#### 3. CORS Origins (Add Your Vercel URLs)

```bash
CORS_ORIGINS=https://sec-exctractor.vercel.app,https://sec-exctractor-git-*.vercel.app,https://sec-exctractor-*.vercel.app
```

**To find your Vercel URLs:**
- Go to Vercel Dashboard → Your Project → Deployments
- Copy all deployment URLs (production + preview)
- Add them comma-separated (no spaces after commas)

**Example** (multiple URLs):
```
CORS_ORIGINS=https://sec-exctractor.vercel.app,https://sec-exctractor-git-feature-nexus5-1-c-rail-alt-abc123.vercel.app,https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app
```

#### 4. Optional: FRED API Key (if using economic data)

```bash
FRED_API_KEY=your_fred_api_key_here
```

#### 5. Optional: App Configuration

```bash
APP_NAME=FinQ Backend API
API_PREFIX=/api
DEBUG=false
ENVIRONMENT=production
```

---

### Step 5: Deploy! (3-5 min)

1. **Click "Create Web Service"**
2. **Wait for deployment** (first build takes 3-5 minutes)
3. **Watch the build logs**:
   - Look for: `✓ Build successful`
   - Look for: `Application startup complete`
   - Look for: `Uvicorn running on http://0.0.0.0:PORT`

**Your service URL will be**: `https://finq-backend.onrender.com` (or your custom name)

---

### Step 6: Test Deployment (2 min)

#### Test 1: Health Check

Open in browser or use curl:
```bash
curl https://finq-backend.onrender.com/api/health
```

**Expected response**:
```json
{"status":"healthy","service":"FinQ Backend API"}
```

#### Test 2: Check Logs

1. Go to Render Dashboard → Your Service → **Logs** tab
2. Look for:
   - ✅ `Application startup complete`
   - ✅ `Database connection successful` (if logged)
   - ❌ No `OperationalError` or `Network is unreachable`

#### Test 3: Test API Docs

Open in browser:
```
https://finq-backend.onrender.com/docs
```

Should show Swagger UI with all endpoints.

---

### Step 7: Update Vercel Frontend (2 min)

1. **Go to Vercel Dashboard**
2. **Select your frontend project**
3. **Go to Settings → Environment Variables**
4. **Update `NEXT_PUBLIC_API_URL`**:
   ```
   https://finq-backend.onrender.com/api
   ```
   (Replace with your actual Render service URL)

5. **Redeploy**:
   - Go to **Deployments** tab
   - Click **"..."** on latest deployment → **"Redeploy"**

---

### Step 8: Test FinQ Chat! 🎉

1. **Open your Vercel frontend**
2. **Navigate to Dashboard → Chatbot Tab**
3. **Try asking a question**:
   - "What is the revenue trend for AAPL?"
   - "Analyze the financial health of MSFT"

**Expected**: Chat should work without database connection errors! ✅

---

## 🔧 Troubleshooting

### Issue 1: Database Connection Still Fails

**Error**: `connection to server... Network is unreachable`

**Solutions**:

1. **Verify Supabase Network Restrictions**:
   - Go to Supabase Dashboard → Settings → Database
   - Ensure **"Network Restrictions"** = **"Allow all IP addresses"**

2. **Try Connection Pooler** (port 6543):
   ```
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.tdebmqhaoiexsdhxwung.supabase.co:6543/postgres?connect_timeout=10&sslmode=require
   ```
   - Get pooler URL from Supabase Dashboard → Settings → Database → Connection Pooling

3. **Check Password Encoding**:
   - If password has special characters, URL-encode them
   - Example: `P@ssw0rd` → `P%40ssw0rd`

4. **Verify Connection String Format**:
   - No square brackets `[]` around password
   - Include `?connect_timeout=10&sslmode=require`
   - Use port `5432` (direct) or `6543` (pooler)

### Issue 2: Build Fails

**Error**: `ModuleNotFoundError: No module named 'psycopg2'`

**Solution**:
- Check `finq-backend/requirements.txt` has `psycopg2-binary>=2.9.9`
- Render should install it automatically, but verify it's in requirements.txt

### Issue 3: CORS Errors

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
1. Add your Vercel URL to `CORS_ORIGINS` in Render
2. Format: `https://domain1.com,https://domain2.com` (comma-separated, no spaces)
3. **Redeploy** after updating environment variables

### Issue 4: Service Sleeps (Free Tier)

**Problem**: First request after 15 minutes takes 30-60 seconds

**Solutions**:
1. **Upgrade to Starter** ($7/month) - Always on, no sleep
2. **Use a ping service** (like UptimeRobot) to keep it awake
3. **Accept the cold start** - Free tier sleeps after 15 min inactivity

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Health endpoint works: `/api/health`
- [ ] API docs accessible: `/docs`
- [ ] Database connection successful (check logs)
- [ ] FinQ Chat works without errors
- [ ] Frontend can connect to backend
- [ ] CORS configured correctly
- [ ] All environment variables set

---

## 📊 Render vs Railway Comparison

| Feature | Railway | Render |
|---------|---------|--------|
| **IPv4 Support** | ❌ Limited | ✅ Full |
| **IPv6 Support** | ✅ Yes | ✅ Yes |
| **Free Tier** | 500 hours/month | 750 hours/month |
| **Sleep on Free** | ❌ No | ✅ Yes (15 min) |
| **Always-On Option** | ✅ $5/mo | ✅ $7/mo |
| **Auto-Deploy** | ✅ Yes | ✅ Yes |
| **Custom Domains** | ✅ Yes | ✅ Yes |

---

## 🎯 Next Steps

1. ✅ **Test FinQ Chat thoroughly**
2. ✅ **Monitor Render logs** for any issues
3. ✅ **Set up alerts** (Render → Settings → Notifications)
4. ✅ **Consider upgrading** to Starter plan ($7/mo) for always-on service
5. ✅ **Update documentation** with new Render URL

---

## 🔗 Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **Your Service Logs**: Render Dashboard → Your Service → Logs
- **Environment Variables**: Render Dashboard → Your Service → Environment
- **Supabase Dashboard**: https://supabase.com/dashboard

---

## 💡 Pro Tips

1. **Keep Railway deployment** as backup until Render is fully tested
2. **Use Render's free tier** to test, upgrade if needed
3. **Monitor logs** during first few days to catch issues early
4. **Set up Render alerts** for deployment failures
5. **Bookmark your Render service URL** for easy access

---

**Need Help?** Check Render's support chat in the dashboard or their documentation.

