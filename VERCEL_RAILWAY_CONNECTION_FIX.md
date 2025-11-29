# 🔧 Fix Vercel → Railway Connection Error

## 🐛 Error You're Seeing

```
Network Error: Cannot connect to backend API at 
https://secexctractor-production-80f5.up.railway.app/api
```

## 🔍 Issues to Check

### Issue 1: URL Typo ⚠️ **MOST LIKELY**

**The error shows:** `secexctractor-production-80f5` (with "s")  
**The working URL is:** `ecexctractor-production-80f5` (without "s")

**Fix:**
1. Go to **Vercel** → **Settings** → **Environment Variables**
2. Find `NEXT_PUBLIC_API_URL`
3. Make sure it's exactly:
   ```
   https://ecexctractor-production-80f5.up.railway.app/api
   ```
   ⚠️ **No "s" in "ecexctractor"** - it's `ecexctractor`, not `secexctractor`
4. Click **Save**
5. **Redeploy** your Vercel project

---

### Issue 2: CORS Configuration ⚠️ **ALSO CRITICAL**

Your Railway backend must allow requests from your Vercel domain.

**Fix:**

1. **Get your Vercel domain:**
   - Go to Vercel → Your Project → **Deployments**
   - Look at the URL of your deployment (e.g., `https://your-app.vercel.app` or `https://your-app-[hash].vercel.app`)

2. **Update Railway CORS_ORIGINS:**
   - Go to **Railway** → Your Service → **Variables** tab
   - Find `CORS_ORIGINS`
   - Click **Edit**
   - Add your Vercel domain. Example:
     ```
     http://localhost:3000,https://your-vercel-app.vercel.app
     ```
   - **Important:** Include the full URL with `https://`
   - **Important:** No trailing slash
   - Click **Save**
   - Railway will automatically redeploy

**Example CORS_ORIGINS:**
```
http://localhost:3000,http://localhost:8501,https://sec-exctractor-cy8qccps0-harshit-golas-projects-ef9cdcc7.vercel.app
```

---

### Issue 3: Multiple Vercel Deployments

If you have multiple deployments (Production, Preview, Development), you need to:

1. **Set environment variable for each environment:**
   - In Vercel → **Settings** → **Environment Variables**
   - When adding/editing `NEXT_PUBLIC_API_URL`, make sure to check:
     - ✅ **Production**
     - ✅ **Preview** (if you use preview deployments)
     - ✅ **Development** (if you use dev deployments)

2. **Redeploy each environment:**
   - Go to **Deployments** tab
   - Find the deployment you're accessing
   - Click **⋮** → **Redeploy**

---

## ✅ Step-by-Step Fix

### Step 1: Verify Railway URL

1. Open your Railway backend URL directly in browser:
   ```
   https://ecexctractor-production-80f5.up.railway.app
   ```
2. You should see:
   ```json
   {"message":"FinQ Backend API","version":"0.1.0","docs":"/docs","health":"/api/health"}
   ```
3. If this works, the Railway URL is correct ✅

### Step 2: Fix Vercel Environment Variable

1. Go to **Vercel** → Your Project → **Settings** → **Environment Variables**
2. Find `NEXT_PUBLIC_API_URL`
3. **Delete it** (if it has the wrong URL)
4. **Add it again** with the correct value:
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://ecexctractor-production-80f5.up.railway.app/api`
   - **Environments:** Check all (Production, Preview, Development)
5. Click **Save**

### Step 3: Update Railway CORS

1. Go to **Railway** → Your Service → **Variables**
2. Find `CORS_ORIGINS`
3. Click **Edit**
4. Add your Vercel domain. Get it from:
   - Vercel → Deployments → Click on a deployment → Look at the URL
5. Update to something like:
   ```
   http://localhost:3000,https://your-actual-vercel-domain.vercel.app
   ```
6. Click **Save**

### Step 4: Redeploy Both

1. **Railway:** Will auto-redeploy after saving CORS_ORIGINS
2. **Vercel:** Go to Deployments → Click **Redeploy** on the latest deployment

### Step 5: Test

1. Open your Vercel frontend URL
2. Open browser **Developer Tools** (F12) → **Console** tab
3. Check for errors
4. Try using a feature that calls the backend
5. Check **Network** tab to see if API calls are successful

---

## 🔍 Debugging Tips

### Check What URL Frontend is Using

1. Open your Vercel frontend
2. Open **Developer Tools** (F12) → **Console**
3. Type:
   ```javascript
   console.log(process.env.NEXT_PUBLIC_API_URL)
   ```
4. This will show what URL the frontend is actually using

### Test Railway API Directly

```bash
# Test health endpoint
curl https://ecexctractor-production-80f5.up.railway.app/api/health

# Should return:
# {"status":"healthy","service":"FinQ Backend API"}
```

### Check CORS in Browser

1. Open **Developer Tools** (F12) → **Network** tab
2. Try to use a feature that calls the backend
3. Look for failed requests
4. Click on a failed request → **Headers** tab
5. Look for CORS errors in the response headers

---

## 📋 Quick Checklist

- [ ] Railway URL is correct: `https://ecexctractor-production-80f5.up.railway.app` (no "s" in "ecexctractor")
- [ ] Vercel `NEXT_PUBLIC_API_URL` is set to: `https://ecexctractor-production-80f5.up.railway.app/api`
- [ ] Railway `CORS_ORIGINS` includes your Vercel domain (with `https://`)
- [ ] Environment variable is set for all environments (Production, Preview, Development)
- [ ] Both Railway and Vercel have been redeployed after changes
- [ ] Browser cache cleared (try incognito mode)

---

## 🎯 Most Common Fix

**99% of the time, it's one of these:**

1. **URL typo:** `secexctractor` instead of `ecexctractor` ❌
2. **Missing CORS:** Vercel domain not in Railway `CORS_ORIGINS` ❌
3. **Wrong environment:** Environment variable not set for the deployment you're accessing ❌

**Fix all three, and it should work!** ✅

