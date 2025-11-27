# 🌐 How to Generate Public URL in Railway

## Problem: Only Seeing "Private Networking"

If you only see **"Private Networking"** in Railway Settings → Networking, you need to **generate a public domain**.

---

## ✅ Solution: Enable Public Networking

### Step-by-Step:

1. **Go to Railway Dashboard**
   - Log in at [railway.app](https://railway.app)
   - Click on your **project**

2. **Select Your Service**
   - Click on the **service** (your deployed backend app)

3. **Open Settings**
   - Click on **Settings** tab (top navigation)

4. **Find Networking Section**
   - Scroll down to **"Networking"** section

5. **Generate Public Domain**
   - Look for one of these options:
     - **"Generate Domain"** button
     - **"Enable Public Networking"** toggle
     - **"Public Networking"** section with a **"+"** or **"Generate"** button
   - Click it!

6. **Copy Your URL**
   - Railway will generate a URL like:
     ```
     https://your-service-name-production.up.railway.app
     ```
   - **Copy this URL** - this is your backend API URL!

---

## 📍 Where to Find It

The public URL will appear in:
- **Settings → Networking → Public Networking** section
- Usually shows as: `https://[random-name].up.railway.app`

---

## 🧪 Test Your URL

Once you have the URL, test it:

```bash
# Replace with your actual Railway URL
curl https://YOUR-URL.up.railway.app/api/health
```

**Expected Response**:
```json
{"status":"healthy","service":"FinQ Backend API"}
```

---

## 🐛 If "Generate Domain" Button is Missing

### Option 1: Check Service Type
- Make sure your service is a **web service** (not a database or other service type)
- Railway only generates public URLs for web services

### Option 2: Check Railway Plan
- Free tier should support public URLs
- If button is missing, try refreshing the page

### Option 3: Check Deployment Status
- Make sure your deployment is **successful** and **running**
- Railway may not show the option if the service isn't running

### Option 4: Use Railway CLI
```bash
# Install Railway CLI (if not installed)
npm i -g @railway/cli

# Login
railway login

# Generate domain
railway domain
```

---

## ✅ After Generating Domain

1. **Copy the URL** - You'll need it for:
   - Testing with `curl`
   - Setting `NEXT_PUBLIC_API_URL` in Vercel
   - Adding to `CORS_ORIGINS` in Railway variables

2. **Update CORS_ORIGINS** (if needed):
   - Go to Railway → Your Service → **Variables**
   - Add/update `CORS_ORIGINS`:
     ```
     https://your-app.up.railway.app,http://localhost:3000
     ```

3. **Test the endpoint**:
   ```bash
   curl https://your-app.up.railway.app/api/health
   ```

---

**Once you generate the domain and test it, you're ready to deploy the frontend!** 🚀

