# ⚡ Simple Vercel Setup (No Branch Change Needed)

## 🎯 The Easy Way

You don't need to change the branch during project creation! Just use **preview deployments**.

---

## ✅ Step-by-Step

### 1. Create Project (2 min)
- Go to https://vercel.com/dashboard
- **Add New** → **Project**
- Import `SEC_exctractor`
- **Project Name**: `finq-frontend-render`
- **Root Directory**: `finq-frontend`
- **Use default branch** (main) - that's fine!
- Click **"Deploy"**

### 2. Set Environment Variables (3 min)

Go to **Settings** → **Environment Variables**:

**For Render Backend (Preview only):**
```
NEXT_PUBLIC_API_URL
Value: https://your-render-service.onrender.com/api
✅ Preview only (uncheck Production, Development)
```

**For Firebase (All environments):**
```
NEXT_PUBLIC_FIREBASE_API_KEY
✅ Production ✅ Preview ✅ Development

NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
✅ Production ✅ Preview ✅ Development

... (all other Firebase vars - set for All)
```

### 3. Push to Your Branch (1 min)

```bash
git push origin feature/nexus5.1_c_Rail_alt
```

**That's it!** Vercel will automatically create a preview deployment.

### 4. Get Preview URL

1. Go to **Deployments** tab
2. Find the preview deployment for `feature/nexus5.1_c_Rail_alt`
3. Copy the URL (e.g., `https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-[hash].vercel.app`)

### 5. Update Render CORS

Add your preview URL to Render's `CORS_ORIGINS`:
```
https://finq-frontend-render-git-feature-nexus5-1-c-rail-alt-*.vercel.app
```

---

## 🎉 Result

- ✅ **Main branch**: Production deployment (Railway backend)
- ✅ **Your branch**: Preview deployment (Render backend)
- ✅ **Both work independently**

---

**No branch switching needed!** Preview deployments are automatic. 🚀


