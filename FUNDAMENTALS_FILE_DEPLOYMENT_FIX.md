# Fix: Fundamentals File Deployment

## Problem Identified ✅
The API test confirmed: `"Fundamentals data file not found on server"`

The `fundamentals_tall.parquet` file (1.8MB) exists in the repo root but Railway builds from `finq-backend/` directory, so it's not accessible.

## Solution Applied ✅

I've copied the file to `finq-backend/fundamentals_tall.parquet` so it's included in Railway's build context.

## Next Steps

### 1. Commit and Push the File
```bash
git add finq-backend/fundamentals_tall.parquet
git commit -m "Add fundamentals file to backend directory for Railway deployment"
git push
```

### 2. Update Railway Environment Variable
On Railway dashboard:
1. Go to **Variables** tab
2. Add/Update: `FUNDAMENTALS_PATH=fundamentals_tall.parquet`
   - This is relative to `finq-backend/` root (where Railway runs)

### 3. Redeploy
Railway will automatically redeploy, or manually trigger a redeploy.

### 4. Test
After deployment, test:
```bash
curl https://secexctractor-production-80f5.up.railway.app/api/financial/fundamentals/AAPL
```

Should now return data with categories!

## Why This Works

- Railway's `root = "finq-backend"` means it only has access to files in that directory
- The file at repo root (`../fundamentals_tall.parquet`) is outside the build context
- By copying it to `finq-backend/`, it's included in the deployment
- Setting `FUNDAMENTALS_PATH=fundamentals_tall.parquet` points to the file in the same directory

## Alternative: If File is Too Large

If the file grows beyond 100MB, consider:
1. **Railway Volumes**: Mount a volume and upload the file there
2. **Cloud Storage**: Download from S3/GCS on startup
3. **Git LFS**: Use Git Large File Storage (but Railway might not support it)

For now, 1.8MB is fine for git! ✅

