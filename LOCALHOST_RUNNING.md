# ✅ App Running on Localhost

## 🎉 Status: Both Services Running!

### Backend API
- **URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health
- **API Docs**: http://localhost:8000/docs
- **Status**: ✅ Running

### Frontend
- **URL**: http://localhost:3000
- **Status**: ✅ Running

---

## 🧪 Quick Tests

### Test Backend Health
```bash
curl http://localhost:8000/api/health
```

**Expected**: `{"status":"healthy","service":"FinQ Backend API"}`

### Test Tickers Endpoint
```bash
curl http://localhost:8000/api/financial/tickers/available
```

**Expected**: `{"tickers":[...],"count":500}`

### Test Frontend
1. **Open browser**: http://localhost:3000
2. **Open DevTools** (F12) → **Console**
3. **Check API URL**:
   ```javascript
   console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)
   ```
   **Expected**: `http://localhost:8000/api`

4. **Test API call**:
   ```javascript
   fetch('http://localhost:8000/api/financial/tickers/available')
     .then(r => r.json())
     .then(data => console.log('✅ Tickers:', data.count))
   ```

---

## 🛑 How to Stop Services

### Stop Backend
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Stop Frontend
```bash
# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Stop Both
```bash
lsof -ti:8000,3000 | xargs kill -9
```

---

## 📝 Environment Variables

### Backend (finq-backend/.env)
- `DATABASE_URL` - Database connection string
- `GEMINI_API_KEY` - Google Gemini API key
- `FRED_API_KEY` - FRED API key (optional)
- `CORS_ORIGINS` - Allowed CORS origins (default includes localhost:3000)

### Frontend (finq-frontend/.env.local)
- `NEXT_PUBLIC_API_URL` - Backend API URL (should be `http://localhost:8000/api`)
- `NEXT_PUBLIC_FIREBASE_*` - Firebase configuration variables

---

## 🔍 Troubleshooting

### Backend Not Starting
1. **Check if port 8000 is in use**:
   ```bash
   lsof -i:8000
   ```
2. **Check backend logs** for errors
3. **Verify virtual environment is activated**:
   ```bash
   cd finq-backend
   source venv/bin/activate
   which python  # Should show venv path
   ```

### Frontend Not Starting
1. **Check if port 3000 is in use**:
   ```bash
   lsof -i:3000
   ```
2. **Check if node_modules exists**:
   ```bash
   cd finq-frontend
   ls node_modules
   ```
   If missing, run: `npm install`

### Frontend Can't Connect to Backend
1. **Verify backend is running**: http://localhost:8000/api/health
2. **Check `.env.local`** has correct `NEXT_PUBLIC_API_URL`
3. **Restart frontend** after changing env vars
4. **Check browser console** for CORS errors

### CORS Errors
If you see CORS errors in browser console:
1. **Check backend `.env`** has `CORS_ORIGINS` including `http://localhost:3000`
2. **Restart backend** after changing env vars

---

## 🚀 Next Steps

1. **Open the app**: http://localhost:3000
2. **Test login/signup** with Firebase
3. **Test dashboard** features
4. **Test API calls** from frontend
5. **Check browser console** for any errors

---

## 📊 Service Status Check

Run this to check both services:
```bash
# Check backend
curl -s http://localhost:8000/api/health && echo " ✅ Backend OK" || echo " ❌ Backend DOWN"

# Check frontend
curl -s http://localhost:3000 > /dev/null && echo " ✅ Frontend OK" || echo " ❌ Frontend DOWN"
```

---

**Both services are running! Open http://localhost:3000 in your browser to test the app.** 🎉

