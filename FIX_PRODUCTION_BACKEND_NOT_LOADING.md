# 🔧 Fix: Backend Data Not Loading in Production

## 🔍 Problem

Your deployed app (Backend: Render, Frontend: Vercel, Database: Supabase) is not loading backend data.

## ✅ Most Common Issues & Fixes

### Issue 1: `NEXT_PUBLIC_API_URL` Not Set in Vercel (90% of cases)

**Symptom**: Frontend tries to call `http://localhost:8000/api` instead of your Render backend

**Fix**:

1. **Go to Vercel Dashboard**:
   - Your Project → **Settings** → **Environment Variables**

2. **Add/Update** `NEXT_PUBLIC_API_URL`:
   ```
   NEXT_PUBLIC_API_URL=https://your-render-backend.onrender.com/api
   ```
   ⚠️ **Important**: 
   - Must include `/api` at the end
   - Must use `https://` (not `http://`)
   - No trailing slash

3. **Set for All Environments**:
   - ✅ Production
   - ✅ Preview
   - ✅ Development

4. **Redeploy**:
   - Go to **Deployments** tab
   - Click **⋯** on latest deployment → **Redeploy**
   - Or push a new commit to trigger rebuild

**Why**: Next.js embeds `NEXT_PUBLIC_*` variables at **build time**, so you must redeploy after changing them!

---

### Issue 2: CORS Configuration Missing in Render (80% of cases)

**Symptom**: Browser console shows CORS errors like:
```
Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS policy
```

**Fix**:

1. **Go to Render Dashboard**:
   - Your Backend Service → **Environment**

2. **Check/Update** `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://your-vercel-app.vercel.app,https://your-vercel-app-*.vercel.app
   ```
   
   **Format**:
   - Comma-separated list
   - Include your production domain
   - Include preview domains (with `*` wildcard)
   - No spaces after commas
   - Must use `https://`

3. **Example**:
   ```
   CORS_ORIGINS=https://sec-exctractor.vercel.app,https://sec-exctractor-*.vercel.app,https://sec-exctractor-git-*.vercel.app
   ```

4. **Restart Service**:
   - Click **Manual Deploy** → **Deploy latest commit**
   - Or wait for auto-deploy

---

### Issue 3: Render Service Sleeping (Free Tier)

**Symptom**: First request takes 30-60 seconds, then works

