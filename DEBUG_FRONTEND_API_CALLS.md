# 🔍 Debug Frontend API Calls - Backend Works, Frontend 404

## ✅ Backend Confirmed Working

The backend endpoint works when accessed directly:
```
https://sec-exctractor.onrender.com/api/financial/tickers/available
```

Returns: `{"tickers":[...],"count":500}` ✅

**This means the issue is in the frontend configuration!**

---

## 🔍 Step 1: Check What URL Frontend is Calling

### In Browser DevTools:

1. **Open your Vercel deployment** in browser
2. **Open DevTools** (F12)
3. **Go to Network tab**
4. **Clear network log** (trash icon)
5. **Try to load the dashboard** (or refresh page)
6. **Look for the failed request**:
   - Find request to `tickers/available` or `financial/tickers/available`
   - **Click on it** to see details
   - **Check the "Request URL"** or "General" section

**What to look for:**

✅ **Correct URL** (should work):
```
https://sec-exctractor.onrender.com/api/financial/tickers/available
```

❌ **Wrong URL** (will give 404):
```
https://sec-exctractor.onrender.com/financial/tickers/available
```
(Missing `/api` prefix)

❌ **Wrong URL** (will give 404):
```
http://localhost:8000/api/financial/tickers/available
```
(Using localhost default)

---

## 🔍 Step 2: Check Environment Variable in Browser

### In Browser Console:

1. **Open DevTools** (F12) → **Console** tab
2. **Run this command**:
   ```javascript
   console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)
   ```

**Expected output:**
```
API URL: https://sec-exctractor.onrender.com/api
```

**If you see:**
- `undefined` → Environment variable not set
- `https://sec-exctractor.onrender.com` (no `/api`) → Missing `/api`
- `http://localhost:8000/api` → Using default, env var not set

---

## 🔧 Fix: Update Vercel Environment Variable

### Step 1: Verify in Vercel

1. **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. **Find `NEXT_PUBLIC_API_URL`**
3. **Check the value**:
   - Should be: `https://sec-exctractor.onrender.com/api`
   - Must include `/api` at the end
   - No trailing slash after `/api`

### Step 2: Check Environment Scope

**For Preview Deployments:**
- `NEXT_PUBLIC_API_URL` should be set for **Preview** environment
- Or set for **All** environments (Production, Preview, Development)

**To check:**
- Click on `NEXT_PUBLIC_API_URL` in the list
- See which environments it's enabled for
- Should show: ✅ Preview (or ✅ All)

### Step 3: If Wrong, Fix It

1. **Click Edit** on `NEXT_PUBLIC_API_URL`
2. **Set value to**:
   ```
   https://sec-exctractor.onrender.com/api
   ```
3. **Select environments**: ✅ **Preview** (or ✅ All)
4. **Click Save**

### Step 4: Redeploy Vercel

**Important**: Environment variables require a redeploy to take effect!

1. **Go to Deployments** tab
2. **Click "..."** (three dots) on latest deployment
3. **Click "Redeploy"**
4. **Wait for deployment to complete**

---

## 🧪 Test After Fix

### Test 1: Check Environment Variable

After redeploy, in browser console:
```javascript
console.log(process.env.NEXT_PUBLIC_API_URL)
```

Should show: `https://sec-exctractor.onrender.com/api`

### Test 2: Check Network Request

1. **Open Network tab** in DevTools
2. **Refresh page** or use the app
3. **Find request to `tickers/available`**
4. **Check URL** - should be:
   ```
   https://sec-exctractor.onrender.com/api/financial/tickers/available
   ```

### Test 3: Test API Call Directly

In browser console (on your Vercel deployment):
```javascript
fetch('https://sec-exctractor.onrender.com/api/financial/tickers/available')
  .then(r => r.json())
  .then(data => console.log('Success:', data))
  .catch(err => console.error('Error:', err))
```

Should return the tickers list.

---

## 🎯 Most Likely Issues

### Issue 1: Environment Variable Not Set for Preview (90% likely)

**Symptom**: 
- Variable exists but only set for Production
- Preview deployment uses default `http://localhost:8000/api`

**Fix**: 
- Set `NEXT_PUBLIC_API_URL` for **Preview** environment
- Redeploy

### Issue 2: Missing `/api` in URL (5% likely)

**Symptom**: 
- Frontend calls `https://sec-exctractor.onrender.com/financial/tickers/available`
- Missing `/api` prefix

**Fix**: 
- Update `NEXT_PUBLIC_API_URL` to include `/api`
- Redeploy

### Issue 3: Variable Not Redeployed (5% likely)

**Symptom**: 
- Variable is set correctly
- But old deployment still uses old value

**Fix**: 
- Redeploy Vercel after setting env var

---

## ✅ Complete Fix Checklist

- [ ] **Backend works** ✅ (confirmed)
- [ ] **Check Network tab** - see what URL frontend calls
- [ ] **Check browser console** - see env var value
- [ ] **Verify `NEXT_PUBLIC_API_URL`** in Vercel = `https://sec-exctractor.onrender.com/api`
- [ ] **Set for Preview environment** (or All)
- [ ] **Redeploy Vercel** after fixing
- [ ] **Test again** - should work now!

---

## 📝 Correct Configuration

### Vercel Environment Variable:
```
NEXT_PUBLIC_API_URL=https://sec-exctractor.onrender.com/api
```

**Environments**: ✅ Preview (or ✅ All)

### Expected Frontend API Call:
```
https://sec-exctractor.onrender.com/api/financial/tickers/available
```

### Expected Response:
```json
{
  "tickers": ["A", "AAPL", "ABBV", ...],
  "count": 500
}
```

---

## 🚨 Quick Debug Command

Run this in browser console to see what's happening:
```javascript
// Check env var
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)

// Test API call
fetch(process.env.NEXT_PUBLIC_API_URL + '/financial/tickers/available')
  .then(r => {
    console.log('Status:', r.status)
    return r.json()
  })
  .then(data => console.log('Data:', data))
  .catch(err => console.error('Error:', err))
```

This will show you:
- What URL the frontend thinks it should use
- Whether the API call works
- Any errors

---

**Next Step**: Check the Network tab to see what URL the frontend is actually calling, then fix the environment variable if needed! 🚀

