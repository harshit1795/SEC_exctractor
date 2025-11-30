# Fix Direct Connection IPv6 Issue

## The Problem

Railway is trying to connect via IPv6 (`2600:1f13:838:6e02:36ff:2798:9ff:23da`), which is causing "Network is unreachable" errors.

Since connection pooling (port 6543) isn't available, we need to fix the direct connection (port 5432).

## Solution 1: Add Connection Parameters to Force IPv4

Update the `DATABASE_URL` in Railway to include connection parameters that help with the connection:

```
postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require
```

**Parameters added:**
- `connect_timeout=10` - Sets connection timeout to 10 seconds
- `sslmode=require` - Requires SSL (Supabase requires this)

## Solution 2: Update Database Connection Code

We can also update the database connection code to handle IPv6/IPv4 better. Let me check the current code and suggest improvements.

## Solution 3: Test Connection Locally First

Before updating Railway, test if the connection works from your machine:

```bash
python -c "
from sqlalchemy import create_engine
import sys

# Test with connection parameters
DATABASE_URL = 'postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require'

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    conn = engine.connect()
    print('✅ Connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
    sys.exit(1)
"
```

## Solution 4: Check Railway Network Settings

1. Railway → Your Service → **Settings**
2. Look for **"Network"** or **"Environment"** settings
3. Check if there are any network restrictions
4. Verify Railway can make outbound connections

## Solution 5: Try Different Connection String Format

Sometimes adding explicit SSL parameters helps:

```
postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?sslmode=require&connect_timeout=10&keepalives=1&keepalives_idle=30&keepalives_interval=10&keepalives_count=5
```

## Recommended: Update Railway DATABASE_URL

1. Railway → Your Service → **Variables**
2. Edit `DATABASE_URL`
3. Update to:
   ```
   postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require
   ```
4. **Save**

## Alternative: Update Database Connection Code

If the connection string parameters don't work, we can update the database connection code to handle this better.

