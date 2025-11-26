# 🔥 How to Get Firebase Web App Config

## ⚠️ Important: You Need TWO Different Configs

1. **Service Account JSON** (what you have) → For **backend/server-side** ✅ Already have this
2. **Web App Config** (what you need) → For **frontend/client-side** ❌ Need to get this

---

## 📋 Step-by-Step: Get Web App Config

### 1. Go to Firebase Console
👉 https://console.firebase.google.com/

### 2. Select Your Project
- Project: **finq-test** (based on your service account)

### 3. Get Web App Config
1. Click the **gear icon** ⚙️ (top left) → **Project Settings**
2. Scroll down to **"Your apps"** section
3. Look for a **Web app** (</> icon)
   - If you see one → Click on it → Copy the config
   - If you DON'T see one → Click **"Add app"** → Select **Web** (</> icon) → Register app → Copy the config

### 4. You'll See Something Like This:

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

### 5. Convert to `.env.local` Format

Copy each value into `.env.local` like this:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=finq-test.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=finq-test
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=finq-test.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789012
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789012:web:abcdef123456
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## ✅ Quick Copy Template

Once you have the values from Firebase Console, replace them here:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=<paste_apiKey_here>
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=<paste_authDomain_here>
NEXT_PUBLIC_FIREBASE_PROJECT_ID=finq-test
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=<paste_storageBucket_here>
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=<paste_messagingSenderId_here>
NEXT_PUBLIC_FIREBASE_APP_ID=<paste_appId_here>
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=<paste_measurementId_here>
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 🔐 Also Enable Email/Password Auth

1. In Firebase Console → **Authentication** → **Sign-in method**
2. Click **Email/Password**
3. Enable it → **Save**

---

## 🚀 After Creating `.env.local`

1. Save the file
2. Restart dev server: `npm run dev`
3. Open http://localhost:3000
4. Should see login page! ✅

