# Metric Preferences Fix - Per Ticker Storage

## Problem
When selecting metrics for a ticker (e.g., AAPL) and clicking "Update Preference", then switching to another ticker (e.g., MSFT) and coming back to AAPL, the metric selections were lost.

## Root Cause
The preferences were stored by category only, not by ticker. So when you selected metrics for AAPL's "IncomeStatement" category, it saved globally for that category. When you switched to MSFT, it used the same saved preferences, overwriting AAPL's selections.

## Solution
Updated the preferences system to store metrics per ticker AND category:

**Old Structure:**
```typescript
{
  "IncomeStatement": ["Revenue", "Net Income"],
  "BalanceSheet": ["Assets"]
}
```

**New Structure:**
```typescript
{
  "AAPL": {
    "IncomeStatement": ["Revenue", "Net Income"],
    "BalanceSheet": ["Assets"]
  },
  "MSFT": {
    "IncomeStatement": ["Total Revenue", "Operating Income"],
    "BalanceSheet": ["Total Assets"]
  }
}
```

## Changes Made

### 1. Updated `useMetricPreferences` Hook
- ✅ Changed interface to store preferences per ticker
- ✅ Updated all functions to accept `ticker` parameter
- ✅ Added migration logic for old format (converts to new format)
- ✅ Functions now: `getMetricsForCategory(ticker, category)`, `setMetricsForCategory(ticker, category, metrics)`

### 2. Updated TrendTab Component
- ✅ All preference calls now include `ticker` parameter
- ✅ Preferences are saved per ticker + category combination
- ✅ When switching tickers, each ticker's preferences are loaded independently

### 3. Updated SnapshotTab Component
- ✅ All preference calls now include `ticker` parameter
- ✅ Same ticker-specific behavior as TrendTab

## How It Works Now

1. **Select metrics for AAPL** → Saves to `preferences["AAPL"]["IncomeStatement"]`
2. **Switch to MSFT** → Loads from `preferences["MSFT"]["IncomeStatement"]` (empty, so shows defaults)
3. **Select metrics for MSFT** → Saves to `preferences["MSFT"]["IncomeStatement"]`
4. **Switch back to AAPL** → Loads from `preferences["AAPL"]["IncomeStatement"]` (your original selections!)

## Migration
The hook includes automatic migration:
- Old format preferences are detected
- They're cleared (user can re-save if needed)
- New format is used going forward

## Testing
1. Select metrics for AAPL in TrendTab
2. Click "Update Preference"
3. Switch to MSFT
4. Select different metrics for MSFT
5. Switch back to AAPL
6. ✅ Your original AAPL selections should be restored!

## Files Modified
- ✅ `finq-frontend/lib/hooks/useMetricPreferences.ts`
- ✅ `finq-frontend/components/dashboard/tabs/TrendTab.tsx`
- ✅ `finq-frontend/components/dashboard/tabs/SnapshotTab.tsx`

