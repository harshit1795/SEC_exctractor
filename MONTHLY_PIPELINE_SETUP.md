# Monthly Data Pipeline Setup Guide

## Overview

This guide helps you set up automated monthly updates for the financial fundamentals data pipeline.

## Current Status ✅

- ✅ Data pipeline service is fully functional
- ✅ API endpoints for updates are working
- ✅ Incremental updates prevent duplicates
- ✅ Monthly update script created (`scripts/monthly_data_update.py`)
- ✅ GitHub Actions workflow created (`.github/workflows/monthly-data-update.yml`)

## Setup Options

### Option 1: Railway Volume + GitHub Actions (Recommended)

**Best for**: Production deployments with persistent storage

#### Step 1: Set Up Railway Volume

1. **Create Volume in Railway**:
   - Go to Railway → Your Service → **Volumes** tab
   - Click **"Add Volume"**
   - Name: `fundamentals-data`
   - Mount Path: `/data`
   - Click **"Add"**

2. **Update Environment Variable**:
   - Railway → Variables → Add/Update:
   - `FUNDAMENTALS_PATH=/data/fundamentals_tall.parquet`

3. **Upload Initial File** (if needed):
   - The file will be created on first update
   - Or manually upload via Railway CLI or copy from deployment

#### Step 2: Set Up GitHub Actions

1. **Add Railway API URL Secret**:
   - GitHub → Repository → Settings → Secrets and variables → Actions
   - Click **"New repository secret"**
   - Name: `RAILWAY_API_URL`
   - Value: `https://secexctractor-production-80f5.up.railway.app`
   - Click **"Add secret"**

2. **Verify Workflow File**:
   - The workflow file is already created at `.github/workflows/monthly-data-update.yml`
   - It will run automatically on the 1st of each month at 2 AM UTC
   - You can also trigger it manually from GitHub Actions tab

3. **Test the Workflow**:
   - Go to GitHub → Actions tab
   - Find "Monthly Data Pipeline Update"
   - Click **"Run workflow"** to test manually

### Option 2: Railway Cron (If Available)

**Best for**: All-in-one Railway solution

1. **Create Cron Service** (if Railway supports it):
   - Create a new Railway service
   - Set it to run: `python scripts/monthly_data_update.py`
   - Configure cron schedule: `0 2 1 * *` (1st of month at 2 AM)

2. **Set Up Volume** (same as Option 1, Step 1)

### Option 3: External Cron Service

**Best for**: Simple HTTP-based scheduling

1. **Use a Cron Service** (cron-job.org, EasyCron, etc.):
   - Sign up for free account
   - Create new cron job
   - URL: `https://secexctractor-production-80f5.up.railway.app/api/data-pipeline/update-latest`
   - Method: POST
   - Schedule: Monthly on 1st at 2 AM UTC
   - Save

2. **Set Up Volume** (same as Option 1, Step 1)

## Testing the Setup

### Test Locally

```bash
# Test the update script
cd finq-backend
python scripts/monthly_data_update.py

# Test with specific tickers
python scripts/monthly_data_update.py --tickers AAPL MSFT

# Test force refresh
python scripts/monthly_data_update.py --force
```

### Test API Endpoint

```bash
# Test update endpoint
curl -X POST https://secexctractor-production-80f5.up.railway.app/api/data-pipeline/update-latest

# Check status
curl https://secexctractor-production-80f5.up.railway.app/api/data-pipeline/status
```

### Test GitHub Actions

1. Go to GitHub → Actions
2. Find "Monthly Data Pipeline Update"
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch the logs to verify it works

## Monitoring

### Check Update Status

```bash
# Get current data status
curl https://secexctractor-production-80f5.up.railway.app/api/data-pipeline/status

# Response shows:
# - Latest period in data
# - Total records
# - Total tickers
# - Latest period per ticker
```

### Check Railway Logs

1. Railway → Service → Deployments
2. Click on latest deployment
3. View **Logs** tab
4. Look for:
   - `Starting monthly update for X tickers`
   - `Successfully updated: X`
   - `Latest period in data: YYYYQX`

### Add Notifications (Optional)

Edit `.github/workflows/monthly-data-update.yml` to add notifications:

```yaml
- name: Notify on Success
  if: success()
  run: |
    # Add Slack/Email notification
    curl -X POST $SLACK_WEBHOOK_URL -d '{"text":"Monthly data update completed successfully"}'
```

## Schedule Recommendations

- **Monthly on 1st at 2 AM UTC**: Recommended
  - Companies report quarterly, monthly updates catch new quarters
  - Off-peak hours reduce load
  - UTC avoids timezone issues

- **Weekly**: If you need more frequent updates
  - Change cron to: `0 2 * * 1` (Mondays at 2 AM)

- **Daily**: For very active monitoring
  - Change cron to: `0 2 * * *` (Every day at 2 AM)

## Troubleshooting

### Issue: File Not Persisting

**Solution**: Ensure Railway volume is mounted and `FUNDAMENTALS_PATH` points to volume path.

### Issue: Update Fails

**Check**:
1. Railway logs for errors
2. Yahoo Finance API rate limits
3. Network connectivity
4. File permissions on volume

### Issue: GitHub Actions Not Running

**Check**:
1. Workflow file is in `.github/workflows/`
2. `RAILWAY_API_URL` secret is set
3. Workflow is enabled in repository settings

## Data Freshness

After each update, verify:
- Latest period is current (e.g., "2025Q1" if we're in Q1 2025)
- All expected tickers have data
- Record counts increased (if new quarters were added)

## Cost Considerations

- **Railway Volume**: ~$0.10/GB/month (minimal for 1.8MB file)
- **GitHub Actions**: 2,000 minutes/month free (plenty for monthly job)
- **API Calls**: Yahoo Finance is free (but rate-limited)
- **Compute**: Monthly cron uses minimal resources

## Next Steps

1. ✅ Set up Railway Volume
2. ✅ Configure GitHub Actions secret
3. ✅ Test workflow manually
4. ✅ Monitor first automatic run
5. ✅ Add notifications (optional)

## Support

If issues arise:
1. Check Railway logs
2. Check GitHub Actions logs
3. Test API endpoint manually
4. Verify volume is mounted correctly

