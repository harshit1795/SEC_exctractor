# 🔧 Troubleshoot: Cannot Connect to Backend API

If you're seeing "cannot connect to backend API" error, follow these steps:

---

## 🔍 Step 1: Check Environment Variables in Vercel

The most common cause is missing or incorrect `NEXT_PUBLIC_API_URL`.

1. **Go to Vercel Dashboard** → Your Project
2. **Settings** → **Environment Variables**
3. **Verify `NEXT_PUBLIC_API_URL` is set**:
   - **Value**: `https://your-render-service.onrender.com/api`
   - **Environments**: ✅ **Preview** (for preview deployments)
   - **Important**: Must include `/api` at the end

**If missing or wrong:**
- Add/Update the variable
- Set for **Preview** environment (if using preview deployment)
- **Redeploy** Vercel (env vars require redeploy)

---

## 🔍 Step 2: Verify Render Backend is Running

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click on your backend service**
3. **Check status**: Should be "Live" ✅
4. **Test backend directly**:
   - Open: `https://your-render-service.onrender.com/api/health`
   - Should return: `{"status":"healthy","service":"FinQ Backend API"}`

**If backend is not running:**
- Check Render logs for errors
- Verify deployment completed successfully

---

## 🔍 Step 3: Check CORS Configuration

**Critical**: Render must allow your Vercel URL in CORS settings.

1. **Render Dashboard** → Your Service → **Environment** tab
2. **Find `CORS_ORIGINS`** variable
3. **Verify it includes your Vercel preview URL**:
   ```
   https://sec-exctractor.vercel.app,https://finq-frontend-render-git-*.vercel.app,https://sec-exctractor-git-*.vercel.app
   ```

**If missing:**
- Add your Vercel preview URL (use `*` wildcard for preview URLs)
- Render will auto-redeploy after saving

---

## 🔍 Step 4: Check Browser Console

1. **Open your Vercel deployment** in browser
2. **Open DevTools** (F12)
3. **Go to Console** tab
4. **Look for errors**:
   - CORS errors: `CORS policy: No 'Access-Control-Allow-Origin' header`
   - Network errors: `Network Error` or `Failed to fetch`
   - Wrong URL: Check if API calls go to correct backend

---

## 🔍 Step 5: Check Network Tab

1. **Open DevTools** (F12) → **Network** tab
2. **Try to use the app** (navigate to dashboard, etc.)
3. **Look at API requests**:
   - **Should go to**: `https://your-render-service.onrender.com/api/...`
   - **Should NOT go to**: `http://localhost:8000/api` or Railway URL

**If wrong URL:**
- Environment variable not set correctly
- Need to redeploy after setting env vars

---

## 🔧 Common Issues & Fixes

### Issue 1: Environment Variable Not Set

**Error**: API calls go to `http://localhost:8000/api` (default)

**Fix**:
1. Vercel Dashboard → Settings → Environment Variables
2. Add `NEXT_PUBLIC_API_URL` = `https://your-render-service.onrender.com/api`
3. Set for **Preview** environment
4. **Redeploy** Vercel

---

### Issue 2: CORS Error

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Fix**:
1. Render Dashboard → Environment → `CORS_ORIGINS`
2. Add Vercel URL: `https://finq-frontend-render-git-*.vercel.app`
3. Wait for Render to redeploy

---

### Issue 3: Backend Not Running

**Error**: `Network Error` or `Failed to fetch`

**Fix**:
1. Check Render Dashboard → Service status
2. Check Render logs for errors
3. Verify backend deployment completed
4. Test backend URL directly: `https://your-render-service.onrender.com/api/health`

---

### Issue 4: Wrong Environment Variable Scope

**Error**: Variable set but not applied to preview deployment

**Fix**:
1. Vercel Dashboard → Settings → Environment Variables
2. Check `NEXT_PUBLIC_API_URL` is set for **Preview** environment
3. If only set for Production, add it for Preview too
4. **Redeploy** Vercel

---

## ✅ Quick Fix Checklist

- [ ] `NEXT_PUBLIC_API_URL` set in Vercel
- [ ] Value = `https://your-render-service.onrender.com/api` (with `/api`)
- [ ] Set for **Preview** environment (for preview deployments)
- [ ] Render backend is **Live** and running
- [ ] Render `CORS_ORIGINS` includes Vercel URL
- [ ] Vercel redeployed after setting env vars
- [ ] Test backend directly: `/api/health` works

---

## 🧪 Test Backend Connection

### Test 1: Direct Backend Test

Open in browser:
```
https://your-render-service.onrender.com/api/health
```

**Expected**: `{"status":"healthy","service":"FinQ Backend API"}`

### Test 2: Check Environment Variable

In browser console (on your Vercel deployment):
```javascript
console.log(process.env.NEXT_PUBLIC_API_URL)
```

**Expected**: `https://your-render-service.onrender.com/api`

### Test 3: Check Network Requests

1. Open DevTools → Network tab
2. Use the app
3. Check API requests go to Render backend

---

## 📝 Step-by-Step Fix

### If Environment Variable is Missing:

1. **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. **Click "Add New"**
3. **Key**: `NEXT_PUBLIC_API_URL`
4. **Value**: `https://your-render-service.onrender.com/api`
   - Replace `your-render-service.onrender.com` with your actual Render URL
5. **Environments**: ✅ **Preview** (uncheck Production, Development if using preview)
6. **Click "Save"**
7. **Redeploy**: Go to Deployments → Click "..." → "Redeploy"

### If CORS Error:

1. **Render Dashboard** → Your Service → **Environment**
2. **Find `CORS_ORIGINS`**
3. **Add**: `https://finq-frontend-render-git-*.vercel.app`
4. **Save** (Render auto-redeploys)

---

## 🎯 Most Likely Cause

For preview deployments, the issue is usually:

1. **`NEXT_PUBLIC_API_URL` not set for Preview environment** → Fix: Set it for Preview
2. **CORS not configured** → Fix: Add Vercel URL to Render CORS
3. **Backend not running** → Fix: Check Render service status

---

**Need more help?** Share:
- The exact error message from browser console
- What you see in Network tab
- Whether backend health endpoint works directly

