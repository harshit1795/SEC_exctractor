# 🔧 Add All Vercel Domains to Railway CORS

## 📋 Your Vercel Domains

You have **3 Vercel domains** that need access to Railway:

1. **Production:** `https://sec-exctractor.vercel.app`
2. **Preview (Feature Branch):** `https://sec-exctractor-git-featu-9f4636-harshit-golas-projects-ef9cdcc7.vercel.app`
3. **Preview (Another):** `https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app`

---

## ✅ Step-by-Step: Update Railway CORS_ORIGINS

### Step 1: Go to Railway Variables

1. Go to **Railway** → Your Service
2. Click **Variables** tab
3. Find `CORS_ORIGINS`
4. Click **Edit** (or **⋮** → **Edit**)

### Step 2: Update CORS_ORIGINS Value

**Copy and paste this exact value:**

```
http://localhost:3000,http://localhost:8501,https://sec-exctractor.vercel.app,https://sec-exctractor-git-featu-9f4636-harshit-golas-projects-ef9cdcc7.vercel.app,https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app
```

**Or if you want to keep your existing localhost entries, add the three Vercel domains:**

```
http://localhost:3000,http://localhost:8501,http://localhost:8080,https://sec-exctractor.vercel.app,https://sec-exctractor-git-featu-9f4636-harshit-golas-projects-ef9cdcc7.vercel.app,https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app
```

**Important:**
- ✅ Include `https://` for all Vercel domains
- ✅ No trailing slashes
- ✅ Separate with commas
- ✅ No spaces after commas (or consistent spacing)

### Step 3: Save and Wait

1. Click **Save**
2. Railway will automatically redeploy
3. Wait ~1-2 minutes for deployment to complete

---

## 🎯 Alternative: Use Wildcard (If Railway Supports It)

Some platforms support wildcards. If Railway supports it, you could use:

```
http://localhost:3000,http://localhost:8501,https://*.vercel.app
```

**However, Railway might not support wildcards**, so it's safer to list all domains explicitly.

---

## ✅ Verification

After Railway redeploys:

1. **Test Production Domain:**
   - Open `https://sec-exctractor.vercel.app`
   - Try using a feature that calls the backend
   - Check browser console (F12) for errors

2. **Test Preview Domains:**
   - Open each preview URL
   - Test backend connectivity
   - Should work now ✅

3. **Check Railway Logs:**
   - Go to Railway → Your Service → **Deployments** → Latest → **Logs**
   - Look for CORS-related errors (should be none)

---

## 📋 Quick Copy-Paste Template

**For Railway CORS_ORIGINS:**

```
http://localhost:3000,http://localhost:8501,https://sec-exctractor.vercel.app,https://sec-exctractor-git-featu-9f4636-harshit-golas-projects-ef9cdcc7.vercel.app,https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app
```

**Copy this, paste into Railway CORS_ORIGINS, save, and you're done!** ✅

---

## 🔄 Future: Adding New Preview Deployments

When Vercel creates new preview deployments, you'll need to:

1. Get the new preview URL from Vercel
2. Add it to Railway `CORS_ORIGINS`
3. Save and wait for Railway to redeploy

**Or** consider using a custom domain for production to avoid this issue.

---

## 🎯 Summary

**What to do:**
1. ✅ Go to Railway → Variables → `CORS_ORIGINS`
2. ✅ Add all 3 Vercel domains (with `https://`)
3. ✅ Save
4. ✅ Wait for Railway to redeploy
5. ✅ Test all three Vercel URLs

**That's it!** 🚀

