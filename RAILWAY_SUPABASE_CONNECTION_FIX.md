# Railway Supabase Connection Fix

## Error
```
connection to server at "db.tdebmqhaoiexsdhxwung.supabase.co" (2600:1f13:838:6e02:36ff:2798:9ff:23da), port 5432 failed: Network is unreachable
```

## Root Causes

1. **Supabase IP Allowlist** - Most common issue
2. **Incorrect DATABASE_URL format** in Railway
3. **Supabase project paused** or deleted
4. **Network connectivity** from Railway to Supabase

## Solution 1: Disable Supabase IP Allowlist (Recommended)

### Step 1: Check Supabase Settings

1. Go to: https://supabase.com/dashboard
2. Select your project: `tdebmqhaoiexsdhxwung`
3. Go to: **Settings** → **Database** → **Connection Pooling**

### Step 2: Disable IP Allowlist

1. Look for **"Connection Pooling"** or **"IP Allowlist"**
2. Find **"Restrict connections to specific IP addresses"**
3. **Disable** this setting (turn it OFF)
4. **Save** changes

### Step 3: Verify Connection String

1. In Supabase Dashboard → **Settings** → **Database**
2. Find **"Connection string"** or **"Connection Pooling"**
3. Copy the connection string
4. Format should be: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`

**OR** use direct connection:
- `postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres`

## Solution 2: Check DATABASE_URL in Railway

### Step 1: Verify Railway Environment Variable

1. Go to Railway Dashboard
2. Select your service
3. Go to **Variables** tab
4. Find `DATABASE_URL`
5. Check the format

### Step 2: Correct Format

**For Direct Connection:**
```
postgresql://postgres:YOUR_PASSWORD@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres
```

**For Connection Pooling (Recommended):**
```
postgresql://postgres.tdebmqhaoiexsdhxwung:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### Step 3: Update in Railway

1. Railway → Your Service → **Variables**
2. Edit `DATABASE_URL`
3. **Important**: 
   - Don't add quotes in Railway (Railway handles it)
   - Make sure password is URL-encoded if it has special characters
   - Use the **pooler** connection string if available (better for Railway)

### Step 4: URL Encode Password (If Needed)

If your password has special characters, encode them:
- `@` → `%40`
- `#` → `%23`
- `$` → `%24`
- `%` → `%25`
- `&` → `%26`
- `+` → `%2B`
- `=` → `%3D`

**Example:**
- Password: `MyP@ss#123`
- Encoded: `MyP%40ss%23123`
- Full URL: `postgresql://postgres:MyP%40ss%23123@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres`

## Solution 3: Use Connection Pooling (Best for Railway)

### Why Connection Pooling?

- Better for serverless/containerized deployments
- Handles connection limits better
- More reliable for Railway

### Step 1: Get Pooler Connection String

1. Supabase Dashboard → **Settings** → **Database**
2. Find **"Connection Pooling"** section
3. Copy the **"Connection string"** (port 6543)
4. Format: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`

### Step 2: Update Railway

1. Railway → Variables → `DATABASE_URL`
2. Replace with pooler connection string
3. Save

## Solution 4: Check Supabase Project Status

### Step 1: Verify Project is Active

1. Go to: https://supabase.com/dashboard
2. Check if project `tdebmqhaoiexsdhxwung` is:
   - ✅ **Active** (not paused)
   - ✅ **Running** (not deleted)
   - ✅ **Accessible**

### Step 2: Check Database Status

1. Supabase Dashboard → **Database**
2. Check if database is:
   - ✅ **Running**
   - ✅ **Accessible**
   - ✅ **Not paused**

## Solution 5: Test Connection Locally First

### Step 1: Test from Your Machine

```bash
# Test connection string
python -c "
from sqlalchemy import create_engine
import sys

DATABASE_URL = 'postgresql://postgres:YOUR_PASSWORD@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres'

try:
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    print('✅ Connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
    sys.exit(1)
"
```

### Step 2: If Local Works but Railway Doesn't

This confirms it's an IP allowlist issue:
- ✅ Disable IP allowlist in Supabase
- ✅ Use connection pooling
- ✅ Check Railway network settings

## Quick Fix Checklist

- [ ] **Disable IP Allowlist** in Supabase (Settings → Database)
- [ ] **Verify DATABASE_URL** format in Railway (no quotes, correct format)
- [ ] **Use Connection Pooling** (port 6543) instead of direct (port 5432)
- [ ] **URL encode password** if it has special characters
- [ ] **Check Supabase project** is active and running
- [ ] **Test connection** locally first
- [ ] **Redeploy Railway** after changing DATABASE_URL

## Recommended DATABASE_URL Format for Railway

**Use Connection Pooling (Best):**
```
postgresql://postgres.tdebmqhaoiexsdhxwung:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

**Or Direct Connection:**
```
postgresql://postgres:YOUR_PASSWORD@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres
```

## After Fixing

1. **Save** DATABASE_URL in Railway
2. **Redeploy** Railway service (or it will auto-redeploy)
3. **Check logs** for successful connection
4. **Test** the API endpoint

## Still Not Working?

If still getting errors:

1. **Check Railway Logs**:
   - Railway → Your Service → **Deployments** → **View Logs**
   - Look for database connection errors

2. **Verify Requirements**:
   - Ensure `psycopg2-binary` is in `requirements.txt`
   - Railway should install it automatically

3. **Contact Support**:
   - Supabase: Check if project has any restrictions
   - Railway: Check if there are network restrictions

## Why This Happens

- **IP Allowlist**: Supabase blocks connections from unknown IPs
- **Railway IPs**: Railway uses dynamic IPs that aren't whitelisted
- **Solution**: Disable allowlist or use connection pooling

