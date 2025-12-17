# 🔧 Fix 404 Error: Failed to Load Tickers

## 🐛 Issue

**Error**: `Failed to load tickers` with status code **404**

**Frontend is calling**: `/api/financial/tickers/available`  
**Expected backend endpoint**: `/api/financial/tickers/available`

---

## 🔍 Diagnosis

The 404 error means the endpoint is not found. This could be:

1. **API URL missing `/api` prefix** - Most likely!
2. **Backend route not registered** - Less likely
3. **Backend not running** - Check Render status

---

## ✅ Quick Fix: Verify API URL

### Check Your Vercel Environment Variable

1. **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. **Find `NEXT_PUBLIC_API_URL`**
3. **Verify it's exactly**:
   ```
   https://sec-exctractor.onrender.com/api
   ```
   - ✅ Must include `/api` at the end
   - ✅ No trailing slash after `/api`

### If Wrong, Fix It:

1. **Click Edit** on `NEXT_PUBLIC_API_URL`
2. **Set value to**:
   ```
   https://sec-exctractor.onrender.com/api
   ```
3. **Click Save**
4. **Redeploy Vercel**:
   - Deployments tab → Click "..." → Redeploy

---

## 🧪 Test Backend Endpoint Directly

### Test 1: Root Endpoint
Open in browser:
```
https://sec-exctractor.onrender.com/
```

**Expected**: `{"message":"FinQ Backend API","version":"0.1.0","docs":"/docs","health":"/api/health"}`

### Test 2: Health Endpoint
Open in browser:
```
https://sec-exctractor.onrender.com/api/health
```

**Expected**: `{"status":"healthy","service":"FinQ Backend API"}`

### Test 3: Tickers Endpoint (The One Failing)
Open in browser:
```
https://sec-exctractor.onrender.com/api/financial/tickers/available
```

**Expected**: `{"tickers":["AAPL","MSFT",...],"count":N}`

**If this returns 404**, the backend endpoint might not be registered.  
**If this works**, the issue is in the frontend API URL configuration.

---

## 🔍 Debug Steps

### Step 1: Check Browser Network Tab

1. **Open your Vercel deployment**
2. **Open DevTools** (F12) → **Network** tab
3. **Try to load the dashboard** (triggers ticker request)
4. **Find the failed request**:
   - Look for request to `/financial/tickers/available`
   - Check the **full URL** it's trying to call
   - Should be: `https://sec-exctractor.onrender.com/api/financial/tickers/available`

**If URL is wrong** (e.g., missing `/api` or wrong domain):
- Fix `NEXT_PUBLIC_API_URL` in Vercel
- Redeploy

**If URL is correct but still 404**:
- Check backend logs in Render
- Verify endpoint exists in backend code

---

### Step 2: Check Browser Console

1. **Open DevTools** (F12) → **Console** tab
2. **Look for errors**:
   - Network errors
   - 404 errors
   - CORS errors

3. **Check environment variable**:
   ```javascript
   console.log(process.env.NEXT_PUBLIC_API_URL)
   ```
   **Expected**: `https://sec-exctractor.onrender.com/api`

---

### Step 3: Check Render Backend Logs

1. **Render Dashboard** → Your Service → **Logs** tab
2. **Look for**:
   - 404 errors
   - Route registration errors
   - Startup errors

---

## 🎯 Most Likely Causes

### Cause 1: API URL Missing `/api` (90% likely)

**Symptom**: Frontend calls `https://sec-exctractor.onrender.com/financial/tickers/available`  
**Fix**: Set `NEXT_PUBLIC_API_URL` = `https://sec-exctractor.onrender.com/api`

### Cause 2: API URL Has Trailing Slash (5% likely)

**Symptom**: Frontend calls `https://sec-exctractor.onrender.com/api//financial/tickers/available`  
**Fix**: Remove trailing slash: `https://sec-exctractor.onrender.com/api` (no `/` at end)

### Cause 3: Backend Endpoint Not Registered (5% likely)

**Symptom**: Backend logs show route not found  
**Fix**: Check backend code has the route registered

---

## ✅ Complete Fix Checklist

- [ ] **Test backend endpoint directly**: `https://sec-exctractor.onrender.com/api/financial/tickers/available`
- [ ] **Verify `NEXT_PUBLIC_API_URL`** in Vercel = `https://sec-exctractor.onrender.com/api`
- [ ] **No trailing slash** after `/api`
- [ ] **Redeploy Vercel** after fixing env var
- [ ] **Check browser Network tab** - verify correct URL is called
- [ ] **Check browser Console** - look for errors
- [ ] **Test again** - should work now!

---

## 📝 Correct Configuration

### Vercel Environment Variable:
```
NEXT_PUBLIC_API_URL=https://sec-exctractor.onrender.com/api
```

### Expected API Call:
```
https://sec-exctractor.onrender.com/api/financial/tickers/available
```

### Expected Response:
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", ...],
  "count": 100
}
```

---

## 🚨 Quick Test

Run this in browser console (on your Vercel deployment):
```javascript
fetch('https://sec-exctractor.onrender.com/api/financial/tickers/available')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

**If this works**: Backend is fine, issue is frontend config  
**If this fails**: Backend issue, check Render logs

---

**Most likely fix**: Update `NEXT_PUBLIC_API_URL` in Vercel to include `/api` at the end! 🚀

