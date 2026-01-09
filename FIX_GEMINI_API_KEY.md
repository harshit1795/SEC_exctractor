# 🔧 Fix: Gemini API Key Not Found Error

## 🔍 Problem

When using FinQ Chat, you see this error:
```
⚠️ Configuration Error: Google API authentication failed: 400 API Key not found. 
Please pass a valid API key. [reason: "API_KEY_INVALID" ...]
```

## ✅ Solution

The `GEMINI_API_KEY` is stored in the **backend's `.env` file** at:
```
finq-backend/.env
```

### Step 1: Verify API Key is Set

Check if the API key exists in your `.env` file:

```bash
cd finq-backend
cat .env | grep GEMINI_API_KEY
```

**Expected output:**
```
GEMINI_API_KEY=AIzaSy...
```

### Step 2: Verify API Key is Valid

Test if the API key works:

```bash
cd finq-backend
source venv/bin/activate
python -c "
import google.generativeai as genai
from app.config import settings

if not settings.gemini_api_key:
    print('❌ GEMINI_API_KEY not found in .env')
    exit(1)

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel('models/gemini-flash-latest')
print('✅ API key is valid and working!')
"
```

### Step 3: Restart Backend Server

**If the backend is already running**, you need to **restart it** to pick up the `.env` file:

```bash
# Stop the current backend
lsof -ti:8000 | xargs kill -9

# Start it again
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test the API

After restarting, test the chat endpoint:

```bash
curl -X POST http://localhost:8000/api/chat/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the revenue trend for AAPL?",
    "context_data": {
      "selected_tickers": ["AAPL"],
      "user_id": "test"
    }
  }'
```

---

## 📍 Where API Keys Are Stored

### For Local Development

**Backend** (`finq-backend/.env`):
```bash
GEMINI_API_KEY=your_api_key_here
FRED_API_KEY=your_fred_key_here
DATABASE_URL=postgresql://...
```

**Frontend** (`finq-frontend/.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_FIREBASE_*=(Firebase config)
```

### For Production (Render Backend)

**Render Dashboard** → Your Service → **Environment**:
- `GEMINI_API_KEY` - Set in Render environment variables
- `DATABASE_URL` - Set in Render environment variables
- `CORS_ORIGINS` - Set in Render environment variables

### For Production (Vercel Frontend)

**Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**:
- `NEXT_PUBLIC_API_URL` - Should be `https://your-render-backend.onrender.com/api`
- `NEXT_PUBLIC_FIREBASE_*` - Firebase configuration

---

## 🔍 How the Backend Loads API Keys

The backend uses **Pydantic Settings** to load environment variables:

1. **First**: Checks environment variables (system env vars)
2. **Second**: Loads from `.env` file in `finq-backend/` directory
3. **Third**: Uses default values (empty string for API keys)

**Code location**: `finq-backend/app/config.py`

```python
class Settings(BaseSettings):
    gemini_api_key: str = Field(
        default="",
        env="GEMINI_API_KEY"
    )
    
    class Config:
        env_file = ".env"  # Loads from finq-backend/.env
```

---

## 🐛 Common Issues

### Issue 1: Backend Not Reading .env File

**Symptom**: API key is in `.env` but backend says it's missing

**Fix**: 
1. Make sure `.env` is in `finq-backend/` directory (not project root)
2. Restart the backend server
3. Check file permissions: `chmod 600 finq-backend/.env`

### Issue 2: API Key Invalid or Expired

**Symptom**: Error says "API Key not found" or "API_KEY_INVALID"

**Fix**:
1. Get a new API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Update `GEMINI_API_KEY` in `.env`
3. Restart backend

### Issue 3: API Key Has Restrictions

**Symptom**: Works locally but fails in production

**Fix**:
1. Check Google Cloud Console → API Keys
2. Ensure API key has no IP restrictions
3. Ensure "Generative Language API" is enabled
4. Check if API key has quota limits

### Issue 4: Wrong .env File Location

**Symptom**: Changes to `.env` don't take effect

**Fix**:
- Make sure `.env` is in `finq-backend/` directory
- Not in project root
- Not in `finq-frontend/`

---

## ✅ Verification Checklist

- [ ] `GEMINI_API_KEY` exists in `finq-backend/.env`
- [ ] API key is not empty (has actual value)
- [ ] Backend server has been restarted after setting API key
- [ ] API key is valid (tested with Python script above)
- [ ] Google Generative Language API is enabled in Google Cloud Console
- [ ] API key has no IP restrictions (for production)

---

## 🚀 Quick Fix Commands

```bash
# 1. Check API key exists
cd finq-backend
grep GEMINI_API_KEY .env

# 2. Test API key
source venv/bin/activate
python -c "from app.config import settings; print('Key length:', len(settings.gemini_api_key))"

# 3. Restart backend
lsof -ti:8000 | xargs kill -9
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📝 Notes

- **Never commit `.env` files to Git** - They're in `.gitignore`
- **API keys are sensitive** - Keep them secure
- **Restart required** - Backend must be restarted to pick up `.env` changes
- **Production**: Use environment variables in Render/Vercel, not `.env` files

---

**After fixing, restart the backend and test FinQ Chat again!** 🎉

