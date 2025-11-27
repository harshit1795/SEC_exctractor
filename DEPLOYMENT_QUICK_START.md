# 🚀 Quick Start: Deploy FinQ to Production

**Time Required**: 30-45 minutes  
**Cost**: $0-5/month (starting with free tiers)

---

## 🎯 Three-Step Deployment

### Step 1: Database (Supabase) - 10 minutes

1. **Create Account**: [supabase.com](https://supabase.com) → Sign up
2. **New Project**: Name it `finq-production`
3. **Get Connection String**: Settings → Database → Connection string (URI)
4. **Save Password**: You'll need it for Railway

### Step 2: Backend (Railway) - 15 minutes

1. **Create Account**: [railway.app](https://railway.app) → Sign up with GitHub
2. **New Project**: Deploy from GitHub → Select `SEC_exctractor` repo
3. **Select Branch**: Choose your branch from the dropdown (or set it in Settings → Source after creation)
4. **Set Root Directory**: Go to Settings → Build → Set `finq-backend`
4. **Add Environment Variables**:
   ```bash
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
   GEMINI_API_KEY=your-key
   FRED_API_KEY=your-key
   CORS_ORIGINS=http://localhost:3000
   ```
5. **Deploy**: Railway auto-deploys
6. **Get URL**: `https://your-app.up.railway.app`

### Step 3: Frontend (Vercel) - 10 minutes

1. **Create Account**: [vercel.com](https://vercel.com) → Sign up with GitHub
2. **Import Project**: Add repository → Select `SEC_exctractor`
3. **Set Root Directory**: `finq-frontend`
4. **Add Environment Variables**:
   ```bash
   NEXT_PUBLIC_FIREBASE_API_KEY=your-key
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
   NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
   NEXT_PUBLIC_API_URL=https://your-app.up.railway.app/api
   ```
5. **Deploy**: Vercel auto-deploys
6. **Get URL**: `https://your-app.vercel.app`

### Step 4: Connect Everything - 5 minutes

1. **Update Backend CORS**: Add Vercel URL to Railway env vars:
   ```bash
   CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
   ```
2. **Run Migrations**: 
   ```bash
   export DATABASE_URL="your-supabase-connection-string"
   cd finq-backend
   alembic upgrade head
   ```
3. **Test**: Visit your Vercel URL and sign in!

---

## ✅ Verification Checklist

- [ ] Backend health: `curl https://your-app.up.railway.app/api/health`
- [ ] Frontend loads: Visit Vercel URL
- [ ] Sign in works: Firebase authentication
- [ ] Dashboard loads: Data appears
- [ ] Nexus works: Can create posts, see feed

---

## 📚 Full Documentation

See `PHASE4_DEPLOYMENT_GUIDE.md` for detailed instructions, troubleshooting, and advanced configuration.

---

## 🆘 Need Help?

- **Railway Issues**: Check Railway logs in dashboard
- **Vercel Issues**: Check Vercel build logs
- **Database Issues**: Verify connection string in Supabase
- **CORS Errors**: Ensure Vercel URL is in Railway CORS_ORIGINS

---

**That's it! Your app is live! 🎉**

