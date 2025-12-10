# ✅ Render Deployment Checklist

Use this checklist to ensure a smooth migration from Railway to Render.

## Pre-Deployment

- [ ] **Repository Ready**
  - [ ] Code is on branch `feature/nexus5.1_c_Rail_alt`
  - [ ] `render.yaml` exists in repo root
  - [ ] `finq-backend/requirements.txt` is up to date
  - [ ] All code changes committed and pushed

- [ ] **Environment Variables Documented**
  - [ ] `DATABASE_URL` (Supabase connection string)
  - [ ] `GEMINI_API_KEY` (Google Gemini API key)
  - [ ] `CORS_ORIGINS` (All Vercel deployment URLs)
  - [ ] Any other custom variables

## Render Setup

- [ ] **Account Created**
  - [ ] Signed up at render.com
  - [ ] Connected GitHub account

- [ ] **Service Created**
  - [ ] Created new Web Service
  - [ ] Connected to correct repository
  - [ ] Selected branch: `feature/nexus5.1_c_Rail_alt`
  - [ ] Root directory: `finq-backend`

- [ ] **Configuration**
  - [ ] Build command: `pip install -r requirements.txt`
  - [ ] Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - [ ] Region selected (Oregon recommended)
  - [ ] Plan selected (Free tier to start)

## Environment Variables

- [ ] **Database**
  - [ ] `DATABASE_URL` set with Supabase connection
  - [ ] Connection string includes `?connect_timeout=10&sslmode=require`
  - [ ] Password is URL-encoded if needed

- [ ] **API Keys**
  - [ ] `GEMINI_API_KEY` set
  - [ ] Key is valid and active

- [ ] **CORS**
  - [ ] `CORS_ORIGINS` includes all Vercel URLs
  - [ ] Format: `url1,url2,url3` (comma-separated, no spaces)
  - [ ] Includes production and preview URLs

- [ ] **App Config**
  - [ ] `APP_NAME` set (optional)
  - [ ] `API_PREFIX` set to `/api` (optional)
  - [ ] `DEBUG` set to `false` (optional)

## Deployment

- [ ] **Initial Deploy**
  - [ ] Service deployed successfully
  - [ ] Build logs show no errors
  - [ ] Service is running (green status)

- [ ] **Health Check**
  - [ ] `GET /api/health` returns `{"status": "healthy"}`
  - [ ] Service URL is accessible
  - [ ] No 502/503 errors

## Testing

- [ ] **API Endpoints**
  - [ ] `/api/health` - Health check works
  - [ ] `/api/financial/tickers/available` - Returns ticker list
  - [ ] `/api/financial/fundamentals/AAPL` - Returns data
  - [ ] `/docs` - Swagger UI loads

- [ ] **Database Connection**
  - [ ] No connection errors in logs
  - [ ] Database queries work
  - [ ] User authentication works (if applicable)

- [ ] **FinQ Chat**
  - [ ] Chat endpoint responds
  - [ ] AI analysis generates responses
  - [ ] No rate limit errors (initially)

## Frontend Integration

- [ ] **Vercel Updated**
  - [ ] `NEXT_PUBLIC_API_URL` updated to Render URL
  - [ ] All Vercel deployments updated
  - [ ] Frontend redeployed

- [ ] **CORS Working**
  - [ ] Frontend can call backend API
  - [ ] No CORS errors in browser console
  - [ ] Data loads correctly

- [ ] **End-to-End Test**
  - [ ] Dashboard loads
  - [ ] Ticker data displays
  - [ ] FinQ Chat works
  - [ ] Nexus features work

## Post-Deployment

- [ ] **Monitoring**
  - [ ] Logs are accessible in Render Dashboard
  - [ ] No critical errors in logs
  - [ ] Service stays running

- [ ] **Documentation**
  - [ ] Updated any docs with new URL
  - [ ] Team notified of new deployment URL
  - [ ] Old Railway deployment can be decommissioned

- [ ] **Optional: Upgrade**
  - [ ] Consider upgrading to Starter plan ($7/mo) for always-on
  - [ ] Set up monitoring/alerting if needed

## Troubleshooting

If something doesn't work:

1. **Check Logs**: Render Dashboard → Your Service → Logs
2. **Verify Environment Variables**: Settings → Environment
3. **Test Health Endpoint**: `curl https://your-service.onrender.com/api/health`
4. **Check Database**: Verify Supabase connection string
5. **Check CORS**: Ensure all frontend URLs are in `CORS_ORIGINS`

## Rollback Plan

If Render deployment fails:

1. Keep Railway deployment running until Render is stable
2. Switch `NEXT_PUBLIC_API_URL` back to Railway if needed
3. Debug Render issues without affecting production

---

**Deployment Date**: _______________
**Render Service URL**: _______________
**Deployed By**: _______________

