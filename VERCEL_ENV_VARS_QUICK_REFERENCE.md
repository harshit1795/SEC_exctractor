# ⚡ Vercel Environment Variables - Quick Reference

## 📋 All Required Variables (8 Total)

### 1. Backend API URL
```
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api
```

### 2-8. Firebase (7 variables)
```
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789012
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789012:web:abcdef123456
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
```

---

## 🎯 Where to Get Values

### Backend URL
- **Render**: Render Dashboard → Your Service → Copy URL
- **Railway**: Railway Dashboard → Your Service → Copy URL

### Firebase Values
- **Firebase Console** → Project Settings → Your apps → Web app
- Copy all 7 values from Firebase config object

---

## ⚙️ How to Set in Vercel

1. **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. **Click "Add New"** for each variable
3. **Enter Key, Value, and select Environments**
4. **Click "Save"**
5. **Redeploy** (env vars require redeploy)

---

## ✅ Environment Selection

**For Preview Deployments (Option B):**
- `NEXT_PUBLIC_API_URL`: ✅ **Preview** only
- Firebase vars: ✅ **All** environments

**For Production Branch (Option A):**
- `NEXT_PUBLIC_API_URL`: ✅ **All** environments
- Firebase vars: ✅ **All** environments

---

## 📝 Complete Template

```bash
# Backend (Render)
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api

# Firebase
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSy...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789012
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789012:web:abcdef123456
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
```

---

**Full Guide**: See `VERCEL_ENVIRONMENT_VARIABLES_COMPLETE.md` for detailed instructions.

