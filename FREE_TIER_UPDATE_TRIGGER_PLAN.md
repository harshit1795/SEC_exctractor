# Free Tier Data Pipeline Update Plan

## Current Status ✅

**Good News**: The infrastructure is already in place!
- ✅ `DataUpdateButton` component exists
- ✅ API endpoints work (`/update-latest`, `/update-batch`)
- ✅ Hooks are set up (`useUpdateLatestData`, `useUpdateTickerData`)
- ✅ Button is already in the dashboard

## Data Source Breakdown

### Real-Time Data (No Update Needed) ✅
These are fetched live from APIs - always current:

1. **Yahoo Finance Price Data**
   - Stock prices, market data, current quotes
   - Fetched on-demand via `get_yahoo_finance_data()`
   - Always up-to-date

2. **FRED Economic Data**
   - Economic indicators (GDP, unemployment, etc.)
   - Fetched on-demand via `get_fred_economic_data()`
   - Always up-to-date

3. **SEC Filings**
   - 10-K, 10-Q filings from SEC EDGAR
   - Fetched on-demand via `get_10k_section_data()`, `get_10q_section_data()`
   - Always up-to-date

### Batch Data (Needs Manual Update) 📊
This data is stored in `fundamentals_tall.parquet` and needs periodic updates:

1. **Quarterly Financial Statements**
   - Income Statement, Balance Sheet, Cash Flow
   - Historical data for trend analysis
   - **What gets updated**: New quarterly reports as companies release earnings
   - **When to update**: Monthly or after major earnings seasons

## Solution: Enhanced Manual Trigger

### Current Implementation
- Button exists in dashboard
- Updates single ticker or all tickers
- Shows progress and results

### Enhancements Needed
1. **Better UI**: Make it more prominent and clear
2. **Update All Option**: Easy way to update entire pipeline
3. **Status Display**: Show when data was last updated
4. **Clear Messaging**: Explain what gets updated

## Implementation

### Option 1: Enhance Existing Button (Recommended)
Add an "Update All Data" button next to the existing one.

### Option 2: Add to Settings/Admin Panel
Create a dedicated data management section.

### Option 3: Add Quick Action in Header
Prominent button in the main navigation.

## Free Tier Strategy

### Ephemeral Storage Approach
- ✅ File stored in Railway filesystem (ephemeral)
- ✅ Lost on redeploy (that's okay for experimental phase)
- ✅ Recreated when you click "Update All Data"
- ✅ No cost, stays on free tier

### Workflow
1. **Normal Usage**: Data is available, everything works
2. **After Redeploy**: File is lost, but that's okay
3. **When You Need Fresh Data**: Click "Update All Data" button
4. **File Recreated**: Updates all tickers, creates new file
5. **Ready to Use**: All modules use updated data immediately

### When to Update
- **Before demos**: Ensure latest data is shown
- **After earnings season**: Catch new quarterly reports
- **Monthly**: Keep data reasonably fresh
- **After redeploy**: Recreate the file if needed

## Enhanced Button Implementation

I'll enhance the existing button to:
1. Add "Update All Data" option (updates entire pipeline)
2. Show data freshness status
3. Better progress indicators
4. Clear messaging about what gets updated

## Benefits of This Approach

✅ **Free**: No Railway volume costs
✅ **Simple**: Just click a button when needed
✅ **Flexible**: Update when you want, not on a schedule
✅ **Experimental-Friendly**: Perfect for startup phase
✅ **Real-Time Data Always Works**: Price data, FRED, SEC filings are always current

## Future Migration Path

When ready to move to paid tier:
1. Add Railway Volume ($0.10/month)
2. Set up monthly automation
3. File persists across redeployments
4. Zero manual intervention needed

## Next Steps

1. ✅ Enhance the update button UI
2. ✅ Add "Update All Data" functionality
3. ✅ Show data freshness status
4. ✅ Test the update process
5. ✅ Document the workflow

