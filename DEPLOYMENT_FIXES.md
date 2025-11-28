# 🔧 Deployment Fixes: Railway 502 & Vercel Firebase Error

## Issue 1: Railway Backend - "Application failed to respond" (502 Error)

### Problem
Deployment shows as "SUCCESS" but accessing `https://secexctractor-production.up.railway.app/` returns 502.

### Root Cause
The start command was using an absolute path `/app/.venv/bin/python` which may not exist in Railway's environment.

### ✅ Fix Applied
Updated all Railway configuration files to use `python -m uvicorn` instead:

**Files Updated:**
- ✅ `finq-backend/railway.json` 
- ✅ `railway.toml`
- ✅ `finq-backend/nixpacks.toml`

**New Start Command:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 📋 Next Steps

1. **Commit and Push Changes:**
   ```bash
   git add finq-backend/railway.json railway.toml finq-backend/nixpacks.toml
   git commit -m "Fix: Use python -m uvicorn for Railway deployment"
   git push origin feature/nexus5.1_c_test
   ```

2. **Redeploy on Railway:**
   - Railway will automatically detect the changes and redeploy
   - Or manually trigger redeploy from Railway dashboard

3. **Verify Fix:**
   - Check Railway logs for: `Uvicorn running on http://0.0.0.0:PORT`
   - Test: `curl https://secexctractor-production.up.railway.app/api/health`
   - Should return: `{"status":"healthy"}`

---

## Issue 2: Vercel Frontend - Firebase "auth/unauthorized-domain" Error

### Problem
When trying to login through Firebase, you get:
```
Firebase: Error (auth/unauthorized-domain)
```

### Root Cause
The Vercel deployment domain is not authorized in Firebase Console.

### ✅ Fix Steps

#### Step 1: Get Your Vercel Domain

Your Vercel domain is:
```
sec-exctractor-cy8qccps0-harshit-golas-projects-ef9cdcc7.vercel.app
```

**Also add these patterns:**
- `*.vercel.app` (wildcard for all Vercel preview deployments)
- Your custom domain (if you have one)

#### Step 2: Add Domain to Firebase

1. **Go to Firebase Console:**
   - https://console.firebase.google.com/
   - Select your project: **finq-test**

2. **Navigate to Authentication Settings:**
   - Click **Authentication** (left sidebar)
   - Click **Settings** tab
   - Scroll to **"Authorized domains"** section

3. **Add Vercel Domains:**
   - Click **"Add domain"**
   - Add: `sec-exctractor-cy8qccps0-harshit-golas-projects-ef9cdcc7.vercel.app`
   - Click **"Add"**
   
   - Click **"Add domain"** again
   - Add: `*.vercel.app` (for all preview deployments)
   - Click **"Add"**

4. **Verify Domains:**
   You should now see:
   - ✅ `localhost`
   - ✅ `finq-test.firebaseapp.com`
   - ✅ `sec-exctractor-cy8qccps0-harshit-golas-projects-ef9cdcc7.vercel.app`
   - ✅ `*.vercel.app`

#### Step 3: Verify Vercel Environment Variables

1. **Go to Vercel Dashboard:**
   - https://vercel.com/harshit-golas-projects-ef9cdcc7/sec-exctractor
   - Click **Settings** → **Environment Variables**

2. **Verify These Are Set:**
   ```
   NEXT_PUBLIC_FIREBASE_API_KEY=your_key
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=finq-test.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=finq-test
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_bucket
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
   NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id
   NEXT_PUBLIC_API_URL=https://secexctractor-production.up.railway.app/api
   ```

3. **Important:** Make sure `NEXT_PUBLIC_API_URL` points to your Railway backend:
   ```
   NEXT_PUBLIC_API_URL=https://secexctractor-production.up.railway.app/api
   ```

#### Step 4: Redeploy Vercel

After adding the domain to Firebase:
1. Go to Vercel → **Deployments**
2. Click **"Redeploy"** on the latest deployment
3. Or push a new commit to trigger redeployment

#### Step 5: Test

1. Go to your Vercel URL
2. Try to sign in with Google or email/password
3. Should work without the `auth/unauthorized-domain` error

---

## 🔍 Troubleshooting

### Railway Still Shows 502

1. **Check Railway Logs:**
   - Railway → Service → **Deployments** → Latest → **Logs**
   - Look for errors like:
     - `ModuleNotFoundError`
     - `Database connection failed`
     - `Port already in use`

2. **Verify Environment Variables:**
   - Railway → Service → **Variables**
   - Ensure `DATABASE_URL` is set correctly
   - Ensure `CORS_ORIGINS` includes your Vercel domain (without trailing slash):
     ```
     CORS_ORIGINS=https://sec-exctractor-cy8qccps0-harshit-golas-projects-ef9cdcc7.vercel.app,http://localhost:3000
     ```
   - **Important:** No trailing slash after `.vercel.app`

3. **Check Start Command:**
   - Railway → Service → **Settings** → **Deploy**
   - Should be: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Firebase Still Shows Unauthorized Domain

1. **Double-check domain spelling:**
   - Must match exactly (case-sensitive)
   - No trailing slashes
   - Include protocol in some cases (check Firebase docs)

2. **Wait a few minutes:**
   - Firebase changes can take 1-2 minutes to propagate

3. **Clear browser cache:**
   - Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)

4. **Check Vercel deployment URL:**
   - The domain might have changed if you redeployed
   - Check Vercel → Deployments → Latest → **Domains**

---

## ✅ Success Checklist

- [ ] Railway backend responds to `/api/health`
- [ ] Railway logs show `Application startup complete`
- [ ] Vercel domain added to Firebase authorized domains
- [ ] `NEXT_PUBLIC_API_URL` set in Vercel environment variables
- [ ] Vercel redeployed after Firebase changes
- [ ] Can sign in via Firebase on Vercel deployment
- [ ] No `auth/unauthorized-domain` error

---

**After completing these steps, both issues should be resolved!** 🚀

