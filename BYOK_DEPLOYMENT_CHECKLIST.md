# BYOK Deployment Checklist

## 🚀 Quick Deployment Guide for BYOK Feature

### ⚡ Quick Summary

You now have a complete BYOK (Bring Your Own Key) implementation! Users can add their own Google Gemini and FRED API keys through the Settings page. Keys are encrypted and stored securely in the database.

---

## 📋 Pre-Deployment Checklist

### 1. Generate Encryption Key

First, generate a secure encryption key for encrypting user API keys:

```python
# Run this in Python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

Example output: `ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg=`

**⚠️ IMPORTANT**: Save this key securely! If you lose it, you won't be able to decrypt existing user keys.

### 2. Update Render Environment Variables

Go to your Render backend service dashboard and add/update these environment variables:

#### Required:
```bash
ENCRYPTION_KEY=<paste-the-key-you-generated-above>
```

#### Optional (but recommended for fallback):
```bash
GEMINI_API_KEY=<your-global-gemini-key>  # Optional fallback
FRED_API_KEY=<your-global-fred-key>      # Optional fallback
```

**Note**: If you don't set global keys, users MUST provide their own keys to use AI features.

### 3. Test Locally (Optional but Recommended)

Before deploying, test locally:

```bash
# Terminal 1 - Backend
cd finq-backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
export ENCRYPTION_KEY="<your-key-here>"
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd finq-frontend
npm run dev
```

Test the Settings page:
1. Navigate to http://localhost:3000/settings
2. Try adding an API key
3. Try validating it
4. Try deleting it

---

## 🚢 Deployment Steps

### Step 1: Deploy Backend to Render

```bash
# Commit all changes
git add .
git commit -m "Add BYOK (Bring Your Own Key) feature for Gemini and FRED APIs"
git push origin main  # or your deployment branch
```

Render will automatically:
1. Pull the latest code
2. Install dependencies
3. Run database migrations (creates `user_api_keys` table)
4. Restart the backend

**⏱️ Estimated time**: 5-10 minutes

**✅ Verify Backend Deployment:**
1. Visit `https://your-backend.onrender.com/docs`
2. Look for new endpoints under "user-api-keys" section:
   - `GET /api/user-api-keys/status`
   - `POST /api/user-api-keys/set`
   - `POST /api/user-api-keys/validate`
   - `DELETE /api/user-api-keys/delete`

### Step 2: Deploy Frontend to Vercel

```bash
# If not already pushed
git push origin main  # or your deployment branch
```

Vercel will automatically:
1. Pull the latest code
2. Build the Next.js application
3. Deploy to production

**⏱️ Estimated time**: 2-5 minutes

**✅ Verify Frontend Deployment:**
1. Visit `https://your-app.vercel.app/settings`
2. You should see a new "API Keys (Bring Your Own Key)" section

---

## 🧪 Post-Deployment Testing

### Test 1: API Keys Status
```bash
# Using curl
curl "https://your-backend.onrender.com/api/user-api-keys/status?user_id=test-user-id"

# Expected response:
# {
#   "user_id": "test-user-id",
#   "has_gemini_key": false,
#   "has_fred_key": false,
#   "gemini_key_is_valid": null,
#   "fred_key_is_valid": null
# }
```

### Test 2: Settings Page UI
1. Sign in to your app
2. Navigate to Settings
3. Scroll to "API Keys (Bring Your Own Key)"
4. You should see:
   - Gemini API Key section (collapsed/expandable)
   - FRED API Key section (collapsed/expandable)
   - Links to get API keys

### Test 3: Add and Validate Key
1. Get a test Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Paste it in the Settings page
3. Click "Save Gemini Key"
4. Click "Validate Key"
5. Should show "API key is valid! ✓"

### Test 4: Use Custom Key in Chat
1. After adding your key
2. Navigate to Dashboard
3. Open the Chatbot tab
4. Ask a question
5. Backend should use YOUR key (check logs to confirm)

---

## 🔍 Monitoring & Verification

### Check Backend Logs

In Render dashboard:
1. Go to your backend service
2. Click "Logs" tab
3. Look for these messages:
   - `🔄 Running database migrations...`
   - `✅ Database migrations completed successfully`
   - `Using user-provided Gemini API key for user <user-id>` (when users use their keys)

