# 🔀 Vercel Branch Setup - Two Easy Options

You're seeing `main` as the default branch when creating a new Vercel project. **That's totally fine!** Here are two easy ways to handle this:

---

## ✅ Option A: Change Branch After Creation (Simple)

### Step 1: Create Project with Main (Default)
- Just proceed with `main` as the production branch
- Complete the setup and deploy

### Step 2: Change Production Branch Later

**Method 1: Via Settings → General**
1. **Go to Vercel Dashboard** → Your new project
2. **Settings** → **General** (left sidebar)
3. Scroll to **"Production Branch"** section
4. Click the **dropdown** or **edit icon** next to "Production Branch"
5. Select `feature/nexus5.1_c_Rail_alt`
6. Click **"Save"**

**Method 2: Via Project Settings (Alternative)**
1. **Go to Vercel Dashboard** → Your new project
2. **Settings** → **Git** (left sidebar)
3. Look for **"Production Branch"** or **"Git Repository"** section
4. Click **"Edit"** or the branch name
5. Select `feature/nexus5.1_c_Rail_alt`
6. Click **"Save"**

**Method 3: Via Deployments Tab**
1. **Go to Vercel Dashboard** → Your new project
2. **Deployments** tab
3. Find a deployment from `feature/nexus5.1_c_Rail_alt` branch
4. Click **"..."** (three dots) → **"Promote to Production"**

**Note**: If you don't see these options, use **Option B (Preview Deployments)** instead - it's easier and doesn't require changing the branch!

---

## ✅ Option B: Use Preview Deployments (Recommended!)

**Even easier** - you don't need to change the branch at all!

### How It Works:
1. **Create project** with `main` branch (default) ✅
2. **Set environment variables**:
   - `NEXT_PUBLIC_API_URL` = Render URL
   - Set for **Preview** environment only (not Production)
3. **Push to your branch**: `feature/nexus5.1_c_Rail_alt`
4. **Vercel automatically creates a preview deployment** 🎉

### Detailed Steps:

#### Step 1: Create Project (Use Main)
- Create project normally with `main` branch
- Complete deployment

#### Step 2: Set Preview Environment Variables
1. **Settings** → **Environment Variables**
2. Click **"Add New"**
3. Add `NEXT_PUBLIC_API_URL`:
   - **Value**: `https://your-render-service.onrender.com/api`
   - **Environments**: ✅ **Preview** (uncheck Production and Development)
   - Click **"Save"**

4. **Firebase variables**:
   - Set for ✅ **Production** ✅ **Preview** ✅ **Development** (all)

#### Step 3: Push to Your Branch
```bash
git push origin feature/nexus5.1_c_Rail_alt
```

#### Step 4: Get Preview URL
1. **Vercel Dashboard** → **Deployments** tab
2. Find preview deployment for `feature/nexus5.1_c_Rail_alt`
3. Copy the URL (e.g., `https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-[hash].vercel.app`)

#### Step 5: Update Render CORS
- Add preview URL to Render's `CORS_ORIGINS`

---

## 📊 Comparison

| Approach | Pros | Cons |
|----------|------|------|
| **Option A: Change Branch** | Simple, one production deployment | Need to change branch manually |
| **Option B: Preview Deployments** | Automatic, flexible, no branch switching | Preview URL has hash suffix |

---

## 🎯 Recommendation

**I recommend Option B (Preview Deployments)** because:

✅ **No branch switching needed** - just push to your branch
✅ **Automatic** - Vercel creates preview deployments automatically
✅ **Flexible** - Can have multiple preview deployments
✅ **Easy to test** - Each branch gets its own URL
✅ **Safe** - Doesn't affect main branch deployment

---

## 🔍 How to Find Your Preview Deployment

After pushing to `feature/nexus5.1_c_Rail_alt`:

1. **Vercel Dashboard** → Your Project → **Deployments** tab
2. You'll see:
   - **Production**: `main` branch deployment
   - **Preview**: `feature/nexus5.1_c_Rail_alt` branch deployment
3. Click on the preview deployment
4. Copy the URL

**Preview URL format**: `https://[project-name]-git-[branch-name]-[hash].vercel.app`

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
Environments: ✅ Preview (uncheck Production, Development)

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

## ✅ Quick Steps Summary

### Option A (Change Branch):
1. ✅ Create project (use `main` - default)
2. ✅ Set environment variables
3. ✅ Deploy
4. ✅ Settings → Git → Change Production Branch to `feature/nexus5.1_c_Rail_alt`
5. ✅ Vercel auto-redeploys

### Option B (Preview Deployments):
1. ✅ Create project (use `main` - default)
2. ✅ Set environment variables:
   - Render URL → **Preview** environment
   - Firebase → **All** environments
3. ✅ Deploy
4. ✅ Push to `feature/nexus5.1_c_Rail_alt` branch
5. ✅ Vercel auto-creates preview deployment
6. ✅ Update Render CORS with preview URL

---

**Both options work great!** Choose whichever feels easier to you. 🚀

