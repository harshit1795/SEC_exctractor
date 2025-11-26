# 🧪 How to Test the FastAPI Backend

## Quick Start

### 1. Start the Server

```bash
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 2. Test in Browser (Easiest)

**Open your browser and visit:**

- **Interactive API Docs**: http://localhost:8000/docs
  - This is a Swagger UI where you can test all endpoints
  - Click "Try it out" on any endpoint
  - Click "Execute" to test

- **Health Check**: http://localhost:8000/api/health
  - Should show: `{"status":"healthy","timestamp":"...","service":"finq-backend"}`

- **Alternative Docs**: http://localhost:8000/redoc
  - ReDoc format documentation

### 3. Test with curl (Command Line)

```bash
# Health check
curl http://localhost:8000/api/health

# Should return:
# {"status":"healthy","timestamp":"2025-11-19T...","service":"finq-backend"}
```

### 4. Test with Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/health")
print(response.json())

# Should print:
# {'status': 'healthy', 'timestamp': '...', 'service': 'finq-backend'}
```

---

## Available Endpoints to Test

### ✅ Working Now

1. **Health Check**
   - GET http://localhost:8000/api/health
   - Returns: `{"status": "healthy", ...}`

2. **Root Endpoint**
   - GET http://localhost:8000/
   - Returns: API info and links

### 🚧 Under Construction (Will show placeholder messages)

3. **Financial Data**
   - GET http://localhost:8000/api/financial/ticker/{ticker}
   - GET http://localhost:8000/api/financial/tickers?tickers=AAPL,MSFT
   - GET http://localhost:8000/api/financial/fred?series_ids=GDP&start_date=2020-01-01&end_date=2024-01-01

4. **Chat API**
   - POST http://localhost:8000/api/chat/analyze
   - GET http://localhost:8000/api/chat/history?user_id=test

---

## Testing Workflow

### Step 1: Start Server
```bash
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Step 2: Open Browser
Visit: http://localhost:8000/docs

### Step 3: Test Endpoints
1. Click on `/api/health` endpoint
2. Click "Try it out"
3. Click "Execute"
4. See the response below

### Step 4: Explore
- Try other endpoints
- Check the response format
- See request/response schemas

---

## What You Should See

### In Browser (http://localhost:8000/docs):
- Swagger UI with all endpoints listed
- "Try it out" buttons on each endpoint
- Request/response examples
- Schema definitions

### Health Check Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-19T03:57:05.330143",
  "service": "finq-backend"
}
```

---

## Troubleshooting

### Server Won't Start
```bash
# Check if port 8000 is in use
lsof -ti:8000

# Kill existing process
lsof -ti:8000 | xargs kill -9

# Try again
uvicorn app.main:app --reload
```

### Can't Access in Browser
- Make sure server is running (check terminal)
- Try: http://127.0.0.1:8000/docs (instead of localhost)
- Check firewall settings

### Import Errors
```bash
# Make sure you're in finq-backend directory
cd finq-backend

# Activate venv
source venv/bin/activate

# Verify Python path
which python  # Should show venv path
```

---

## Next Steps

Once you've tested the health endpoint:

1. **Explore the API Docs**: http://localhost:8000/docs
2. **Check Available Endpoints**: See what's implemented
3. **Test Endpoints**: Use "Try it out" feature
4. **Start Building**: Add more endpoints as needed

---

**The server runs with `--reload` flag, so it automatically restarts when you make code changes!**

