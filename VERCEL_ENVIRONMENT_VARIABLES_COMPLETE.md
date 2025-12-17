# 🔐 Complete Vercel Environment Variables Guide

This guide lists **all environment variables** you need to set in Vercel for your FinQ frontend deployment.

---

## 📋 Required Environment Variables (8 Total)

### 1. Backend API URL ⚠️ **CRITICAL**

**Variable Name:**
```
NEXT_PUBLIC_API_URL
```

**Value (for Render deployment):**
```
https://your-render-service.onrender.com/api
```

**Value (for Railway deployment):**
```
https://your-railway-service.up.railway.app/api
```

**Where to get it:**
- **Render**: Render Dashboard → Your Service → Copy service URL
- **Railway**: Railway Dashboard → Your Service → Copy service URL

**Important:**
- ✅ Must include `/api` at the end
- ✅ Use `https://` (not `http://`)
- ✅ No trailing slash after `/api`

**Set for which environments:**
- **Option A (Change Branch)**: ✅ Production ✅ Preview ✅ Development
- **Option B (Preview Deployments)**: ✅ Preview only (for Render branch)

**Example:**
```
NEXT_PUBLIC_API_URL=https://finq-backend.onrender.com/api
```

---

### 2-8. Firebase Configuration (7 Variables) ⚠️ **REQUIRED**

All Firebase variables are **required** for authentication to work.

#### 2. Firebase API Key

**Variable Name:**
```
NEXT_PUBLIC_FIREBASE_API_KEY
```

**Value:**
```
AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Where to get it:**
- Firebase Console → Project Settings → Your apps → Web app → `apiKey`

**Set for:** ✅ Production ✅ Preview ✅ Development

---

#### 3. Firebase Auth Domain

**Variable Name:**
```
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
```

**Value:**
```
your-project.firebaseapp.com
```

**Where to get it:**
- Firebase Console → Project Settings → Your apps → Web app → `authDomain`

**Set for:** ✅ Production ✅ Preview ✅ Development

**Example:**
```
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=finq-test.firebaseapp.com
```

---

#### 4. Firebase Project ID

**Variable Name:**
```
NEXT_PUBLIC_FIREBASE_PROJECT_ID
```

**Value:**
```
your-project-id
```

**Where to get it:**
- Firebase Console → Project Settings → Your apps → Web app → `projectId`

**Set for:** ✅ Production ✅ Preview ✅ Development

**Example:**
```
NEXT_PUBLIC_FIREBASE_PROJECT_ID=finq-test
```

---

#### 5. Firebase Storage Bucket

**Variable Name:**
```
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
```

**Value:**
```
your-project.appspot.com
```

**Where to get it:**
- Firebase Console → Project Settings → Your apps → Web app → `storageBucket`

**Set for:** ✅ Production ✅ Preview ✅ Development

**Example:**
```
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=finq-test.appspot.com
```

---

#### 6. Firebase Messaging Sender ID

**Variable Name:**
```
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
```

**Value:**
```
123456789012
```

**Where to get it:**
- Firebase Console → Project Settings → Your apps → Web app → `messagingSenderId`

**Set for:** ✅ Production ✅ Preview ✅ Development

**Example:**
```
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789012
```

---

#### 7. Firebase App ID

**Variable Name:**
```
NEXT_PUBLIC_FIREBASE_APP_ID
```

**Value:**
```
1:123456789012:web:abcdef123456
```

**Where to get it:**
- Firebase Console → Project Settings → Your apps → Web app → `appId`

**Set for:** ✅ Production ✅ Preview ✅ Development

**Example:**
```
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789012:web:abcdef123456
```

---

#### 8. Firebase Measurement ID (Optional but Recommended)

**Variable Name:**
```
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID
```

**Value:**
```
G-XXXXXXXXXX
```

**Where to get it:**
- Firebase Console → Project Settings → Your apps → Web app → `measurementId`
- Only available if Google Analytics is enabled

**Set for:** ✅ Production ✅ Preview ✅ Development

**Note:** This is optional but recommended if you use Google Analytics.

**Example:**
```
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
```

---

## 📝 Complete Template

Copy this template and fill in your values:

```bash
# Backend API URL (Render)
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api

# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789012
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789012:web:abcdef123456
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
```

---

## 🎯 How to Set in Vercel

### Step-by-Step:

1. **Go to Vercel Dashboard** → Your Project
2. **Settings** → **Environment Variables**
3. **Click "Add New"** for each variable
4. **Enter:**
   - **Key**: Variable name (e.g., `NEXT_PUBLIC_API_URL`)
   - **Value**: Your actual value
   - **Environments**: Select which environments (Production, Preview, Development)
5. **Click "Save"**
6. **Repeat** for all 8 variables

### Environment Selection Guide:

**For Render Deployment (Option B - Preview Deployments):**
- `NEXT_PUBLIC_API_URL`: ✅ **Preview** only (uncheck Production, Development)
- All Firebase vars: ✅ **Production** ✅ **Preview** ✅ **Development**

**For Render Deployment (Option A - Change Branch):**
- `NEXT_PUBLIC_API_URL`: ✅ **Production** ✅ **Preview** ✅ **Development**
- All Firebase vars: ✅ **Production** ✅ **Preview** ✅ **Development**

---

## 🔍 How to Get Firebase Values

### Quick Steps:

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Select your project** (e.g., `finq-test`)
3. **Click gear icon** ⚙️ → **Project Settings**
4. **Scroll to "Your apps"** section
5. **Find your Web app** (</> icon)
   - If you don't have one: Click **"Add app"** → **Web** (</> icon) → Register app
6. **Copy the config values** from the Firebase config object

### Firebase Config Format:

You'll see something like this in Firebase Console:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "finq-test.firebaseapp.com",
  projectId: "finq-test",
  storageBucket: "finq-test.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef123456",
  measurementId: "G-XXXXXXXXXX"
};
```

**Convert to Vercel format:**
- `apiKey` → `NEXT_PUBLIC_FIREBASE_API_KEY`
- `authDomain` → `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- `projectId` → `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- `storageBucket` → `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
- `messagingSenderId` → `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
- `appId` → `NEXT_PUBLIC_FIREBASE_APP_ID`
- `measurementId` → `NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID`

---

## ✅ Verification Checklist

After setting all variables:

- [ ] **All 8 variables set** in Vercel
- [ ] **`NEXT_PUBLIC_API_URL`** points to correct backend (Render or Railway)
- [ ] **All Firebase variables** set correctly
- [ ] **Environment selection** correct (Production/Preview/Development)
- [ ] **Redeployed** Vercel (env vars require redeploy to take effect)
- [ ] **Tested** frontend loads without errors
- [ ] **Tested** authentication works (sign up/sign in)
- [ ] **Tested** API calls work (check Network tab)

---

## 🔧 Troubleshooting

### Issue: Firebase Authentication Not Working

**Symptoms:**
- `Firebase: Error (auth/invalid-api-key)`
- Login page shows setup error

**Solution:**
1. Verify all 7 Firebase variables are set
2. Check values match Firebase Console exactly
3. Ensure variables are set for correct environments
4. Redeploy Vercel after adding variables

### Issue: API Calls Fail

**Symptoms:**
- Network errors in browser console
- "Cannot connect to backend API"

**Solution:**
1. Verify `NEXT_PUBLIC_API_URL` is set correctly
2. Check URL includes `/api` at the end
3. Verify backend is running (test backend URL directly)
4. Check CORS settings in backend
5. Redeploy Vercel after updating variable

### Issue: Wrong Backend URL

**Symptoms:**
- Frontend calls wrong backend
- CORS errors

**Solution:**
1. Check `NEXT_PUBLIC_API_URL` value in Vercel
2. Verify environment selection (Production vs Preview)
3. Redeploy Vercel (env vars require redeploy)

---

## 📊 Quick Reference Table

| Variable | Required | Purpose | Where to Get |
|----------|----------|---------|--------------|
| `NEXT_PUBLIC_API_URL` | ✅ Yes | Backend API connection | Render/Railway Dashboard |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | ✅ Yes | Firebase authentication | Firebase Console |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | ✅ Yes | Firebase auth domain | Firebase Console |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | ✅ Yes | Firebase project ID | Firebase Console |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | ✅ Yes | Firebase storage | Firebase Console |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | ✅ Yes | Firebase messaging | Firebase Console |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | ✅ Yes | Firebase app ID | Firebase Console |
| `NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID` | ⚠️ Optional | Google Analytics | Firebase Console |

---

## 🚀 Quick Copy-Paste Template

**For Render Deployment:**

```bash
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id
```

**Replace all placeholders with your actual values!**

---

## 💡 Pro Tips

1. **Copy from Railway Deployment**: If you already have a Railway Vercel deployment, copy all Firebase variables from there (they're the same!)

2. **Use Preview Environment**: For branch-specific deployments, set `NEXT_PUBLIC_API_URL` for Preview environment only

3. **Redeploy After Changes**: Environment variables require a redeploy to take effect

4. **Test Locally First**: Set up `.env.local` with same values to test before deploying

5. **Keep Secrets Safe**: Never commit `.env.local` to Git - Vercel handles secrets securely

---

**Need Help?**
- Firebase Console: https://console.firebase.google.com/
- Vercel Docs: https://vercel.com/docs
- Render Dashboard: https://dashboard.render.com

