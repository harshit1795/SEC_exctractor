# Monthly Data Pipeline Automation Plan

## Current Structure Analysis ✅

### What Works Well
1. **Data Pipeline Service**: Fully functional `DataPipeline` class
2. **API Endpoints**: RESTful endpoints for updates (`/update-latest`, `/update-batch`)
3. **Incremental Updates**: Smart merging prevents duplicates
4. **Rate Limiting**: Built-in delays (0.5s) to avoid Yahoo Finance throttling
5. **Status Monitoring**: Endpoint to check data freshness

### Current Limitations for Monthly Automation
1. ❌ **No Scheduling**: No cron/scheduled task mechanism
2. ❌ **File Persistence**: On Railway, files are ephemeral - need persistent storage
3. ❌ **No Monitoring**: No alerts/notifications for failed runs
4. ❌ **No Logging**: Limited visibility into scheduled runs

## Proposed Solution: Monthly Automated Updates

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Monthly Trigger (Railway Cron / GitHub Actions)         │
└────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  API Endpoint: POST /api/data-pipeline/update-latest    │
└────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  DataPipeline Service                                    │
│  - Fetches from Yahoo Finance                            │
│  - Updates fundamentals_tall.parquet                    │
│  - Saves to persistent storage                          │
└────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Persistent Storage (Railway Volume / S3)                │
│  - fundamentals_tall.parquet                            │
└─────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Persistent Storage ✅ (Critical)

**Problem**: Railway's filesystem is ephemeral - files are lost on redeploy.

**Solution Options**:

#### Option A: Railway Volume (Recommended)
1. Create a Railway volume for data persistence
2. Mount it at `/data` or `/app/data`
3. Update `FUNDAMENTALS_PATH` to point to volume

**Steps**:
```bash
# In Railway Dashboard:
1. Service → Volumes → Add Volume
2. Name: "fundamentals-data"
3. Mount Path: "/data"
4. Set env var: FUNDAMENTALS_PATH=/data/fundamentals_tall.parquet
```

#### Option B: Cloud Storage (S3/GCS)
- Upload/download from S3 on each update
- More complex but more scalable
- Better for multiple instances

#### Option C: Database Storage
- Store parquet in PostgreSQL (as bytea)
- More complex queries but fully managed

**Recommendation**: Start with Railway Volume (Option A) - simplest and sufficient for monthly updates.

### Phase 2: Scheduling Mechanism

#### Option A: Railway Cron Jobs (Recommended)
Railway supports cron jobs via their platform.

**Implementation**:
1. Create a separate Railway service for cron
2. Use Railway's cron syntax
3. Call the API endpoint monthly

**Example**:
```yaml
# railway.toml or Railway dashboard
[deploy]
cron = "0 2 1 * *"  # 2 AM on 1st of every month
```

#### Option B: GitHub Actions (Alternative)
Create a GitHub Actions workflow that runs monthly.

**Implementation**:
```yaml
# .github/workflows/monthly-data-update.yml
name: Monthly Data Update
on:
  schedule:
    - cron: '0 2 1 * *'  # 2 AM UTC on 1st of month
  workflow_dispatch:  # Allow manual trigger

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Data Update
        run: |
          curl -X POST ${{ secrets.RAILWAY_API_URL }}/api/data-pipeline/update-latest
```

#### Option C: External Cron Service (Cron-job.org, EasyCron)
- Simple HTTP endpoint call
- Free tier available
- No code changes needed

**Recommendation**: Railway Cron if available, otherwise GitHub Actions.

### Phase 3: Monitoring & Logging

**Add**:
1. **Success/Failure Notifications**: Email/Slack on completion
2. **Detailed Logging**: Log each ticker update status
3. **Health Checks**: Verify data freshness after update
4. **Error Alerts**: Notify on failures

### Phase 4: Data Validation

**Add checks**:
1. Verify file exists after update
2. Check data freshness (latest period)
3. Validate data integrity (row counts, schema)
4. Compare with previous month's data

## Implementation Steps

### Step 1: Set Up Persistent Storage (Railway Volume)

1. **Create Volume in Railway**:
   - Service → Volumes → Add Volume
   - Name: `fundamentals-data`
   - Mount Path: `/data`

