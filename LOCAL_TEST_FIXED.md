# Fixed Local Test Commands

## Issue Found
The connection is failing with DNS resolution error. This suggests either:
1. Network connectivity issue
2. DNS resolution problem
3. The hostname might need verification

## Step-by-Step Commands

### Step 1: Install psycopg2-binary (Already Done ✅)
```bash
cd finq-backend
pip install psycopg2-binary
```

### Step 2: Test DNS Resolution
```bash
# Test if hostname resolves
nslookup db.tdebmqhaoiexsdhxwung.supabase.co

# Or use ping (will fail to connect but shows if DNS works)
ping -c 1 db.tdebmqhaoiexsdhxwung.supabase.co
```

### Step 3: Set Database URL and Test Connection
```bash
export DATABASE_URL="postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require"

# Test connection
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

### Step 4: If Connection Works, Run the App
```bash
# Make sure DATABASE_URL is still set
export DATABASE_URL="postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require"

# Run the app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 5: Test the API (In Another Terminal)
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Or open in browser
open http://localhost:8000/docs
```

### Step 6: Kill the Process
```bash
# Press Ctrl+C in the terminal where uvicorn is running
# OR find and kill:
kill $(lsof -ti:8000)
```

## If DNS Resolution Fails

If `nslookup` or `ping` fails, it means:
1. **Network issue**: Your local network can't reach Supabase
2. **DNS issue**: DNS servers can't resolve the hostname
3. **Firewall/VPN**: Something is blocking the connection

**Solutions:**
- Check your internet connection
- Try a different network (mobile hotspot)
- Check if VPN is blocking
- Verify the Supabase project is active

## If Connection Works Locally But Not on Railway

This confirms it's a **Railway-specific network issue** (IPv6 problem). In that case:
1. The connection string with parameters should work on Railway
2. We may need to contact Railway support about IPv6 connectivity
3. Or use a different deployment platform

## Quick Test Script

```bash
#!/bin/bash
cd finq-backend

# Set database URL
export DATABASE_URL="postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require"

# Test DNS first
echo "Testing DNS resolution..."
if nslookup db.tdebmqhaoiexsdhxwung.supabase.co > /dev/null 2>&1; then
    echo "✅ DNS resolution works"
else
    echo "❌ DNS resolution failed - check your network"
    exit 1
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
    echo ""
    echo "✅ All tests passed! Starting server..."
    echo "Server will run at http://localhost:8000"
    echo "Press Ctrl+C to stop"
    echo ""
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "❌ Database connection test failed"
    exit 1
fi
```

## What This Tells Us

- **If local connection works**: Railway has a network/IPv6 issue
- **If local connection fails**: There's a network/DNS issue on your machine
- **If DNS fails**: Network connectivity problem

Run these commands and let me know the results!

