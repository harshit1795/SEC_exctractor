# 🔧 Dashboard Troubleshooting Guide

## Issue: No Tickers Showing / No Charts

### **Problem 1: Ticker Selector is Empty**

**Symptoms:**
- Dropdown shows "No tickers found"
- Can't select any ticker

**Solutions:**

1. **Check Backend is Running**
   ```bash
   curl http://localhost:8000/api/financial/tickers/available
   ```
   Should return: `{"tickers": [...], "count": N}`

2. **Check Browser Console**
   - Open DevTools (F12)
   - Check Network tab for failed requests
   - Check Console for errors

3. **Verify API Endpoint**
   - Backend should be on `http://localhost:8000`
   - Frontend should call `/api/financial/tickers/available`

4. **Restart Backend** (if needed)
   ```bash
   cd finq-backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

---

### **Problem 2: No Charts Showing**

**Symptoms:**
- Ticker selected but no data
- Charts are empty
- "No metrics available" message

**Solutions:**

1. **Check Fundamentals Data**
   ```bash
   curl http://localhost:8000/api/financial/fundamentals/AAPL
   ```
   Should return data, not `{"detail": "No fundamentals data found"}`

2. **Verify Fundamentals File**
   - File should exist: `fundamentals_tall.parquet`
   - Location: Project root directory
   - Backend looks for it at: `../fundamentals_tall.parquet` (relative to backend)

3. **Install pyarrow** (if missing)
   ```bash
   cd finq-backend
   source venv/bin/activate
   pip install pyarrow
   ```

4. **Check Category Selection**
   - Make sure a category is selected
   - Category filter should auto-select first category
   - If not, manually select one

5. **Check Browser Console**
   - Look for API errors
   - Check Network tab for failed requests
   - Verify response format matches expected structure

---

### **Problem 3: Category Filter Not Working**

**Symptoms:**
- Category dropdown is empty
- Can't select category

**Solutions:**

1. **Verify Fundamentals Endpoint**
   ```bash
   curl http://localhost:8000/api/financial/fundamentals/AAPL
   ```

2. **Check Data Structure**
   - Response should have `data` array
   - Each item should have `Category` field

3. **Check Browser Console**
   - Look for errors in CategoryFilter component
   - Verify data is being received

---

## Quick Fixes

### **Restart Everything**
```bash
# Terminal 1: Backend
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd finq-frontend
npm run dev
```

### **Clear Browser Cache**
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Or clear browser cache

### **Check Environment Variables**
- Backend `.env` should have correct paths
- Frontend `.env.local` should have `NEXT_PUBLIC_API_URL=http://localhost:8000/api`

---

## Expected API Responses

### **Tickers Endpoint**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", ...],
  "count": 9
}
```

### **Fundamentals Endpoint**
```json
{
  "ticker": "AAPL",
  "data": [
    {
      "Ticker": "AAPL",
      "Category": "Income Statement",
      "Metric": "Total Revenue",
      "Value": 1234567890,
      "FiscalPeriod": "2024-01-01"
    },
    ...
  ]
}
```

---

## Debug Steps

1. **Open Browser DevTools** (F12)
2. **Go to Network tab**
3. **Filter by "tickers" or "fundamentals"**
4. **Check request/response**
5. **Look for 404, 500, or CORS errors**

---

## Common Errors

### **CORS Error**
- Backend CORS config needs to include frontend URL
- Check `finq-backend/app/config.py` and `.env`

### **404 Not Found**
- Backend not running
- Wrong API URL in frontend

### **500 Internal Server Error**
- Check backend logs
- Missing dependencies (pyarrow)
- File path issues

---

**If issues persist, check the browser console and backend logs for specific error messages.**

