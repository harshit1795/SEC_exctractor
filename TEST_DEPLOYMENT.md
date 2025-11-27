# 🧪 Testing Your Railway Deployment

## Step 1: Generate Public Domain (If Not Visible)

**If you only see "Private Networking" in Settings → Networking**, you need to generate a public domain:

1. Go to [railway.app](https://railway.app) and log in
2. Click on your **project**
3. Click on your **service** (the deployed app)
4. Go to **Settings** tab
5. Scroll to **"Networking"** section
6. Look for **"Public Networking"** or **"Generate Domain"** button
7. Click **"Generate Domain"** or **"Enable Public Networking"**
8. Railway will create a public URL like:
   ```
   https://your-service-name-production.up.railway.app
   ```
9. Copy this URL - this is your backend API URL!

---

## Step 1 (Alternative): Find Your Railway App URL

### Method 1: Railway Dashboard

1. Go to [railway.app](https://railway.app) and log in
2. Click on your **project**
3. Click on your **service** (the deployed app)
4. Go to **Settings** tab
5. Scroll to **"Networking"** section
6. Under **"Public Networking"**, you should see your Railway URL:
   ```
   https://your-app-name-production.up.railway.app
   ```
   or
   ```
   https://your-app-name.railway.app
   ```

### Method 2: Railway Dashboard - Deployments Tab

1. Go to your **service** in Railway
2. Click on **Deployments** tab
3. Click on the latest (successful) deployment
4. Look at the logs - Railway often shows the URL there
5. Or check the **"Settings"** → **"Networking"** section

### Method 3: Railway CLI (if installed)

```bash
railway status
```

---

## Step 2: Test Health Endpoint

Once you have your Railway URL, test it:

```bash
# Replace YOUR-APP-NAME with your actual Railway app name
curl https://YOUR-APP-NAME.up.railway.app/api/health
```

**Expected Response**:
```json
{"status":"healthy","service":"FinQ Backend API"}
```

---

## Step 3: Test Other Endpoints

### Test API Root
```bash
curl https://YOUR-APP-NAME.up.railway.app/api/
```

### Test Financial Data Endpoint
```bash
curl https://YOUR-APP-NAME.up.railway.app/api/financial/tickers
```

### Test Chat Endpoint (if configured)
```bash
curl https://YOUR-APP-NAME.up.railway.app/api/chat/health
```

---

## Step 4: Check Deployment Logs

1. Go to Railway → Your Project → **Deployments**
2. Click on the latest deployment
3. Check the logs for:
   - ✅ `Application startup complete`
   - ✅ `Uvicorn running on http://0.0.0.0:PORT`
   - ❌ Any error messages

---

## Step 5: Verify Environment Variables

1. Go to Railway → Your Service → **Variables** tab
2. Verify these are set:
   - ✅ `DATABASE_URL`
   - ✅ `GEMINI_API_KEY` (if using chat)
   - ✅ `FRED_API_KEY` (if using FRED data)
   - ✅ `CORS_ORIGINS` (should include your frontend URL)

---

## Step 6: Test Database Connection

If health endpoint works but you get database errors:

```bash
# Test database connection (if you have psql installed)
psql $DATABASE_URL -c "SELECT version();"
```

Or check Railway logs for database connection errors.

---

## 🐛 Troubleshooting

### "Connection refused" or "Cannot connect"
- Check Railway deployment is actually running (not sleeping)
- Verify the URL is correct
- Check Railway dashboard shows "Active" status

### "404 Not Found"
- Verify the endpoint path: `/api/health` (not `/health`)
- Check Railway logs for routing errors

### "500 Internal Server Error"
- Check Railway logs for detailed error messages
- Verify environment variables are set correctly
- Check database connection

### "CORS error" (when testing from browser)
- Add your test URL to `CORS_ORIGINS` in Railway variables
- Format: `https://your-app.up.railway.app,http://localhost:3000`

---

## ✅ Success Checklist

- [ ] Found Railway app URL
- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] No errors in Railway logs
- [ ] Environment variables are set
- [ ] Database connection working (if applicable)
- [ ] Ready to connect frontend!

---

**Once health endpoint works, you can proceed to deploy the frontend to Vercel!** 🚀