### Check Database Migration

Connect to your database and verify the new table exists:

```sql
-- Check if table exists
SELECT * FROM user_api_keys LIMIT 1;

-- Should return: no rows (initially empty)
```

### Monitor for Errors

Watch for these common issues:

**Backend Errors:**
- `ENCRYPTION_KEY not configured` → Set the environment variable
- `Migration failed` → Check database connection and permissions
- `Failed to encrypt data` → Verify encryption key is valid

**Frontend Errors:**
- `Network Error` → Check if backend URL is correct
- `Failed to load API keys status` → Check authentication and backend availability

---

## 📊 Success Indicators

✅ **Backend**:
- [ ] `/docs` endpoint shows new user-api-keys routes
- [ ] Database migration completed successfully
- [ ] No errors in backend logs
- [ ] Can call API endpoints via Swagger UI

✅ **Frontend**:
- [ ] Settings page loads without errors
- [ ] API Keys section is visible
- [ ] Can input and save API keys
- [ ] Can validate and delete keys
- [ ] Status indicators work correctly

✅ **Integration**:
- [ ] Chat uses user-specific keys when available
- [ ] Falls back to global keys correctly
- [ ] Error messages are clear and helpful

---

## 🐛 Troubleshooting

### Issue: "Migration failed"

**Check**: Does the `ENCRYPTION_KEY` environment variable exist?

```bash
# In Render dashboard, verify environment variables
echo $ENCRYPTION_KEY  # Should output your key
```

**Fix**: Add the encryption key to Render environment variables and restart.

### Issue: "Cannot connect to backend"

**Check**: Is the backend running?

```bash
# Test health endpoint
curl https://your-backend.onrender.com/api/health
```

**Fix**: 
1. Check Render logs for errors
2. Verify environment variables
3. Restart the backend service

### Issue: "Failed to validate API key"

**Check**: Is the API key correct?

**Fix**:
1. Copy the key again (ensure no spaces)
2. Verify the key works directly with the provider
3. Try generating a new key

### Issue: "Keys not encrypted in database"

**Check**: Look at the database directly

```sql
SELECT gemini_api_key_encrypted FROM user_api_keys LIMIT 1;
```

**Expected**: Should see encrypted string like `gAAAABl...`  
**Not Expected**: Plain text API key

**Fix**: If you see plain text, check encryption service initialization.

---

## 🔄 Rollback Plan

If something goes wrong, you can rollback:

### Quick Rollback (Code Only)
```bash
git revert HEAD
git push origin main
```

### Full Rollback (Including Database)
```bash
# Rollback migration
cd finq-backend
alembic downgrade -1

# Then revert code
git revert HEAD
git push origin main
```

---

## 📞 Need Help?

### Debugging Steps:
1. Check Render backend logs
2. Check Vercel frontend logs
3. Check browser console (F12)
4. Test API endpoints in `/docs`
5. Verify environment variables

### Quick Tests:
```bash
# Test backend health
curl https://your-backend.onrender.com/api/health

# Test API keys endpoint
curl "https://your-backend.onrender.com/api/user-api-keys/status?user_id=test"

# Expected: 200 OK with JSON response
```

---

## ✅ Final Checklist

Before marking as complete:

- [ ] Encryption key generated and saved securely
- [ ] Environment variables set in Render
- [ ] Backend deployed successfully
- [ ] Frontend deployed successfully
- [ ] Database migration completed
- [ ] API endpoints accessible in /docs
- [ ] Settings page shows API Keys section
- [ ] Can save and validate a test key
- [ ] Chat uses user keys correctly
- [ ] Error messages are clear
- [ ] Documented for team/users

---

## 🎉 You're Done!

Your BYOK feature is now live! Users can:
- Add their own API keys in Settings
- Validate keys before using them
- Use the app without relying on global keys
- Delete keys anytime

**Next Steps:**
1. Announce the feature to users
2. Monitor usage and errors
3. Collect feedback
4. Consider future enhancements (see `BYOK_IMPLEMENTATION_GUIDE.md`)

---

**Deployment Date**: _____________  
**Deployed By**: _____________  
**Status**: 🚀 Ready for Production
