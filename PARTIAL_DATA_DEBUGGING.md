# Partial Data Loading - Debugging Guide

## Issues Identified

### 1. Categories Not Showing in Dashboard
**Symptoms**: Dashboard loads but categories dropdown is empty or shows "No categories available"

**Possible Causes**:
- Fundamentals parquet file not found on Railway
- Fundamentals file exists but doesn't contain Category column
- API returning empty data or 404/500 errors

**Debugging Steps**:
1. Check Railway logs for fundamentals endpoint errors
2. Test the fundamentals API directly:
   ```bash
   curl https://secexctractor-production-80f5.up.railway.app/api/financial/fundamentals/AAPL
   ```
3. Verify `FUNDAMENTALS_PATH` environment variable on Railway
4. Check if fundamentals file exists in Railway filesystem

**Expected Response**:
```json
{
  "ticker": "AAPL",
  "data": [
    {
      "Category": "IncomeStatement",
      "Metric": "Total Revenue",
      "Value": 1234567890,
      "FiscalPeriod": "2025Q1"
    }
  ]
}
```

### 2. Nexus Profiles Not Loading
**Symptoms**: Nexus page loads but profiles don't display, tabs show errors

**Possible Causes**:
- Database not initialized (no UserProfile table)
- Missing `user_id` query parameter
- Database connection issues
- Authentication not working properly

**Debugging Steps**:
1. Check Railway logs for Nexus endpoint errors (500/404)
2. Test Nexus profile endpoint:
   ```bash
   curl "https://secexctractor-production-80f5.up.railway.app/api/nexus/users/USER_ID/profile?user_id=USER_ID"
   ```
3. Verify `DATABASE_URL` is set correctly on Railway
4. Check if database migrations have run
5. Verify user authentication is working

**Expected Response**:
```json
{
  "user_id": "USER_ID",
  "display_name": "User Name",
  "posts_count": 0,
  "friends_count": 0,
  "insights_count": 0
}
```

## Quick Fixes

### Fix 1: Verify Fundamentals File on Railway
1. SSH into Railway or check Railway logs
2. Verify file exists at one of these paths:
   - Path specified in `FUNDAMENTALS_PATH` env var
   - `../fundamentals_tall.parquet` (relative to backend root)
   - `finq-backend/fundamentals_tall.parquet`
3. If file doesn't exist, upload it or set `FUNDAMENTALS_PATH` correctly

### Fix 2: Check Database Initialization
1. Verify `DATABASE_URL` is set on Railway
2. Check if database tables exist (UserProfile, Post, Friend, etc.)
3. Run migrations if needed:
   ```bash
   # On Railway, check if migrations are auto-run or need manual execution
   ```

### Fix 3: Check API Endpoints Directly
Test these endpoints to see what errors they return:

```bash
# Fundamentals
curl https://secexctractor-production-80f5.up.railway.app/api/financial/fundamentals/AAPL

# Nexus Profile (replace USER_ID with actual user ID)
curl "https://secexctractor-production-80f5.up.railway.app/api/nexus/users/USER_ID/profile?user_id=USER_ID"

# Health check
curl https://secexctractor-production-80f5.up.railway.app/api/health
```

## Common Error Codes

- **404**: Resource not found (fundamentals file missing, user not found)
- **500**: Server error (database connection, file read error, missing dependencies)
- **422**: Validation error (missing required parameters)

## Next Steps

1. Check Railway deployment logs for specific error messages
2. Verify all environment variables are set correctly
3. Test API endpoints directly to isolate frontend vs backend issues
4. Check browser console for frontend errors
5. Verify CORS is still configured correctly (should be fixed already)

