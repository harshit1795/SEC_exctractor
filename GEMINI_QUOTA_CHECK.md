# Critical: Check Google Cloud Console Quota Settings

## ⚠️ Important Finding

The error message shows:
```
quota_limit_value: "0"
```

**This is suspicious!** A quota limit of 0 typically means:
1. The quota is disabled
2. The API is not enabled
3. Billing is not set up
4. The project has been suspended

## Immediate Action Required

### Step 1: Check Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
2. Look for: **"GenerateContent requests per minute per project per region"**
3. Check the quota limit value

### Step 2: Enable API (if not enabled)

1. Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
2. Click **"Enable"** if not already enabled

### Step 3: Check Billing

1. Go to: https://console.cloud.google.com/billing
2. Ensure billing is set up (even for free tier)
3. Free tier usually includes 15-60 requests/minute

### Step 4: Request Quota Increase

If quota is 0 or too low:

1. Go to: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
2. Click **"Edit Quotas"** or use: https://cloud.google.com/docs/quotas/help/request_increase
3. Request increase for: **"GenerateContentRequestsPerMinutePerProjectPerRegion"**
4. Request at least 15-30 requests/minute for free tier

### Step 5: Verify API Key

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your API key
3. Ensure it has access to **"Generative Language API"**
4. Check restrictions (if any)

## Expected Quota Limits

- **Free Tier**: 15-60 requests/minute (varies by region)
- **Paid Tier**: Can request higher limits

## After Fixing Quota

1. Wait a few minutes for changes to propagate
2. Test the chatbot again
3. The rate limiter will help prevent future issues

## Rate Limiter Settings

The code now includes a rate limiter set to **15 requests/minute** (conservative).

If your quota is higher, you can adjust in `financial_analyzer.py`:
```python
self.rate_limiter = get_rate_limiter(max_requests=30, window_seconds=60)  # For 30/min quota
```

