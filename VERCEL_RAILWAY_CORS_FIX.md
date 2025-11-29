# 🔧 Fix Vercel → Railway Connection (CORS Issue)

## ✅ Confirmed: Railway URL is Correct

Your Railway URL: `https://secexctractor-production-80f5.up.railway.app` ✅

The error you're seeing is likely a **CORS issue** - Railway is blocking requests from your Vercel domain.

---

## 🎯 Step 1: Update Railway CORS_ORIGINS

### 1.1 Get Your Vercel Domain

1. Go to **Vercel** → Your Project → **Deployments**
2. Click on your latest deployment
3. Look at the URL at the top (e.g., `https://your-app.vercel.app` or `https://your-app-[hash].vercel.app`)
4. Copy the full URL (including `https://`)

**Common Vercel domain formats:**
- `https://your-app.vercel.app` (production)
- `https://your-app-[random-hash].vercel.app` (preview)
- `https://your-app-git-[branch]-[username].vercel.app` (branch preview)

### 1.2 Update Railway CORS_ORIGINS

1. Go to **Railway** → Your Service → **Variables** tab
2. Find `CORS_ORIGINS`
3. Click **Edit** (or **⋮** → **Edit**)
4. Add your Vercel domain(s). Example:
   ```
   http://localhost:3000,http://localhost:8501,https://your-vercel-app.vercel.app
   ```
   
   **Important:**
   - Include `https://` (not `http://`)
   - No trailing slash
   - Separate multiple domains with commas
   - Include all your Vercel domains (production + preview if needed)
   
5. Click **Save**
6. Railway will automatically redeploy (wait ~1-2 minutes)

**Example CORS_ORIGINS:**
```
http://localhost:3000,http://localhost:8501,https://sec-exctractor-cy8qccps0-harshit-golas-projects-ef9cdcc7.vercel.app,https://sec-exctractor.vercel.app
```

---

## 🎯 Step 2: Verify Vercel Environment Variable

### 2.1 Check NEXT_PUBLIC_API_URL

1. Go to **Vercel** → Your Project → **Settings** → **Environment Variables**
2. Find `NEXT_PUBLIC_API_URL`
3. Verify it's set to:
   ```
   https://secexctractor-production-80f5.up.railway.app/api
   ```
   ⚠️ **Must include `/api` at the end!**

### 2.2 Check Environment Scope

Make sure `NEXT_PUBLIC_API_URL` is enabled for:
- ✅ **Production**
- ✅ **Preview** (if you use preview deployments)
- ✅ **Development** (if you use dev deployments)

**To check:**
- Click on `NEXT_PUBLIC_API_URL` to edit
- Look at the checkboxes under "Environment"
- Make sure all relevant environments are checked

### 2.3 If Missing or Wrong

1. Click **Edit** on `NEXT_PUBLIC_API_URL`
2. Update the value to: `https://secexctractor-production-80f5.up.railway.app/api`
3. Check all environment checkboxes
4. Click **Save**

---

## 🎯 Step 3: Redeploy Vercel

After updating environment variables:

1. Go to **Vercel** → **Deployments** tab
2. Find your latest deployment
3. Click **⋮** (three dots) → **Redeploy**
4. Wait for deployment to complete (~2-3 minutes)

**Or trigger a new deployment:**
- Make a small change and push to your branch
- Vercel will auto-deploy

---

## 🧪 Step 4: Test the Connection

### 4.1 Test Railway Directly

Open in browser:
```
https://secexctractor-production-80f5.up.railway.app/api/health
```

Should return:
```json
{"status":"healthy","service":"FinQ Backend API"}
```

### 4.2 Test from Vercel Frontend

1. Open your Vercel frontend URL
2. Open **Developer Tools** (F12) → **Console** tab
3. Check for errors
4. Try using a feature that calls the backend (e.g., load tickers)
5. Check **Network** tab:
   - Look for requests to `/api/...`
   - Check if they're successful (200 status) or failing (CORS error)

### 4.3 Check CORS Headers

1. Open **Developer Tools** (F12) → **Network** tab
2. Try to use a feature that calls the backend
3. Click on a failed request
4. Go to **Headers** tab
5. Look for:
   - **Request Headers:** Should show `Origin: https://your-vercel-app.vercel.app`
   - **Response Headers:** Should show `Access-Control-Allow-Origin: https://your-vercel-app.vercel.app`
   
   If you see `Access-Control-Allow-Origin: null` or a different domain, CORS is not configured correctly.

---

## 🔍 Debugging: Check What Frontend is Using

1. Open your Vercel frontend
2. Open **Developer Tools** (F12) → **Console** tab
3. Type:
   ```javascript
   console.log(process.env.NEXT_PUBLIC_API_URL)
   ```
4. This will show what URL the frontend is actually using
5. Verify it matches: `https://secexctractor-production-80f5.up.railway.app/api`

**Note:** If it shows `undefined`, the environment variable isn't set correctly.

---

## 📋 Complete Checklist

- [ ] Railway URL is correct: `https://secexctractor-production-80f5.up.railway.app`
- [ ] Vercel `NEXT_PUBLIC_API_URL` is set to: `https://secexctractor-production-80f5.up.railway.app/api`
- [ ] `NEXT_PUBLIC_API_URL` is enabled for all environments (Production, Preview, Development)
- [ ] Railway `CORS_ORIGINS` includes your Vercel domain(s) with `https://`
- [ ] Railway has been redeployed after updating CORS_ORIGINS
- [ ] Vercel has been redeployed after updating environment variables
- [ ] Tested Railway health endpoint directly (works ✅)
- [ ] Tested from Vercel frontend (should work now ✅)

---

## 🚨 Common CORS Error Messages

If you still see errors, check the browser console:

### Error: "Access to fetch at '...' from origin '...' has been blocked by CORS policy"
**Fix:** Add your Vercel domain to Railway `CORS_ORIGINS`

### Error: "Network Error: Cannot connect to backend API"
**Possible causes:**
1. Railway backend is down (check Railway logs)
2. Wrong URL in `NEXT_PUBLIC_API_URL`
3. Environment variable not set for the deployment you're accessing

### Error: "Failed to fetch"
**Possible causes:**
1. CORS issue (most likely)
2. Railway backend crashed (check Railway logs)
3. Network/firewall blocking the connection

---

## 🎯 Quick Fix Summary

**Most likely issue:** CORS

1. ✅ Add your Vercel domain to Railway `CORS_ORIGINS`
2. ✅ Verify `NEXT_PUBLIC_API_URL` is correct in Vercel
3. ✅ Redeploy both Railway and Vercel
4. ✅ Test again

**That should fix it!** 🚀

