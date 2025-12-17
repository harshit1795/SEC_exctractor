# 🔄 How to Change Branch in Vercel After Project Creation

## ✅ Quick Solution

You can create the project now and change the branch later. Here's how:

---

## 🚀 Step 1: Create Project (Use Default Branch for Now)

1. **Create New Project** in Vercel
2. **Import** your `SEC_exctractor` repository
3. **Project Name**: `finq-frontend-render`
4. **Root Directory**: `finq-frontend`
5. **Use default branch** (probably `main`) - that's fine for now!
6. **Click "Deploy"**

This will create the project. We'll change the branch next.

---

## 🔧 Step 2: Change Production Branch (After Deployment)

### Method 1: Via Settings (Recommended)

1. **Go to your new project** in Vercel Dashboard
2. Click **"Settings"** (top navigation)
3. Click **"Git"** (left sidebar)
4. Scroll to **"Production Branch"** section
5. Click the **dropdown** next to "Production Branch"
6. **Select**: `feature/nexus5.1_c_Rail_alt`
7. **Click "Save"**

Vercel will automatically redeploy using the new branch!

### Method 2: Via Project Settings → General

1. Go to **Settings** → **General**
2. Find **"Production Branch"** field
3. Change from `main` to `feature/nexus5.1_c_Rail_alt`
4. Click **"Save"**

---

## 🎯 Alternative: Use Preview Deployments (Easier!)

Actually, you don't even need to change the production branch! Vercel automatically creates **preview deployments** for all branches.

### How It Works:

1. **Create project** with default branch (`main`)
2. **Set environment variables** (see below)
3. **Push to your branch**: `feature/nexus5.1_c_Rail_alt`
4. **Vercel automatically creates a preview deployment** for that branch!

### Set Branch-Specific Environment Variables:

1. Go to **Settings** → **Environment Variables**
2. Add `NEXT_PUBLIC_API_URL`:
   - **Value**: `https://your-render-service.onrender.com/api`
   - **Environments**: Select **"Preview"** ✅ (this applies to all non-main branches)
   - Click **"Save"**

3. **For Production branch** (main), you can either:
   - Leave it empty (won't affect main branch)
   - Or set it to Railway URL for Production environment

### Result:

- **Main branch** → Production deployment (uses Railway if you set Production env vars)
- **feature/nexus5.1_c_Rail_alt** → Preview deployment (uses Render via Preview env vars)

---

## 📋 Complete Setup Checklist

### Option A: Change Production Branch Later

- [ ] Create new Vercel project (use default branch)
- [ ] Set environment variables (see below)
- [ ] Deploy (will use main branch initially)
- [ ] Go to Settings → Git → Change Production Branch to `feature/nexus5.1_c_Rail_alt`
- [ ] Vercel will auto-redeploy with new branch
- [ ] Update Render CORS with new Vercel URL

### Option B: Use Preview Deployments (Recommended)

- [ ] Create new Vercel project (use default branch)
- [ ] Set environment variables:
  - [ ] `NEXT_PUBLIC_API_URL` = Render URL (set for **Preview** environment)
  - [ ] Firebase config (set for **All** environments)
- [ ] Deploy (creates main branch deployment)
- [ ] Push to `feature/nexus5.1_c_Rail_alt` branch
- [ ] Vercel automatically creates preview deployment
- [ ] Update Render CORS with preview URL

---

## 🔍 How to Find Your Preview Deployment URL

After pushing to `feature/nexus5.1_c_Rail_alt`:

1. Go to **Vercel Dashboard** → Your Project
2. Click **"Deployments"** tab
3. You'll see:
   - **Production**: `main` branch deployment
   - **Preview**: `feature/nexus5.1_c_Rail_alt` branch deployment
4. Click on the preview deployment
5. Copy the URL (e.g., `https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-[hash].vercel.app`)

---

## ⚙️ Environment Variables Setup

### For Preview Deployments (Render Branch):

1. **Settings** → **Environment Variables**
2. Click **"Add New"**
3. Add each variable:

```bash
# Render Backend (Preview only)
NEXT_PUBLIC_API_URL
Value: https://your-render-service.onrender.com/api
Environments: ✅ Preview (uncheck Production and Development)

# Firebase (All environments)
NEXT_PUBLIC_FIREBASE_API_KEY
Value: [your key]
Environments: ✅ Production ✅ Preview ✅ Development

NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
Value: [your domain]
Environments: ✅ Production ✅ Preview ✅ Development

# ... (all other Firebase vars - set for All environments)
```

---

## 🎯 Recommended Approach

**I recommend Option B (Preview Deployments)** because:

✅ **No branch switching needed** - just push to your branch
✅ **Automatic** - Vercel creates preview deployments automatically
✅ **Flexible** - Can have multiple preview deployments
✅ **Easy to test** - Each branch gets its own URL

---

## 📝 Quick Steps Summary

1. ✅ **Create project** (use default branch - that's fine!)
2. ✅ **Set environment variables**:
   - Render URL → **Preview** environment
   - Firebase → **All** environments
3. ✅ **Push to your branch**: `git push origin feature/nexus5.1_c_Rail_alt`
4. ✅ **Vercel auto-creates preview deployment**
5. ✅ **Update Render CORS** with preview URL
6. ✅ **Test!**

---

## 🔗 Useful Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Project Settings**: https://vercel.com/dashboard → Your Project → Settings
- **Deployments**: https://vercel.com/dashboard → Your Project → Deployments

---

**Need Help?** The preview deployment approach is usually easier and more flexible!


