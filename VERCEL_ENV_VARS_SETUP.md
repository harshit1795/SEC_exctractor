# 🔥 Set Up Firebase Environment Variables in Vercel

## Problem
Vercel deployment shows: "Firebase configuration is missing"

This means the Firebase environment variables aren't set in Vercel.

---

## ✅ Solution: Add Environment Variables in Vercel

### Step 1: Get Firebase Config from Firebase Console

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (or create one if needed)
3. Click ⚙️ **Settings** → **Project Settings**
4. Scroll down to **"Your apps"** section
5. Click on your **Web app** (</> icon) or create one:
   - Click **"Add app"** → Select **Web** (</> icon)
   - Register app → Copy the config

### Step 2: Copy Firebase Config Values

You'll see something like:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef123456",
  measurementId: "G-XXXXXXXXXX"
};
```

### Step 3: Add Environment Variables in Vercel

1. Go to your Vercel project
2. Click **Settings** tab
3. Click **Environment Variables** (left sidebar)
4. Add each variable one by one:

#### Add These Variables:

Click **"Add New"** for each:

1. **Key**: `NEXT_PUBLIC_FIREBASE_API_KEY`
   **Value**: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` (from apiKey)

2. **Key**: `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
   **Value**: `your-project.firebaseapp.com` (from authDomain)

3. **Key**: `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
   **Value**: `your-project-id` (from projectId)

4. **Key**: `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
   **Value**: `your-project.appspot.com` (from storageBucket)

5. **Key**: `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
   **Value**: `123456789012` (from messagingSenderId)

6. **Key**: `NEXT_PUBLIC_FIREBASE_APP_ID`
   **Value**: `1:123456789012:web:abcdef123456` (from appId)

7. **Key**: `NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID`
   **Value**: `G-XXXXXXXXXX` (from measurementId - optional)

8. **Key**: `NEXT_PUBLIC_API_URL`
   **Value**: `https://secexctractor-production.up.railway.app/api` (your Railway backend URL)

### Step 4: Set Environment for Each Variable

For each variable, make sure:
- ✅ **Production** is checked
- ✅ **Preview** is checked (optional, for preview deployments)
- ✅ **Development** is checked (optional)

### Step 5: Redeploy

After adding all variables:
1. Go to **Deployments** tab
2. Click **"Redeploy"** on the latest deployment
3. Or Vercel will auto-redeploy when you save variables

---

## 📋 Quick Checklist

- [ ] Got Firebase config from Firebase Console
- [ ] Added `NEXT_PUBLIC_FIREBASE_API_KEY`
- [ ] Added `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- [ ] Added `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- [ ] Added `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
- [ ] Added `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
- [ ] Added `NEXT_PUBLIC_FIREBASE_APP_ID`
- [ ] Added `NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID` (optional)
- [ ] Added `NEXT_PUBLIC_API_URL` (Railway backend URL)
- [ ] Redeployed

---

## 🔍 Where to Find Firebase Config

**Firebase Console** → **Project Settings** → **Your apps** → **Web app**

If you don't have a Web app:
1. Click **"Add app"**
2. Select **Web** (</> icon)
3. Register the app
4. Copy the config values

---

## ⚠️ Important Notes

- All Firebase variables must start with `NEXT_PUBLIC_` (Next.js requirement)
- `NEXT_PUBLIC_API_URL` should point to your Railway backend
- After adding variables, Vercel will automatically redeploy
- Make sure all variables are set for **Production** environment

---

**Add all the environment variables in Vercel Settings → Environment Variables, then redeploy!** 🚀

