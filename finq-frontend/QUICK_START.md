# 🚀 Quick Start - Test the App

## ⚡ 3-Step Setup

### 1. **Create Environment File**

Create `finq-frontend/.env.local`:

```bash
# Copy from your Firebase project settings
NEXT_PUBLIC_FIREBASE_API_KEY=your_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_domain_here
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id_here
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_bucket_here
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id_here
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id_here
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id_here

# API URL (backend)
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 2. **Start Backend** (Terminal 1)

```bash
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload
```

✅ Backend: http://localhost:8000

### 3. **Start Frontend** (Terminal 2)

```bash
cd finq-frontend
npm run dev
```

✅ Frontend: http://localhost:3000

---

## 🧪 Test Checklist

1. ✅ Open http://localhost:3000
2. ✅ See login page
3. ✅ Sign up with email/password
4. ✅ Redirected to Dashboard
5. ✅ Sidebar navigation works
6. ✅ All 4 pages accessible
7. ✅ Logout works

---

## 📝 Notes

- **Firebase Config**: Get from Firebase Console → Project Settings → Your apps
- **Backend**: Must be running for API calls (optional for basic auth test)
- **Logo**: If missing, copy `FInQLogo.png` to `finq-frontend/public/`

---

**Ready to test!** 🎉

