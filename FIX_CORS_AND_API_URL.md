# 🔧 Fix CORS and API URL Issues

## 🐛 Issues Found

### Issue 1: CORS_ORIGINS Format Problems
**Current (WRONG):**
```
https://sec-extractor-render.vercel.app/,sec-extractor-render-ocyqq71vd-harshit-golas-projects-ef9cdcc7.vercel.app
```

**Problems:**
- ❌ Trailing slash `/` after first URL
- ❌ Missing `https://` before second URL
- ❌ No space after comma (this is actually OK, but format is inconsistent)

### Issue 2: NEXT_PUBLIC_API_URL Missing `/api`
**Current (WRONG):**
```
https://sec-exctractor.onrender.com
```

**Problem:**
- ❌ Missing `/api` at the end
- Should be: `https://sec-exctractor.onrender.com/api`

---

## ✅ Fixes

### Fix 1: Update CORS_ORIGINS in Render

**Correct Format:**
```
https://sec-extractor-render.vercel.app,https://sec-extractor-render-ocyqq71vd-harshit-golas-projects-ef9cdcc7.vercel.app
```

**Changes:**
- ✅ Removed trailing slash `/` from first URL
- ✅ Added `https://` before second URL
- ✅ Comma-separated, no spaces

**Steps:**
1. **Render Dashboard** → Your Service → **Environment** tab
2. **Find `CORS_ORIGINS`** → Click **Edit**
3. **Replace with**:
   ```
   https://sec-extractor-render.vercel.app,https://sec-extractor-render-ocyqq71vd-harshit-golas-projects-ef9cdcc7.vercel.app
   ```
4. **Click "Save"**
5. **Wait for Render to redeploy** (1-2 minutes)

---

### Fix 2: Update NEXT_PUBLIC_API_URL in Vercel

**Correct Value:**
```
https://sec-exctractor.onrender.com/api
```

**Important:** Must include `/api` at the end!

**Steps:**
1. **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. **Find `NEXT_PUBLIC_API_URL`** → Click **Edit**
3. **Update value to**:
   ```
   https://sec-exctractor.onrender.com/api
   ```
4. **Verify environment**: Should be set for **Preview** (or **All** if using production branch)
5. **Click "Save"**
6. **Redeploy Vercel**:
   - Go to **Deployments** tab
   - Click **"..."** on latest deployment
   - Click **"Redeploy"**

---

## 📋 Complete Corrected Values

### Render CORS_ORIGINS:
```
https://sec-extractor-render.vercel.app,https://sec-extractor-render-ocyqq71vd-harshit-golas-projects-ef9cdcc7.vercel.app
```

### Vercel NEXT_PUBLIC_API_URL:
```
https://sec-exctractor.onrender.com/api
```

---

## ✅ Verification Checklist

After making changes:

- [ ] **CORS_ORIGINS updated** in Render (no trailing slash, `https://` on both URLs)
- [ ] **NEXT_PUBLIC_API_URL updated** in Vercel (includes `/api` at end)
- [ ] **Render redeployed** (wait 1-2 minutes)
- [ ] **Vercel redeployed** (after env var change)
- [ ] **Test backend directly**: `https://sec-exctractor.onrender.com/api/health`
- [ ] **Test frontend**: Should connect to backend now!

---

## 🧪 Test After Fixes

### Test 1: Backend Health Check
Open in browser:
```
https://sec-exctractor.onrender.com/api/health
```

**Expected**: `{"status":"healthy","service":"FinQ Backend API"}`

### Test 2: Frontend Connection
1. **Open your Vercel deployment**
2. **Open DevTools** (F12) → **Network** tab
3. **Use the app** (navigate to dashboard)
4. **Check API requests**:
   - Should go to: `https://sec-exctractor.onrender.com/api/...`
   - Should NOT show CORS errors
   - Should NOT show network errors

### Test 3: Check Environment Variable
In browser console (on Vercel deployment):
```javascript
console.log(process.env.NEXT_PUBLIC_API_URL)
```

**Expected**: `https://sec-exctractor.onrender.com/api`

---

## 🔍 Why These Fixes Are Needed

### CORS_ORIGINS Issues:
- **Trailing slash**: Can cause CORS to fail - browsers are strict about URL matching
- **Missing https://**: Second URL won't be recognized as valid origin
- **Format**: Must be exact URLs, comma-separated

### NEXT_PUBLIC_API_URL Issue:
- **Missing `/api`**: Your frontend code expects `/api` prefix
- **Default fallback**: Without it, might try `http://localhost:8000/api` (local dev)
- **API routes**: All your API endpoints are under `/api` path

---

## 📝 Quick Copy-Paste Values

### For Render CORS_ORIGINS:
```
https://sec-extractor-render.vercel.app,https://sec-extractor-render-ocyqq71vd-harshit-golas-projects-ef9cdcc7.vercel.app
```

### For Vercel NEXT_PUBLIC_API_URL:
```
https://sec-exctractor.onrender.com/api
```

---

## 🚨 Common Mistakes to Avoid

1. ❌ **Don't add trailing slash** to CORS URLs
2. ❌ **Don't forget `https://`** on all URLs in CORS
3. ❌ **Don't forget `/api`** at end of NEXT_PUBLIC_API_URL
4. ❌ **Don't forget to redeploy** after changing env vars
5. ❌ **Don't use spaces** after commas in CORS_ORIGINS

---

**After making both fixes, wait for redeployments and test again!** 🚀

