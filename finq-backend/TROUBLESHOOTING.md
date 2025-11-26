# 🔧 Troubleshooting Guide

## "Failed to Fetch" Error

### Common Causes

1. **Backend Not Running**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/api/health
   
   # If not running, start it:
   cd finq-backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **CORS Issue**
   - Frontend on `http://localhost:8080` must be in CORS allowed origins
   - Check: `app/config.py` → `cors_origins` should include `http://localhost:8080`
   - Restart backend after changing CORS config

3. **Wrong API URL**
   - Frontend uses: `http://localhost:8000/api`
   - Check browser console (F12) for exact error

4. **Network/Firewall**
   - Check if port 8000 is accessible
   - Try accessing `http://localhost:8000/docs` directly

### Quick Fixes

```bash
# 1. Restart backend
pkill -f uvicorn
cd finq-backend && source venv/bin/activate
uvicorn app.main:app --reload

# 2. Check CORS config
cd finq-backend
python -c "from app.config import settings; print(settings.get_cors_origins())"
# Should include: http://localhost:8080

# 3. Test API directly
curl http://localhost:8000/api/health
curl http://localhost:8000/api/financial/ticker/AAPL
```

## Architecture Clarification

### **NEW Architecture (Current)**
- **Backend**: FastAPI (Python) on port 8000
- **Frontend**: HTML/JavaScript on port 8080
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **No Streamlit**: Completely separate

### **OLD Architecture (Not Used)**
- Streamlit app in root directory
- Still exists but NOT used by new frontend
- Can run separately if needed

### File Locations

**New Backend:**
- `finq-backend/app/` - FastAPI application
- `finq-backend/frontend/` - HTML/JS frontend

**Old Streamlit:**
- `pages/` - Old Streamlit pages
- `components/` - Old Streamlit components
- `home.py` - Old Streamlit entry point

## Testing

1. **Backend Health**
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Frontend Access**
   ```bash
   # Should open in browser
   open http://localhost:8080
   ```

3. **API Documentation**
   ```bash
   # Interactive API docs
   open http://localhost:8000/docs
   ```

4. **Browser Console**
   - Open DevTools (F12)
   - Check Console tab for errors
   - Check Network tab for failed requests
