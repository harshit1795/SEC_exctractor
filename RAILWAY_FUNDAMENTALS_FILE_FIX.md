# Fix: Fundamentals File Missing on Railway

## Problem
The API returns: `"Fundamentals data file not found on server. Please check FUNDAMENTALS_PATH environment variable."`

The `fundamentals_tall.parquet` file exists locally but is not available on Railway.

## Solution Options

### Option 1: Copy File to finq-backend Directory (Recommended)
This ensures the file is included in the Railway deployment.

```bash
# Copy the file into finq-backend directory
cp fundamentals_tall.parquet finq-backend/fundamentals_tall.parquet

# Commit and push
git add finq-backend/fundamentals_tall.parquet
git commit -m "Add fundamentals_tall.parquet to backend for Railway deployment"
git push
```

Then set `FUNDAMENTALS_PATH` on Railway to: `fundamentals_tall.parquet` (relative to finq-backend root)

### Option 2: Use Railway Volume (For Large Files)
If the file is too large for git (>100MB), use Railway volumes:

1. **Create a Volume in Railway**:
   - Railway → Your Service → **Volumes** tab
   - Click **"Add Volume"**
   - Name: `fundamentals-data`
   - Mount Path: `/data`

2. **Upload the file**:
   - Use Railway CLI or web interface to upload the file
   - Or use a startup script to download it

3. **Set FUNDAMENTALS_PATH**:
   - Railway → Variables → Add: `FUNDAMENTALS_PATH=/data/fundamentals_tall.parquet`

### Option 3: Download on Startup (If File is Large)
Create a startup script that downloads the file from a cloud storage (S3, Google Cloud Storage, etc.)

### Option 4: Set FUNDAMENTALS_PATH to Root
If the file is in the repo root, set the path relative to finq-backend:

1. **Copy file to finq-backend**:
   ```bash
   cp fundamentals_tall.parquet finq-backend/
   ```

2. **Set Railway environment variable**:
   - `FUNDAMENTALS_PATH=fundamentals_tall.parquet`

## Quick Fix (Recommended)

**Step 1**: Copy file to finq-backend
```bash
cp fundamentals_tall.parquet finq-backend/fundamentals_tall.parquet
```

**Step 2**: Verify it's not in .gitignore
```bash
git check-ignore finq-backend/fundamentals_tall.parquet
# Should return nothing (file is tracked)
```

**Step 3**: Add and commit
```bash
git add finq-backend/fundamentals_tall.parquet
git commit -m "Add fundamentals file for Railway deployment"
git push
```

**Step 4**: Set Railway environment variable
- Railway → Variables → Add/Update:
  - `FUNDAMENTALS_PATH=fundamentals_tall.parquet`

**Step 5**: Redeploy on Railway
- Railway will automatically redeploy, or manually trigger a redeploy

## Verify Fix

After deployment, test the endpoint:
```bash
curl https://secexctractor-production-80f5.up.railway.app/api/financial/fundamentals/AAPL
```

Should return data instead of the "file not found" error.

