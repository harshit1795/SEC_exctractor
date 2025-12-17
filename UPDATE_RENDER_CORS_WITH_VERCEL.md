# 🔧 Update Render CORS with New Vercel Deployment URL

## 🎯 How to Find Your New Vercel Preview URL

### Step 1: Go to Vercel Dashboard

1. **Open Vercel Dashboard**: https://vercel.com/dashboard
2. **Click on your new project** (the one for Render, e.g., `finq-frontend-render`)

### Step 2: Go to Deployments Tab

1. **Click "Deployments"** tab (top navigation)
2. **Find the deployment** for `feature/nexus5.1_c_Rail_alt` branch
3. **Look for the preview deployment** (it will say "Preview" badge)

### Step 3: Copy the URL

1. **Click on the preview deployment** to open it
2. **Copy the URL** from the top of the page
   - It looks like: `https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-[hash].vercel.app`
   - Or: `https://[project-name]-git-[branch-name]-[hash].vercel.app`

**This is your new Render Vercel deployment URL!**

---

## 📝 Understanding Vercel URL Patterns

### Preview Deployment URLs:

**Pattern**: `https://[project-name]-git-[branch-name]-[hash].vercel.app`

**Example**:
```
https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-abc123.vercel.app
```

**Components**:
- `finq-frontend-render` = Your project name
- `git` = Indicates it's a Git deployment
- `feature-nexus5-1-c-rail-alt` = Your branch name (hyphenated)
- `abc123` = Unique hash for this deployment

### Using Wildcards:

You can use a **wildcard** (`*`) to match all preview deployments from a branch:

```
https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-*.vercel.app
```

This matches:
- `https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-abc123.vercel.app`
- `https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-xyz789.vercel.app`
- Any future deployments from that branch

---

## 🔧 Update Render CORS_ORIGINS

### Current Value (Railway Vercel URLs):

```
https://sec-exctractor.vercel.app,https://sec-exctractor-git-featu-9f4636-harshit-golas-projects-ef9cdcc7.vercel.app,https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app
```

### Updated Value (Add Render Vercel URL):

**Option 1: Use Wildcard (Recommended)**

```
https://sec-exctractor.vercel.app,https://sec-exctractor-git-featu-9f4636-harshit-golas-projects-ef9cdcc7.vercel.app,https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app,https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-*.vercel.app
```

**Option 2: Use Specific URL (If you have the exact URL)**

```
https://sec-exctractor.vercel.app,https://sec-exctractor-git-featu-9f4636-harshit-golas-projects-ef9cdcc7.vercel.app,https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app,https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-[your-hash].vercel.app
```

**Replace `[your-hash]` with the actual hash from your deployment URL!**

---

## ✅ Step-by-Step: Update in Render

### Step 1: Get Your Vercel Preview URL

1. **Vercel Dashboard** → Your Render project → **Deployments** tab
2. **Find preview deployment** for `feature/nexus5.1_c_Rail_alt`
3. **Copy the URL** (or use wildcard pattern)

### Step 2: Go to Render Environment Variables

1. **Render Dashboard**: https://dashboard.render.com
2. **Click on your backend service** (e.g., `finq-backend`)
3. **Click "Environment"** tab

### Step 3: Edit CORS_ORIGINS

1. **Find `CORS_ORIGINS`** in the list
2. **Click "Edit"** button
3. **Add your new Vercel URL** to the existing list:

**Copy this (with wildcard):**
```
https://sec-exctractor.vercel.app,https://sec-exctractor-git-featu-9f4636-harshit-golas-projects-ef9cdcc7.vercel.app,https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app,https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-*.vercel.app
```

**Or if you have the exact URL, replace `*` with the hash:**
```
https://sec-exctractor.vercel.app,https://sec-exctractor-git-featu-9f4636-harshit-golas-projects-ef9cdcc7.vercel.app,https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app,https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-[YOUR-HASH].vercel.app
```

4. **Click "Save"**
5. **Render will auto-redeploy** with the updated CORS settings

---

## 🎯 Quick Reference: URL Patterns

### Railway Vercel URLs (Keep These):
- `https://sec-exctractor.vercel.app` (Production)
- `https://sec-exctractor-git-featu-9f4636-harshit-golas-projects-ef9cdcc7.vercel.app` (Preview)
- `https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app` (Preview)

### Render Vercel URL (Add This):
- `https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-*.vercel.app` (Preview with wildcard)
- OR `https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-[hash].vercel.app` (Specific)

---

## 📋 Complete CORS_ORIGINS Value

**Copy and paste this into Render (with wildcard):**

```
https://sec-exctractor.vercel.app,https://sec-exctractor-git-featu-9f4636-harshit-golas-projects-ef9cdcc7.vercel.app,https://sec-exctractor-r4du6r9tl-harshit-golas-projects-ef9cdcc7.vercel.app,https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-*.vercel.app
```

**Important Notes:**
- ✅ **Comma-separated** (no spaces after commas)
- ✅ **No quotes** needed
- ✅ **Wildcard `*`** matches all preview deployments from that branch
- ✅ **Keep all Railway URLs** - they're still needed

---

## 🔍 How to Derive the URL Pattern

### If You Know Your Project Name:

1. **Project name**: `finq-frontend-render`
2. **Branch name**: `feature/nexus5.1_c_Rail_alt`
3. **Convert branch to URL format**: `feature-nexus5-1-c-rail-alt` (hyphens, lowercase)
4. **Pattern**: `https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-*.vercel.app`

### If You Have the Exact URL:

1. **Copy the full URL** from Vercel Deployments
2. **Use it as-is** (specific URL)
3. **Or replace the hash with `*`** (wildcard pattern)

---

## ✅ Verification Checklist

After updating CORS_ORIGINS:

- [ ] **Vercel preview URL copied** (or pattern derived)
- [ ] **CORS_ORIGINS updated** in Render
- [ ] **All Railway URLs kept** (not removed)
- [ ] **New Render URL added** (with wildcard or specific)
- [ ] **Render redeployed** (auto after saving)
- [ ] **Test frontend** - should connect to backend now!

---

## 🧪 Test After Update

1. **Wait for Render to redeploy** (1-2 minutes)
2. **Open your Vercel preview deployment**
3. **Try to use the app** (navigate to dashboard)
4. **Check browser console** - should not see CORS errors
5. **Test API calls** - should work now!

---

## 💡 Pro Tips

1. **Use wildcard (`*`)** - Covers all future preview deployments from that branch
2. **Keep Railway URLs** - Your Railway deployment still needs them
3. **No spaces** - Comma-separated, no spaces after commas
4. **Test after update** - Wait for Render redeploy, then test

---

**Need Help?** If you can't find your Vercel preview URL, check the Deployments tab in your Vercel project!