**Fix**:
- **Option A**: Upgrade to paid plan (always-on)
- **Option B**: Use a service like [UptimeRobot](https://uptimerobot.com) to ping your backend every 5 minutes
- **Option C**: Accept the cold start delay (first request will be slow)

**Test**: Try accessing your backend directly:
```
https://your-render-backend.onrender.com/api/health
```

---

### Issue 4: Backend Environment Variables Missing

**Symptom**: Backend returns 500 errors or "API key not found"

**Fix**:

1. **Go to Render Dashboard**:
   - Your Backend Service → **Environment**

2. **Verify these are set**:
   ```
   DATABASE_URL=postgresql://... (from Supabase)
   GEMINI_API_KEY=your_gemini_key
   FRED_API_KEY=your_fred_key (optional)
   CORS_ORIGINS=https://your-vercel-app.vercel.app,...
   ```

3. **Check Supabase Connection String**:
   - Go to Supabase → **Settings** → **Database**
   - Copy **Connection string** (use **Connection Pooling** port `6543` if available)
   - Format: `postgresql://postgres:[PASSWORD]@[HOST]:6543/postgres?sslmode=require`

---

## 🧪 Step-by-Step Debugging

### Step 1: Test Backend Directly

Open in browser:
```
https://your-render-backend.onrender.com/api/health
```

**Expected**: `{"status":"healthy","service":"FinQ Backend API"}`

**If fails**: Backend is not running or has errors

---

### Step 2: Check Frontend Environment Variable

1. **Open your Vercel deployment** in browser
2. **Open DevTools** (F12) → **Console**
3. **Run**:
   ```javascript
   console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)
   ```

**Expected**: `https://your-render-backend.onrender.com/api`

**If shows**:
- `undefined` → Variable not set
- `http://localhost:8000/api` → Using default, variable not set
- Wrong URL → Variable has wrong value

---

### Step 3: Check Network Requests

1. **Open DevTools** (F12) → **Network** tab
2. **Clear network log**
3. **Refresh page** or use the app
4. **Find failed requests** (red in Network tab)
5. **Click on failed request** → Check:
   - **Request URL**: Should be `https://your-render-backend.onrender.com/api/...`
   - **Status**: Should be `200` (not `404`, `CORS error`, or `Network Error`)
   - **Response**: Should have data (not error message)

---

### Step 4: Check Browser Console

Look for errors:
- **CORS errors** → Backend CORS_ORIGINS missing your Vercel URL
- **Network errors** → Backend URL wrong or backend not accessible
- **404 errors** → Backend URL missing `/api` or endpoint doesn't exist
- **401/403 errors** → Authentication or API key issues

---

## 📋 Complete Checklist

### Vercel Configuration
- [ ] `NEXT_PUBLIC_API_URL` is set to `https://your-render-backend.onrender.com/api`
- [ ] Variable is set for **All Environments** (Production, Preview, Development)
- [ ] Frontend has been **redeployed** after setting variable
- [ ] All Firebase variables (`NEXT_PUBLIC_FIREBASE_*`) are set

### Render Configuration
- [ ] `CORS_ORIGINS` includes your Vercel production URL
- [ ] `CORS_ORIGINS` includes Vercel preview URLs (with wildcards)
- [ ] `DATABASE_URL` is set (Supabase connection string)
- [ ] `GEMINI_API_KEY` is set
- [ ] Backend service is **Running** (not sleeping)
- [ ] Backend logs show no errors

### Supabase Configuration
- [ ] Database is accessible
- [ ] Connection string is correct
- [ ] IP allowlist is disabled (or Render IPs are allowed)

---

## 🔧 Quick Fix Commands

### Test Backend Health
```bash
curl https://your-render-backend.onrender.com/api/health
```

### Test Backend from Frontend Domain
```bash
# In browser console on your Vercel site:
fetch('https://your-render-backend.onrender.com/api/health')
  .then(r => r.json())
  .then(data => console.log('✅ Backend works:', data))
  .catch(err => console.error('❌ Backend error:', err))
```

### Check CORS
```bash
curl -H "Origin: https://your-vercel-app.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://your-render-backend.onrender.com/api/health \
     -v
```

Should return headers like:
```
Access-Control-Allow-Origin: https://your-vercel-app.vercel.app
Access-Control-Allow-Methods: GET, POST, ...
```

---

## 🎯 Most Likely Solution

Based on your setup, the **most likely issue** is:

1. **`NEXT_PUBLIC_API_URL` not set in Vercel** → Set it and redeploy
2. **CORS_ORIGINS missing Vercel URL in Render** → Add it and restart

**Quick Fix**:
1. Vercel: Set `NEXT_PUBLIC_API_URL=https://your-render-backend.onrender.com/api` (all environments)
2. Render: Set `CORS_ORIGINS=https://your-vercel-app.vercel.app,https://your-vercel-app-*.vercel.app`
3. Redeploy both (Vercel: redeploy, Render: manual deploy)

---

## 📝 Environment Variables Reference

### Vercel (Frontend)
```bash
NEXT_PUBLIC_API_URL=https://your-render-backend.onrender.com/api
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=...
```

### Render (Backend)
```bash
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:6543/postgres?sslmode=require
GEMINI_API_KEY=your_gemini_key
FRED_API_KEY=your_fred_key
CORS_ORIGINS=https://your-vercel-app.vercel.app,https://your-vercel-app-*.vercel.app
```

---

## 🚨 Still Not Working?

1. **Check Render Logs**:
   - Render Dashboard → Your Service → **Logs**
   - Look for errors, especially on startup

2. **Check Vercel Logs**:
   - Vercel Dashboard → Your Project → **Deployments** → Click deployment → **Build Logs**
   - Look for build errors or warnings

3. **Test Backend Endpoints Directly**:
   ```
   https://your-render-backend.onrender.com/api/health
   https://your-render-backend.onrender.com/api/financial/tickers/available
   ```

4. **Check Browser Console**:
   - Open your Vercel site
   - F12 → Console tab
   - Look for specific error messages

---

**After fixing, test again and check the browser console for any remaining errors!** 🎉

