# ✅ Render Setup Quick Checklist

Use this checklist to quickly set up Render and fix FinQ Chat.

---

## 🚀 Setup Steps (15 minutes)

### 1. Create Render Account
- [ ] Go to https://render.com
- [ ] Sign up with GitHub
- [ ] Authorize repository access

### 2. Create Web Service
- [ ] Click "New +" → "Web Service"
- [ ] Select repository: `SEC_exctractor`
- [ ] Select branch: `feature/nexus5.1_c_Rail_alt`
- [ ] Verify auto-detected settings:
  - [ ] Root Directory: `finq-backend`
  - [ ] Build Command: `pip install -r requirements.txt`
  - [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Set Environment Variables (CRITICAL!)
- [ ] `DATABASE_URL` = `postgresql://postgres:[PASSWORD]@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require`
  - Replace `[PASSWORD]` with actual password (no brackets!)
- [ ] `GEMINI_API_KEY` = Your Gemini API key
- [ ] `CORS_ORIGINS` = Your Vercel URLs (comma-separated)
- [ ] `FRED_API_KEY` = Your FRED API key (optional)

### 4. Deploy
- [ ] Click "Create Web Service"
- [ ] Wait 3-5 minutes for build
- [ ] Check logs for success

### 5. Test Backend
- [ ] Health check: `https://your-service.onrender.com/api/health`
- [ ] API docs: `https://your-service.onrender.com/docs`
- [ ] Check logs for database connection success

### 6. Update Frontend
- [ ] Vercel Dashboard → Settings → Environment Variables
- [ ] Update `NEXT_PUBLIC_API_URL` = `https://your-service.onrender.com/api`
- [ ] Redeploy frontend

### 7. Test FinQ Chat
- [ ] Open Vercel frontend
- [ ] Navigate to Chatbot tab
- [ ] Ask a question
- [ ] Verify no database errors!

---

## 🔍 Quick Verification

**Backend URL**: `https://[service-name].onrender.com`

**Test Commands**:
```bash
# Health check
curl https://your-service.onrender.com/api/health

# Should return: {"status":"healthy","service":"FinQ Backend API"}
```

---

## ⚠️ Common Issues

**Database Connection Fails?**
- ✅ Check Supabase Network Restrictions = "Allow all IPs"
- ✅ Verify password has no brackets `[]`
- ✅ Try connection pooler (port 6543)

**CORS Errors?**
- ✅ Add Vercel URL to `CORS_ORIGINS`
- ✅ Redeploy after updating env vars

**Service Sleeps?**
- ✅ Free tier sleeps after 15 min
- ✅ First request takes 30-60 seconds
- ✅ Upgrade to Starter ($7/mo) for always-on

---

## 📝 Notes

- **Render URL**: `https://[service-name].onrender.com`
- **Free tier**: 750 hours/month
- **Sleep**: 15 minutes inactivity (free tier)
- **Always-on**: $7/month (Starter plan)

---

**Full Guide**: See `RENDER_SETUP_FINQ_CHAT_FIX.md` for detailed instructions.

