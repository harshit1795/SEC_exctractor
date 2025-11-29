# 🔍 Railway Environment Variables Checklist

## How to Check Variables in Railway

1. Go to **Railway Dashboard** → Your Service
2. Click on **Variables** tab
3. Review all variables listed below

---

## ✅ Required Variables (Critical)

### 1. `DATABASE_URL` ⚠️ **MOST CRITICAL**
- **Status**: Must be set or app will crash on startup
- **Format**: `postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
- **Example**: `postgresql://postgres:mypassword123@db.abcdefghijklmnop.supabase.co:5432/postgres`
- **Notes**: 
  - No quotes needed in Railway dashboard
  - Must be a valid PostgreSQL connection string
  - If missing, you'll see `OperationalError` or `Connection refused` in logs

**How to verify it's correct:**
- Check Railway logs for database connection errors
- Test connection: The app should connect on startup without errors

---

## 🔧 Recommended Variables (For Full Functionality)

### 2. `CORS_ORIGINS`
- **Status**: Should be set to allow frontend access
- **Format**: Comma-separated list of URLs (no spaces after commas)
- **Example**: `http://localhost:3000,https://your-app.vercel.app`
- **Default**: `http://localhost:8501,http://localhost:3000,http://localhost:8080`
- **Notes**: 
  - Must include your Vercel frontend domain
  - Can use `*` for testing (not recommended for production)
  - If missing, frontend will get CORS errors

**Current Vercel domain to add:**
- Check your Vercel deployment URL and add it here

### 3. `GEMINI_API_KEY`
- **Status**: Required for chat/AI features
- **Format**: Your Google Generative AI API key
- **Example**: `AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567`
- **Notes**: 
  - If missing, chat endpoints will return errors
  - Get from: [Google AI Studio](https://makersuite.google.com/app/apikey)

### 4. `FRED_API_KEY`
- **Status**: Required for FRED economic data
- **Format**: Your FRED API key
- **Example**: `abcdef1234567890abcdef1234567890`
- **Notes**: 
  - If missing, FRED data endpoints will return errors
  - Get from: [FRED API](https://fred.stlouisfed.org/docs/api/api_key.html)

---

## 🔐 Optional Variables (Firebase)

### 5. `FIREBASE_CREDENTIALS_JSON`
- **Status**: Optional (only if backend needs Firebase Admin)
- **Format**: Full JSON string of Firebase service account credentials
- **Example**: `{"type":"service_account","project_id":"...","private_key":"..."}`
- **Notes**: 
  - Must be valid JSON (can be minified)
  - Used for Firebase Admin SDK operations
  - Alternative: Use `FIREBASE_CREDENTIALS_B64` (base64 encoded)

### 6. `FIREBASE_CREDENTIALS_B64`
- **Status**: Optional (alternative to FIREBASE_CREDENTIALS_JSON)
- **Format**: Base64-encoded Firebase credentials JSON
- **Notes**: 
  - Use this if you prefer base64 encoding
  - Only set one: either `FIREBASE_CREDENTIALS_JSON` or `FIREBASE_CREDENTIALS_B64`

---

## ⚙️ Optional Configuration Variables

### 7. `ENVIRONMENT`
- **Status**: Optional
- **Default**: `development`
- **Recommended for production**: `production`
- **Example**: `production`

### 8. `DEBUG`
- **Status**: Optional
- **Default**: `false`
- **Recommended for production**: `false`
- **Example**: `false`

### 9. `API_PREFIX`
- **Status**: Optional
- **Default**: `/api`
- **Example**: `/api`
- **Notes**: Usually don't need to change this

---

## 🚨 Common Issues

### Issue 1: Missing DATABASE_URL
**Symptoms:**
- App crashes immediately on startup
- Logs show: `OperationalError`, `Connection refused`, or `database_url is required`

**Fix:**
1. Go to Railway → Variables tab
2. Add `DATABASE_URL` with your PostgreSQL connection string
3. Redeploy

### Issue 2: Wrong CORS_ORIGINS
**Symptoms:**
- Frontend can't connect to backend
- Browser console shows: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Fix:**
1. Get your Vercel deployment URL
2. Add it to `CORS_ORIGINS` in Railway Variables
3. Format: `https://your-app.vercel.app` (comma-separated if multiple)
4. Redeploy

### Issue 3: Invalid DATABASE_URL Format
**Symptoms:**
- App crashes on startup
- Logs show: `invalid connection string` or `could not parse`

**Fix:**
- Verify format: `postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
- No quotes in Railway dashboard
- Replace `[PASSWORD]` and `[PROJECT-REF]` with actual values

---

## 📋 Quick Checklist

Before deploying, verify:

- [ ] `DATABASE_URL` is set and valid
- [ ] `CORS_ORIGINS` includes your Vercel domain
- [ ] `GEMINI_API_KEY` is set (if using chat features)
- [ ] `FRED_API_KEY` is set (if using FRED data)
- [ ] `ENVIRONMENT=production` (recommended)
- [ ] `DEBUG=false` (recommended for production)

---

## 🔍 How to Verify Variables Are Working

### Test 1: Check Health Endpoint
```bash
curl https://secexctractor-production.up.railway.app/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "FinQ Backend API",
  "database_configured": true
}
```

### Test 2: Check Railway Logs
1. Railway → Service → Deployments → Latest
2. Look for:
   - ✅ `Application startup complete`
   - ✅ `Uvicorn running on http://0.0.0.0:PORT`
   - ❌ Any errors about missing variables or connection failures

### Test 3: Check Database Connection
If logs show database connection errors, verify:
- `DATABASE_URL` format is correct
- Database is accessible from Railway
- Password is correct
- Network/firewall allows Railway IPs

---

## 📝 Example Railway Variables Setup

```bash
# Required
DATABASE_URL=postgresql://postgres:yourpassword@db.abcdefghijklmnop.supabase.co:5432/postgres

# Recommended
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
GEMINI_API_KEY=AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567
FRED_API_KEY=abcdef1234567890abcdef1234567890

# Optional
ENVIRONMENT=production
DEBUG=false
```

**Important:** In Railway dashboard, enter these values **without quotes** around them.

---

## 🆘 Still Having Issues?

1. **Check Railway Logs** - Most errors will show in deployment logs
2. **Verify Variable Names** - Must match exactly (case-sensitive)
3. **Check for Typos** - Especially in `DATABASE_URL`
4. **Test Locally** - Set same variables in `.env` and test locally first
5. **Redeploy** - After changing variables, trigger a new deployment

---

**Last Updated:** Based on `finq-backend/app/config.py` configuration

