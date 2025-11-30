# Supabase Direct Connection Guide (When Pooling Not Available)

## If You Can't Find Connection Pooling

If you don't see "Connection Pooling" on the Database Settings page, you can use the **direct connection string** instead. Here's how:

## Step 1: Find Connection String on Database Settings Page

On the Supabase Database Settings page (`https://supabase.com/dashboard/project/tdebmqhaoiexsdhxwung/database/settings`), look for:

### Option A: Connection String Section
- Look for **"Connection string"** or **"Connection info"**
- Should show a connection string like:
  ```
  postgresql://postgres:[YOUR-PASSWORD]@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres
  ```

### Option B: Connection Parameters
You might see separate fields:
- **Host**: `db.tdebmqhaoiexsdhxwung.supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **User**: `postgres`
- **Password**: `[Your password]`

### Option C: Connection Pooling Tab (Alternative Location)
1. Look for tabs at the top: **"Connection string"**, **"Connection pooling"**, **"Settings"**
2. Click on **"Connection string"** tab
3. You should see the connection string there

## Step 2: Construct the Connection String

If you see separate fields, construct it like this:

```
postgresql://postgres:[PASSWORD]@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres
```

**Replace:**
- `[PASSWORD]` with your actual database password
- If password has special characters, URL-encode them:
  - `@` → `%40`
  - `#` → `%23`
  - `$` → `%24`
  - `%` → `%25`
  - `&` → `%26`
  - `+` → `%2B`
  - `=` → `%3D`

## Step 3: Disable IP Allowlist (CRITICAL)

**This is the most important step!** Railway uses dynamic IPs that won't be in Supabase's allowlist.

### How to Disable IP Allowlist:

1. On the Database Settings page, look for:
   - **"Network Restrictions"**
   - **"IP Allowlist"**
   - **"Restrict connections to specific IP addresses"**
   - **"Connection Security"**

2. **Disable** or **turn OFF** any IP restriction settings

3. If you can't find it:
   - Go to: **Settings** → **Database** → **Network Restrictions**
   - Or: **Project Settings** → **Database** → **Connection Pooling**

4. Make sure it says **"Allow all IPs"** or **"No restrictions"**

## Step 4: Alternative - Find Connection String in Project Settings

If you still can't find it:

1. Go to: **Project Settings** (gear icon in left sidebar)
2. Click **"Database"** or **"Connection string"**
3. Look for **"Connection string"** or **"URI"**
4. Copy the connection string

## Step 5: Update Railway

1. Go to **Railway Dashboard**: https://railway.app
2. Select your **backend service**
3. Go to **Variables** tab
4. Find `DATABASE_URL`
5. **Edit** it
6. **Paste** the connection string:
   ```
   postgresql://postgres:YOUR_PASSWORD@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres
   ```
7. **Important**: 
   - Don't add quotes (Railway handles it)
   - Make sure password is URL-encoded if needed
8. **Save**

## Step 6: Verify Connection

1. Railway will **auto-redeploy** after saving
2. Check **Railway logs** for:
   - ✅ "Connected to database" or similar success message
   - ❌ Any connection errors

3. Test the API:
   ```bash
   curl https://your-railway-url.up.railway.app/api/health
   ```

## Why Direct Connection Works

Even without connection pooling, the direct connection (port 5432) will work **IF**:
- ✅ IP allowlist is **disabled**
- ✅ Password is **correct** and **URL-encoded**
- ✅ Connection string format is **correct**

## Troubleshooting

### Still Getting "Network is unreachable"

1. **Double-check IP allowlist is disabled**:
   - This is the #1 cause of connection failures
   - Railway IPs are dynamic and won't be whitelisted

2. **Verify password**:
   - Make sure it's correct
   - URL-encode special characters

3. **Check Supabase project status**:
   - Make sure project is **active** (not paused)
   - Database is **running**

4. **Test connection locally first**:
   ```bash
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

### If Local Works but Railway Doesn't

This confirms it's an **IP allowlist issue**:
- Go back to Supabase settings
- Find and **disable** IP restrictions
- Railway will then be able to connect

## Quick Checklist

- [ ] Found connection string on Database Settings page
- [ ] Copied connection string (port 5432)
- [ ] Replaced `[PASSWORD]` with actual password
- [ ] URL-encoded password if it has special characters
- [ ] **Disabled IP allowlist** (most important!)
- [ ] Updated `DATABASE_URL` in Railway Variables
- [ ] Saved changes in Railway
- [ ] Checked Railway logs for successful connection
- [ ] Tested API endpoint

## Alternative: Get Connection String from Supabase CLI

If you have Supabase CLI installed:

```bash
supabase status
```

This will show you the connection string.

## What to Look For on the Page

The Database Settings page should have sections like:
- **Connection Info**
- **Connection String**
- **Database URL**
- **Connection Parameters**
- **Network Restrictions** ← Check this one!

Scroll through the page - the connection string might be in a different section than expected.

Good luck! The key is **disabling the IP allowlist** - that's what's blocking Railway's connection. 🔓

