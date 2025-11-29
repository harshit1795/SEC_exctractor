# 🔄 Update Vercel Backend URL - Quick Guide

## ✅ Backend Status: WORKING! 🎉

Your Railway backend is now working at:
```
https://ecexctractor-production-80f5.up.railway.app
```

The JSON response you saw confirms the backend is running correctly!

---

## 📋 Step 1: Update Vercel Environment Variable

### 1.1 Go to Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Select your project
3. Go to **Settings** → **Environment Variables**

### 1.2 Update `NEXT_PUBLIC_API_URL`

1. Find the variable `NEXT_PUBLIC_API_URL`
2. Click **Edit** (or **⋮** → **Edit**)
3. Update the value to:
   ```
   https://ecexctractor-production-80f5.up.railway.app/api
   ```
   ⚠️ **Important**: Include `/api` at the end!
4. Make sure **Production**, **Preview**, and **Development** are all checked
5. Click **Save**

---

## 📋 Step 2: Update Railway CORS Origins (Important!)

Your Railway backend needs to allow requests from your Vercel domain.

### 2.1 Get Your Vercel Domain

Your Vercel frontend URL should be something like:
- `https://your-app.vercel.app` or
- `https://your-app-[hash].vercel.app`

### 2.2 Update Railway CORS_ORIGINS

1. Go to **Railway** → Your Service → **Variables** tab
2. Find `CORS_ORIGINS`
3. Click **Edit**
4. Update the value to include your Vercel domain:
   ```
   http://localhost:3000,https://your-vercel-app.vercel.app
   ```
   Replace `your-vercel-app.vercel.app` with your actual Vercel domain.
   
   **Example:**
   ```
   http://localhost:3000,https://sec-exctractor-cy8qccps0-harshit-golas-projects-ef9cdcc7.vercel.app
   ```
5. Click **Save**
6. Railway will automatically redeploy

---

## 📋 Step 3: Redeploy Vercel

After updating the environment variable:

1. Go to **Deployments** tab in Vercel
2. Click **⋮** (three dots) on the latest deployment
3. Click **Redeploy**
4. Wait for deployment to complete (~2-3 minutes)

---

## ✅ Verification Checklist

After redeploying, verify:

- [ ] Vercel environment variable `NEXT_PUBLIC_API_URL` is set to `https://ecexctractor-production-80f5.up.railway.app/api`
- [ ] Railway `CORS_ORIGINS` includes your Vercel domain
- [ ] Vercel deployment completed successfully
- [ ] Frontend can make API calls to the backend (check browser console for errors)

---

## 🧪 Test the Connection

1. Open your Vercel frontend URL
2. Open browser **Developer Tools** (F12) → **Console** tab
3. Try logging in or using any feature that calls the backend
4. Check for any network errors in the **Network** tab

If you see errors like:
- `Network Error: Cannot connect to backend API` → The `NEXT_PUBLIC_API_URL` might be wrong
- `CORS error` → The `CORS_ORIGINS` in Railway needs to include your Vercel domain

---

## 🎯 Quick Summary

**What to do:**
1. ✅ Update `NEXT_PUBLIC_API_URL` in Vercel to: `https://ecexctractor-production-80f5.up.railway.app/api`
2. ✅ Update `CORS_ORIGINS` in Railway to include your Vercel domain
3. ✅ Redeploy Vercel

**That's it!** 🚀

