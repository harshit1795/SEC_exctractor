# ⚡ Vercel Render Setup - Quick Start (5 Minutes)

## 🎯 Quick Steps

### 1. Get Render URL (30 sec)
- Render Dashboard → Your Service → Copy URL
- Example: `https://finq-backend.onrender.com`

### 2. Create Vercel Project (1 min)
- Vercel Dashboard → "Add New" → "Project"
- Import: `SEC_exctractor`
- **Project Name**: `finq-frontend-render`
- **Root Directory**: `finq-frontend`
- **Production Branch**: `main` (default - that's OK! ✅)
  - You can change it later OR use preview deployments (see below)

### 3. Set Environment Variables (2 min)

**Option A - Change Branch Later:**
- Set `NEXT_PUBLIC_API_URL` for all environments
- After deployment: Settings → Git → Change Production Branch

**Option B - Use Preview Deployments (Recommended!):**
- Set `NEXT_PUBLIC_API_URL` for **Preview** environment only
- Push to `feature/nexus5.1_c_Rail_alt` → Auto-creates preview deployment

**Backend URL (Render):**
```
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api
```

**Firebase** (copy from Railway Vercel project):
- Copy all `NEXT_PUBLIC_FIREBASE_*` variables
- Set for: ✅ Production ✅ Preview ✅ Development

### 4. Deploy (1 min)
- Click "Deploy" (even with `main` branch - that's fine!)
- Wait 2-5 minutes

**Then choose one:**
- **Option A**: Settings → Git → Change Production Branch to `feature/nexus5.1_c_Rail_alt`
- **Option B**: Push to `feature/nexus5.1_c_Rail_alt` → Get preview URL

### 5. Update Render CORS (30 sec)
- Render Dashboard → Environment
- Add Vercel URL to `CORS_ORIGINS`:
```
https://sec-exctractor.vercel.app,https://finq-frontend-render.vercel.app,https://sec-exctractor-git-*.vercel.app
```

### 6. Test! (1 min)
- Open: `https://finq-frontend-render.vercel.app`
- Test FinQ Chat → Should work! ✅

---

## ✅ Checklist

- [ ] Render URL copied
- [ ] Vercel project created
- [ ] Branch set to `feature/nexus5.1_c_Rail_alt`
- [ ] `NEXT_PUBLIC_API_URL` = Render URL
- [ ] Firebase vars copied from Railway
- [ ] Deployed successfully
- [ ] Render CORS updated
- [ ] FinQ Chat tested and working

---

## 📚 More Info

- **Full Guide**: `VERCEL_RENDER_SETUP_GUIDE.md`
- **Branch Options**: `VERCEL_BRANCH_SETUP_OPTIONS.md` (explains both approaches)

