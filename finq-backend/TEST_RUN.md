# 🧪 How to Test Run the App

## Quick Start

### 1. Activate Virtual Environment

```bash
cd finq-backend
source venv/bin/activate
```

### 2. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

### 3. Test the API

**Option A: Browser**
- Open: http://localhost:8000/docs
- This shows interactive API documentation (Swagger UI)
- Click "Try it out" on any endpoint

**Option B: curl**
```bash
# Health check
curl http://localhost:8000/api/health

# Should return:
# {"status":"healthy","timestamp":"2025-01-XX...","service":"finq-backend"}
```

**Option C: Python**
```python
import requests
response = requests.get("http://localhost:8000/api/health")
print(response.json())
```

## Available Endpoints

### Health Check
- **URL**: http://localhost:8000/api/health
- **Method**: GET
- **Response**: `{"status": "healthy", ...}`

### API Documentation
- **URL**: http://localhost:8000/docs
- **Description**: Interactive Swagger UI

### ReDoc Documentation
- **URL**: http://localhost:8000/redoc
- **Description**: Alternative API documentation

## Testing Checklist

- [ ] Server starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] API docs accessible at /docs
- [ ] No import errors in logs

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### Import Errors
```bash
# Make sure you're in finq-backend directory
cd finq-backend

# Activate venv
source venv/bin/activate

# Verify Python path
which python  # Should show venv path
```

### Configuration Errors
```bash
# Check .env file exists
ls -la .env

# Test config loading
python -c "from app.config import settings; print('OK')"
```

## Next Steps

Once the server is running:
1. Visit http://localhost:8000/docs
2. Test the health endpoint
3. Explore the API documentation
4. Start building features!

---

**Note**: The server runs with `--reload` flag, so it will automatically restart when you make code changes.