2. **Update Environment Variable**:
   - Add: `FUNDAMENTALS_PATH=/data/fundamentals_tall.parquet`

3. **Update Code** (if needed):
   - Ensure path resolution includes `/data/fundamentals_tall.parquet`

### Step 2: Create Scheduled Update Script

Create a script that can be called by cron:

```python
# finq-backend/scripts/monthly_update.py
"""
Monthly data pipeline update script
Can be called by Railway cron, GitHub Actions, or external cron service
"""
import asyncio
import sys
from app.services.data_pipeline import DataPipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Run monthly data update"""
    try:
        pipeline = DataPipeline()
        
        # Get all tickers that need updates
        status = await pipeline.get_latest_periods()
        
        if status.get('ticker_periods'):
            tickers = list(status['ticker_periods'].keys())
        else:
            # Fallback to common tickers
            tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']
        
        logger.info(f"Starting monthly update for {len(tickers)} tickers")
        
        result = await pipeline.update_all_tickers(tickers, batch_size=10, delay=0.5)
        
        logger.info(f"Update completed: {result['updated']} updated, {result['failed']} failed")
        
        if result['failed'] > 0:
            logger.warning(f"Some updates failed: {result['failed']}")
            sys.exit(1)
        
        sys.exit(0)
    except Exception as e:
        logger.error(f"Monthly update failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Set Up Scheduling

**Option A: Railway Cron** (if available):
- Create separate service or use existing
- Configure cron schedule: `0 2 1 * *` (2 AM on 1st of month)

**Option B: GitHub Actions**:
- Create `.github/workflows/monthly-data-update.yml`
- Schedule: `cron: '0 2 1 * *'`
- Call Railway API endpoint

**Option C: External Cron**:
- Use cron-job.org or similar
- Schedule: Monthly on 1st at 2 AM
- Call: `POST https://secexctractor-production-80f5.up.railway.app/api/data-pipeline/update-latest`

### Step 4: Add Monitoring

Add notification endpoint or integrate with monitoring service:

```python
# Add to data_pipeline.py
async def send_update_notification(result: Dict):
    """Send notification about update status"""
    # Email, Slack, or logging service
    pass
```

## Testing the Setup

### Test Locally
```bash
# Test the update script
cd finq-backend
python scripts/monthly_update.py

# Or test via API
curl -X POST http://localhost:8000/api/data-pipeline/update-latest
```

### Test on Railway
```bash
# Test API endpoint
curl -X POST https://secexctractor-production-80f5.up.railway.app/api/data-pipeline/update-latest

# Check status
curl https://secexctractor-production-80f5.up.railway.app/api/data-pipeline/status
```

## Monthly Update Schedule

**Recommended**: 1st of each month at 2 AM UTC
- Companies typically report earnings quarterly
- Monthly updates catch new quarters as they're released
- 2 AM UTC = off-peak hours, less load

**Alternative**: Weekly updates (if needed for more frequent data)

## Data Freshness Monitoring

Add endpoint to check when data was last updated:

```python
@router.get("/data-pipeline/freshness")
async def check_data_freshness():
    """Check how fresh the data is"""
    status = await pipeline.get_latest_periods()
    # Return latest period, days since update, etc.
```

## Cost Considerations

- **Railway Volume**: ~$0.10/GB/month (minimal for 1.8MB file)
- **API Calls**: Yahoo Finance is free (but rate-limited)
- **Compute**: Monthly cron job uses minimal resources

## Next Steps

1. ✅ **Immediate**: Set up Railway Volume for persistent storage
2. ✅ **Week 1**: Create monthly update script
3. ✅ **Week 2**: Set up scheduling (Railway Cron or GitHub Actions)
4. ✅ **Week 3**: Add monitoring and notifications
5. ✅ **Week 4**: Test full monthly cycle

## Dependencies

All modules that use fundamentals data:
- ✅ Dashboard (categories, metrics)
- ✅ Health Scores (FinQ scores, custom scores)
- ✅ Financial Analysis (trends, snapshots)
- ✅ Chat Bot (context data)

All will automatically use updated data once the file is refreshed.

