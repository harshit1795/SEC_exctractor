# Free Tier Data Pipeline Plan

## Data Source Analysis

### Real-Time Data (No Update Needed) ✅
These are fetched live from APIs when requested:

1. **Yahoo Finance Price Data** (`get_yahoo_finance_data`)
   - Stock prices, market data
   - Fetched on-demand, always current
   - No storage needed

2. **FRED Economic Data** (`get_fred_series`)
   - Economic indicators from Federal Reserve
   - Fetched on-demand via API
   - No storage needed

3. **SEC Filings** (`get_10k_sections`, `get_10q_sections`)
   - 10-K, 10-Q filings
   - Fetched on-demand from SEC EDGAR
   - No storage needed

### Batch Data (Needs Periodic Updates) 📊
This data is stored in files and needs monthly updates:

1. **Fundamentals Data** (`fundamentals_tall.parquet`)
   - Quarterly financial statements (Income Statement, Balance Sheet, Cash Flow)
   - Historical data for analysis
   - **Size**: ~1.8MB
   - **Update Frequency**: Monthly (to catch new quarterly reports)
   - **Storage**: Ephemeral (lost on redeploy, but that's okay for experimental phase)

## Solution: Manual Trigger with Ephemeral Storage

### Approach
Since we're staying on free tier:
- ✅ Keep file in ephemeral storage (Railway filesystem)
- ✅ Create manual trigger endpoint/button
- ✅ Update file in place when triggered
- ✅ Accept that file is lost on redeploy (will be recreated on next trigger)
- ✅ Optional: Commit updated file to git for persistence

### Benefits
- ✅ No cost (stays on free tier)
- ✅ Simple to implement
- ✅ Full control over when updates happen
- ✅ Can test updates manually before automating

## Implementation Plan

### Phase 1: Manual Trigger Endpoint ✅

Create a simple endpoint that:
1. Updates all tickers in fundamentals file
2. Returns status and results
3. Can be called from frontend button or directly

### Phase 2: Frontend Trigger Button

Add a button in the dashboard to:
1. Trigger the update
2. Show progress
3. Display results

### Phase 3: Optional Git Persistence

If you want to persist updates:
1. After update, commit file to git
2. Push to repository
3. File survives redeployments

## Data Flow

```
User Clicks "Update Data" Button
    ↓
Frontend calls: POST /api/data-pipeline/update-latest
    ↓
Backend fetches from Yahoo Finance API
    ↓
Updates fundamentals_tall.parquet (ephemeral)
    ↓
Optional: Commit to git (if enabled)
    ↓
All modules use updated data immediately
```

## What Gets Updated

When you trigger the update:
- ✅ Fetches latest quarterly financial data from Yahoo Finance
- ✅ Updates Income Statement, Balance Sheet, Cash Flow
- ✅ Adds new quarters if available
- ✅ Merges with existing data (no duplicates)
- ✅ Updates ~9 tickers (or all tickers in file)

**Does NOT update** (these are real-time):
- ❌ Stock prices (always fetched live)
- ❌ FRED economic data (always fetched live)
- ❌ SEC filings (always fetched live)

## Storage Strategy

### Current (Ephemeral)
- File stored in Railway filesystem
- Lost on redeploy
- Recreated on next trigger
- **Pros**: Free, simple
- **Cons**: Need to re-trigger after redeploy

### Future (When Ready for Paid Tier)
- Move to Railway Volume
- File persists across redeployments
- Automatic monthly updates
- **Cost**: ~$0.10/month (minimal)

## Update Frequency Recommendations

**For Experimental Phase**:
- **Manual**: Trigger when you need fresh data
- **Before demos**: Update to show latest data
- **After earnings season**: Update to catch new quarters

**When Ready for Production**:
- Monthly automated updates
- Move to Railway Volume
- Set up GitHub Actions or cron

