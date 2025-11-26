# 🧪 Testing Guide - Phase 3 Frontend

## 🚀 Quick Start

### 1. **Set Up Environment Variables**

Create `.env.local` file in `finq-frontend/`:

```bash
# Firebase Configuration (get from your Firebase project settings)
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain_here
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id_here
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_storage_bucket_here
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id_here
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id_here
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id_here

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 2. **Start Backend** (if not running)

```bash
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Backend should be running on: http://localhost:8000

### 3. **Start Frontend**

```bash
cd finq-frontend
npm run dev
```

Frontend will be running on: http://localhost:3000

---

## ✅ What to Test

### **Authentication**
1. ✅ Go to http://localhost:3000
2. ✅ See login page
3. ✅ Sign up with new email/password
4. ✅ Sign in with existing credentials
5. ✅ Should redirect to `/dashboard` after login

### **Navigation**
1. ✅ After login, see sidebar with 4 pages
2. ✅ Click "Dashboard" - should show dashboard page
3. ✅ Click "Financial Health Monitoring" - should show health page
4. ✅ Click "Nexus" - should show nexus page
5. ✅ Click "Settings" - should show settings page
6. ✅ Active page should be highlighted in sidebar

### **Logout**
1. ✅ Click "Log Out" button in sidebar
2. ✅ Should redirect to login page
3. ✅ Should not be able to access protected pages

### **Protected Routes**
1. ✅ Try accessing http://localhost:3000/dashboard directly (not logged in)
2. ✅ Should redirect to login page

---

## 🐛 Troubleshooting

### **Firebase Errors**
- Make sure `.env.local` has all Firebase config values
- Check Firebase project settings match
- Ensure Firebase Authentication is enabled in Firebase Console

### **API Connection Errors**
- Make sure backend is running on http://localhost:8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Check CORS settings in backend

### **Logo Not Showing**
- Make sure `FInQLogo.png` is in `finq-frontend/public/`
- If missing, copy from project root: `cp FInQLogo.png finq-frontend/public/`

### **Build Errors**
- Run `npm install` to ensure all dependencies are installed
- Check Node.js version (should be 18+)

---

## 📝 Current Status

### ✅ **Working**
- Authentication (login/signup/logout)
- Routing structure
- Sidebar navigation
- Protected routes
- Basic page layouts

### 🚧 **In Progress**
- Dashboard tabs and features
- Nexus community features
- Financial Health Monitoring
- Settings page

---

## 🎯 Next Steps

After confirming basic functionality works:
1. Start migrating Dashboard tabs
2. Add ticker selector
3. Implement charts
4. Connect to backend API

---

**Ready to test!** 🚀

