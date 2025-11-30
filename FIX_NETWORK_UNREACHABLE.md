# Fix "Network is unreachable" Error

## The Issue

Even with correct connection string, you're getting:
```
connection to server at "db.tdebmqhaoiexsdhxwung.supabase.co" (2600:1f13:838:6e02:36ff:2798:9ff:23da), port 5432 failed: Network is unreachable
```

The IPv6 address `2600:1f13:838:6e02:36ff:2798:9ff:23da` suggests Railway is trying IPv6, which might not be working.

## Solution 1: Use Connection Pooling (Port 6543) - RECOMMENDED

Connection pooling often works better with Railway and handles network issues better.

### Step 1: Get Connection Pooling String

1. Go to Supabase Dashboard: https://supabase.com/dashboard/project/tdebmqhaoiexsdhxwung
2. Go to: **Settings** → **Database**
3. Look for **"Connection Pooling"** section
4. Find connection string with port **6543**

It should look like:
```
postgresql://postgres.tdebmqhaoiexsdhxwung:Supabasefinq@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

**OR** if you see a different region:
```
postgresql://postgres.tdebmqhaoiexsdhxwung:Supabasefinq@aws-0-[region].pooler.supabase.com:6543/postgres
```

**Key differences:**
- Username: `postgres.tdebmqhaoiexsdhxwung` (includes project ref)
- Host: `aws-0-[region].pooler.supabase.com` (pooler hostname)
- Port: `6543` (pooler port, not 5432)

### Step 2: Update Railway

1. Railway → Your Service → **Variables**
2. Edit `DATABASE_URL`
3. Replace with pooling connection string:
   ```
   postgresql://postgres.tdebmqhaoiexsdhxwung:Supabasefinq@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
4. **Save**

### Step 3: Verify

- Railway will auto-redeploy
- Check logs for successful connection
- Test FinQ Chat

## Solution 2: Check Railway Logs for More Details

1. Railway → Your Service → **Deployments**
2. Click on latest deployment
3. View **Logs**
4. Look for:
   - Database connection attempts
   - Any DNS resolution errors
   - Network errors

## Solution 3: Test Connection String Locally

Test if the connection string works from your machine:

```bash
python -c "
from sqlalchemy import create_engine
import sys

# Test direct connection
DATABASE_URL = 'postgresql://postgres:Supabasefinq@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres'

try:
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    print('✅ Direct connection (5432) works!')
    conn.close()
except Exception as e:
    print(f'❌ Direct connection failed: {e}')

# Test pooling connection (if you have it)
POOLER_URL = 'postgresql://postgres.tdebmqhaoiexsdhxwung:Supabasefinq@aws-0-us-east-1.pooler.supabase.com:6543/postgres'
try:
    engine = create_engine(POOLER_URL)
    conn = engine.connect()
    print('✅ Pooler connection (6543) works!')
    conn.close()
except Exception as e:
    print(f'❌ Pooler connection failed: {e}')
"
```

## Solution 4: Check Supabase Project Status

1. Go to: https://supabase.com/dashboard/project/tdebmqhaoiexsdhxwung
2. Check if project is:
   - ✅ **Active** (not paused)
   - ✅ **Running** (not stopped)
   - ✅ **Accessible**

## Solution 5: Verify Network Restrictions

Even though you said it's disabled, double-check:

1. Supabase Dashboard → **Settings** → **Database**
2. Look for **"Network Restrictions"**
3. Should say: **"Your database can be accessed by all IP addresses"**
4. If it says anything else, disable restrictions

## Why Connection Pooling Works Better

- **Better for Railway**: Handles dynamic IPs better
- **More Reliable**: Pooler manages connections efficiently
- **IPv4/IPv6**: Pooler often handles both better
- **Recommended**: Supabase recommends pooling for serverless/containers

## If You Can't Find Connection Pooling

If connection pooling isn't available:

1. **Check Supabase Plan**: All plans should have pooling
2. **Try Different Location**: Look in **Project Settings** → **Database**
3. **Contact Supabase Support**: They can enable it

## Quick Checklist

- [ ] Found connection pooling string (port 6543)
- [ ] Updated `DATABASE_URL` in Railway with pooler string
- [ ] Verified Railway redeployed
- [ ] Checked Railway logs
- [ ] Tested connection locally
- [ ] Verified Supabase project is active

## Expected Pooler Connection String Format

```
postgresql://postgres.tdebmqhaoiexsdhxwung:Supabasefinq@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

**Note**: The region (`us-east-1`) might be different for your project. Check Supabase dashboard for your actual region.

Try connection pooling first - it's the most likely solution! 🚀

