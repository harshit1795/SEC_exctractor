# 🔥 Firebase Setup Guide

## The Error You're Seeing

```
Firebase: Error (auth/invalid-api-key)
```

This means Firebase configuration is missing or invalid.

---

## ✅ Quick Fix

### 1. **Get Firebase Config**

Go to [Firebase Console](https://console.firebase.google.com/):
1. Select your project (or create one)
2. Click the gear icon ⚙️ → **Project Settings**
3. Scroll to **Your apps** section
4. If you don't have a web app, click **Add app** → **Web** (</> icon)
5. Copy the config values

### 2. **Create `.env.local` File**

In `finq-frontend/` directory, create `.env.local`:

```bash
cd finq-frontend
touch .env.local
```

### 3. **Add Config Values**

Open `.env.local` and paste:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=your_actual_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**Replace all values with your actual Firebase config!**

### 4. **Restart Dev Server**

```bash
# Stop current server (Ctrl+C)
# Then restart:
npm run dev
```

---

## 📋 Example Config

Your Firebase config looks like this in the console:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "myproject.firebaseapp.com",
  projectId: "myproject",
  storageBucket: "myproject.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef123456",
  measurementId: "G-XXXXXXXXXX"
};
```

Convert to `.env.local` format:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=myproject.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=myproject
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=myproject.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789012
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789012:web:abcdef123456
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
```

---

## 🔐 Enable Authentication

In Firebase Console:
1. Go to **Authentication** → **Sign-in method**
2. Enable **Email/Password**
3. Click **Save**

---

## ✅ Verify Setup

After restarting, you should see:
- ✅ No Firebase errors in console
- ✅ Login page loads correctly
- ✅ Can sign up/sign in

---

## 🐛 Still Having Issues?

1. **Check file location**: `.env.local` must be in `finq-frontend/` directory
2. **Check variable names**: Must start with `NEXT_PUBLIC_`
3. **No quotes needed**: Don't wrap values in quotes
4. **Restart required**: Changes only take effect after restart
5. **Check console**: Look for any other error messages

---

**Once configured, the app will work!** 🚀


