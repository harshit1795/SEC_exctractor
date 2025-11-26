# 📊 Data Pipeline Documentation

## Overview

The Data Pipeline service automatically fetches and updates financial fundamentals data from Yahoo Finance. It keeps your `fundamentals_tall.parquet` file up-to-date with the latest quarterly financial statements.

---

## 🚀 Features

- **Automatic Data Fetching**: Fetches quarterly financial data (Income Statement, Balance Sheet, Cash Flow) from Yahoo Finance
- **Incremental Updates**: Only adds new data, doesn't duplicate existing records
- **Smart Merging**: Automatically handles duplicate records and keeps the latest data
- **Batch Updates**: Update multiple tickers at once
- **Status Monitoring**: Check latest periods and data freshness

---

## 📡 API Endpoints

### 1. **Update Single Ticker**
```http
POST /api/data-pipeline/update/{ticker}?force_refresh=false
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/data-pipeline/update/AAPL"
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully updated data for AAPL",
  "ticker": "AAPL",
  "new_records": 450,
  "existing_records": 1200,
  "total_records": 1650,
  "file_path": "/path/to/fundamentals_tall.parquet"
}
```

---

### 2. **Update Latest Data (Smart Update)**
```http
POST /api/data-pipeline/update-latest
```

Updates all tickers that have data, fetching the latest quarters.

**Example:**
```bash
curl -X POST "http://localhost:8000/api/data-pipeline/update-latest"
```

**Response:**
```json
{
  "message": "Latest data update completed",
  "total_tickers": 9,
  "updated": 8,
  "failed": 1,
  "results": [...]
}
```

---

### 3. **Batch Update**
```http
POST /api/data-pipeline/update-batch
Content-Type: application/json

{
  "tickers": ["AAPL", "MSFT", "GOOGL"]
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/data-pipeline/update-batch" \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "MSFT"]}'
```

---

### 4. **Get Data Status**
```http
GET /api/data-pipeline/status?ticker=AAPL
```

**Example:**
```bash
curl "http://localhost:8000/api/data-pipeline/status?ticker=AAPL"
```

**Response:**
```json
{
  "latest_period": "2025Q1",
  "ticker_periods": {
    "AAPL": {
      "latest": "2025Q1",
      "all_periods": ["2023Q1", "2023Q2", "2023Q3", "2023Q4", "2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1"],
      "count": 9
    }
  },
  "total_records": 1650,
  "total_tickers": 9
}
```

---

## 🎯 Frontend Usage

### Update Button Component

The dashboard now includes an "Update Data" button that:
- Shows the latest period in the data
- Allows one-click updates for the current ticker
- Displays update progress and results

**Location**: Top-right of the dashboard, next to the company header

---

## 🔧 How It Works

### Data Flow

1. **Fetch**: Queries Yahoo Finance for quarterly financial statements
   - Income Statement (`quarterly_financials`)
   - Balance Sheet (`quarterly_balance_sheet`)
   - Cash Flow (`quarterly_cashflow`)

2. **Transform**: Converts wide format (metrics × periods) to long format
   - Each row: `Ticker | FiscalPeriod | Metric | Value | Category | PeriodEnd`

3. **Merge**: Combines with existing data
   - Removes duplicates (same Ticker + FiscalPeriod + Metric + Category)
   - Keeps the latest data

4. **Save**: Updates `fundamentals_tall.parquet` file

---

## 📋 Data Format

The pipeline maintains the same format as `build_fundamentals_tall.py`:

| Column | Type | Description |
|--------|------|-------------|
| `Ticker` | string | Stock ticker symbol |
| `FiscalPeriod` | string | Quarter label (e.g., "2025Q1") |
| `Metric` | string | Financial metric name |
| `Value` | float | Metric value |
| `Category` | string | IncomeStatement, BalanceSheet, or CashFlow |
| `PeriodEnd` | date | Period end date |

---

## ⚙️ Configuration

### File Location

The pipeline automatically finds `fundamentals_tall.parquet` in:
1. Path specified in `FUNDAMENTALS_PATH` env variable
2. Project root: `../fundamentals_tall.parquet` (relative to backend)
3. Backend directory: `fundamentals_tall.parquet`

### Rate Limiting

- Default delay: 0.5 seconds between ticker requests
- Adjustable in `update_all_tickers()` method

---

## 🧪 Testing

### Test Single Ticker Update
```bash
# Update AAPL data
curl -X POST "http://localhost:8000/api/data-pipeline/update/AAPL"

# Check status
curl "http://localhost:8000/api/data-pipeline/status?ticker=AAPL"
```

### Test Batch Update
```bash
curl -X POST "http://localhost:8000/api/data-pipeline/update-batch" \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "MSFT"]}'
```

---

## 🐛 Troubleshooting

### Issue: "No data fetched for {ticker}"

**Possible Causes:**
- Yahoo Finance API rate limiting
- Invalid ticker symbol
- Network connectivity issues

**Solutions:**
- Wait a few minutes and retry
- Verify ticker symbol is correct
- Check internet connection

### Issue: "Fundamentals file not found"

**Solution:**
- Ensure `fundamentals_tall.parquet` exists in project root
- Or set `FUNDAMENTALS_PATH` in `.env`

### Issue: Data not updating in frontend

**Solution:**
- Click the "Update Data" button in the dashboard
- Or refresh the page after backend update
- Check browser console for errors

---

## 🔄 Scheduled Updates (Future)

For production, you can set up scheduled updates using:

1. **Cron Job** (Linux/Mac):
   ```bash
   # Update daily at 2 AM
   0 2 * * * curl -X POST http://localhost:8000/api/data-pipeline/update-latest
   ```

2. **Python Schedule**:
   ```python
   import schedule
   import requests
   
   def update_data():
       requests.post("http://localhost:8000/api/data-pipeline/update-latest")
   
   schedule.every().day.at("02:00").do(update_data)
   ```

3. **Railway Cron Jobs**: Use Railway's cron job feature for cloud deployments

---

## 📝 Notes

- **Data Freshness**: Financial data is typically updated quarterly after earnings reports
- **Storage**: The parquet file grows with each update. Monitor file size.
- **Backup**: Consider backing up `fundamentals_tall.parquet` before large batch updates
- **Performance**: Batch updates can take time (0.5s per ticker + fetch time)

---

## ✅ Next Steps

1. **Test the Update Button**: Click "Update Data" in the dashboard
2. **Check Latest Period**: Verify new quarters appear after update
3. **Monitor Status**: Use `/api/data-pipeline/status` to check data freshness
4. **Set Up Automation**: Configure scheduled updates for production

---

**The data pipeline is now ready to keep your financial data up-to-date!** 🎉

