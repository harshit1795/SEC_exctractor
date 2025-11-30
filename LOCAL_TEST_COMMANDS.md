# Local Testing Commands

## Quick Test Commands

### Step 1: Navigate to Backend Directory
```bash
cd finq-backend
```

### Step 2: Set Database URL (One-time)
```bash
export DATABASE_URL="postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require"
```

### Step 3: Activate Virtual Environment (If You Have One)
```bash
# If you have a venv
source venv/bin/activate

# Or create one if you don't have it
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Test Database Connection
```bash
python -c "
from sqlalchemy import create_engine
import sys

DATABASE_URL = 'postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require'

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    conn = engine.connect()
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"
```

### Step 5: Run the FastAPI App
```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Using python module
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The app will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### Step 6: Test the API (In Another Terminal)
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test chat endpoint (if you have GEMINI_API_KEY set)
curl -X POST http://localhost:8000/api/chat/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "context_data": {}}'
```

### Step 7: Kill the Process

**Option A: If running in foreground (Ctrl+C)**
- Press `Ctrl+C` in the terminal where the app is running

**Option B: If you need to find and kill the process**
```bash
# Find the process
lsof -ti:8000

# Kill it
kill $(lsof -ti:8000)

# Or force kill if needed
kill -9 $(lsof -ti:8000)
```

**Option C: Kill all Python processes (nuclear option)**
```bash
pkill -f uvicorn
# or
pkill -f "app.main:app"
```

## Complete Test Script

Here's a complete script you can run:

```bash
#!/bin/bash

# Navigate to backend
cd finq-backend

# Set database URL
export DATABASE_URL="postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require"

# Activate venv (if exists)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Test database connection
echo "Testing database connection..."
python -c "
from sqlalchemy import create_engine
import sys

DATABASE_URL = 'postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require'

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    conn = engine.connect()
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Database connection works! Starting server..."
    echo "Server will run at http://localhost:8000"
    echo "Press Ctrl+C to stop"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "❌ Database connection failed. Fix the connection string first."
fi
```

## Quick Commands Summary

```bash
# 1. Go to backend
cd finq-backend

# 2. Set database URL
export DATABASE_URL="postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require"

# 3. Activate venv (if you have one)
source venv/bin/activate

# 4. Test connection
python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL', pool_pre_ping=True); conn = engine.connect(); print('✅ Connected!'); conn.close()"

# 5. Run app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 6. In another terminal, test it
curl http://localhost:8000/api/health

# 7. Kill when done (Ctrl+C or):
kill $(lsof -ti:8000)
```

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Port 8000 already in use"
```bash
# Use a different port
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Or kill the process using port 8000
kill $(lsof -ti:8000)
```

### Database connection fails locally
- Check if your local network can reach Supabase
- Verify the password is correct
- Try without the connection parameters first

