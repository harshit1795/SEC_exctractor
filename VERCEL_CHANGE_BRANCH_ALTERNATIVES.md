# 🔀 Vercel Change Branch - Alternative Methods

If you can't find the "Change Production Branch" option in Settings → Git, here are alternative methods:

---

## 🎯 Method 1: Settings → General (Most Common)

1. **Vercel Dashboard** → Your Project
2. **Settings** → **General** (left sidebar)
3. Scroll down to **"Production Branch"** section
4. Click the **dropdown** or **edit icon** next to the branch name
5. Select `feature/nexus5.1_c_Rail_alt`
6. Click **"Save"**

---

## 🎯 Method 2: Promote Deployment to Production

**Easiest method if you already have a deployment from your branch!**

1. **Vercel Dashboard** → Your Project
2. **Deployments** tab
3. Find a deployment from `feature/nexus5.1_c_Rail_alt` branch
   - Look for deployments with branch name in the list
4. Click **"..."** (three dots menu) on that deployment
5. Click **"Promote to Production"**

**Result**: That branch becomes your production branch! ✅

---

## 🎯 Method 3: Use Preview Deployments (Recommended!)

**Actually, you don't need to change the branch at all!**

### How It Works:

1. **Create project** with `main` branch (default) ✅
2. **Set environment variables**:
   - `NEXT_PUBLIC_API_URL` = Render URL
   - Set for **Preview** environment only
   - Firebase vars = All environments
3. **Push to your branch**: `feature/nexus5.1_c_Rail_alt`
4. **Vercel automatically creates a preview deployment** 🎉

### Steps:

1. **Push your branch**:
   ```bash
   git push origin feature/nexus5.1_c_Rail_alt
   ```

2. **Go to Vercel Dashboard** → **Deployments** tab
3. **Find preview deployment** for `feature/nexus5.1_c_Rail_alt`
4. **Copy the preview URL** (e.g., `https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-[hash].vercel.app`)

5. **Update Render CORS** with preview URL

**That's it!** No branch switching needed. ✅

---

## 🔍 Why You Might Not See the Option

The "Change Production Branch" option might not be visible if:

1. **UI has changed** - Vercel updates their UI frequently
2. **Project is new** - Some options appear after first deployment
3. **Permissions** - You might need admin access
4. **Different plan** - Some features vary by plan

---

## ✅ Recommended Solution: Preview Deployments

**I strongly recommend using Preview Deployments (Method 3)** because:

✅ **No branch switching needed**
✅ **Automatic** - Just push to your branch
✅ **Flexible** - Each branch gets its own URL
✅ **Safe** - Doesn't affect main branch
✅ **Easy** - No UI navigation needed

---

## 📝 Quick Steps for Preview Deployments

1. **Set environment variables**:
   - `NEXT_PUBLIC_API_URL` = Render URL → **Preview** environment only
   - Firebase vars → **All** environments

2. **Push to branch**:
   ```bash
   git push origin feature/nexus5.1_c_Rail_alt
   ```

3. **Get preview URL**:
   - Vercel Dashboard → Deployments → Find preview deployment

4. **Update Render CORS**:
   - Add preview URL to `CORS_ORIGINS`

5. **Done!** ✅

---

## 🎯 Which Method Should You Use?

| Method | Difficulty | When to Use |
|--------|------------|-------------|
| **Method 1: Settings → General** | Easy | If you can find the option |
| **Method 2: Promote Deployment** | Easy | If you have a deployment from your branch |
| **Method 3: Preview Deployments** | Easiest | **Recommended** - Works always! |

---

**Recommendation**: Use **Method 3 (Preview Deployments)** - it's the easiest and most flexible! 🚀

