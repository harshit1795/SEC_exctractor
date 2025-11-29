# Gemini API Rate Limit Fix

## Problem
Getting 429 "Quota exceeded" errors when using FinQ Bot. The error shows:
- `429 Quota exceeded for quota metric 'Generate Content API requests per minute'`
- Quota limit value is "0" (suspicious - might indicate disabled quota)

## Root Causes

1. **No Rate Limiting**: Multiple requests could hit the API simultaneously
2. **No Retry Logic**: Failed requests weren't retried with backoff
3. **No Request Queuing**: Concurrent requests could exceed limits
4. **Quota Limit = 0**: This suggests the quota might be disabled in Google Cloud Console

## Solutions Implemented

### 1. Rate Limiter Service ✅
Created `finq-backend/app/services/rate_limiter.py`:
- Sliding window rate limiter
- Default: 15 requests per minute (conservative)
- Automatically waits if limit is reached
- Thread-safe with async locks

### 2. Retry Logic with Exponential Backoff ✅
Updated `financial_analyzer.py`:
- Detects 429 rate limit errors
- Retries up to 3 times with exponential backoff (2s, 4s, 8s)
- Waits for rate limiter window before retry
- Better error messages

### 3. Better Error Handling ✅
Updated `chat.py` API endpoint:
- Detects 429 errors specifically
- Returns helpful error messages
- Frontend shows user-friendly rate limit messages

### 4. Frontend Protection ✅
Updated `ChatbotTab.tsx`:
- Better error handling for 429 status
- Prevents duplicate submissions (isLoading check)
- User-friendly error messages

## Configuration

### Rate Limiter Settings
Default: 15 requests per minute (60 second window)

To adjust, modify in `financial_analyzer.py`:
```python
self.rate_limiter = get_rate_limiter(max_requests=15, window_seconds=60)
```

**Recommended Settings:**
- **Free Tier**: 15 requests/minute (current default)
- **Paid Tier**: 30-60 requests/minute (depending on your quota)

### Google Cloud Console Check

**IMPORTANT**: The error shows `quota_limit_value: "0"` which suggests:

1. **Check Quota in Google Cloud Console**:
   - Go to: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
   - Look for: "GenerateContent requests per minute per project per region"
   - Ensure quota is NOT set to 0
   - Default free tier: Usually 15-60 requests/minute

2. **Request Quota Increase** (if needed):
   - Click "Edit Quotas" in Google Cloud Console
   - Request increase for "GenerateContentRequestsPerMinutePerProjectPerRegion"
   - Or use the link from error: https://cloud.google.com/docs/quotas/help/request_increase

3. **Check API Key Permissions**:
   - Ensure API key has access to Generative AI API
   - Check if API is enabled in your project

## How It Works Now

1. **Request Comes In** → Rate limiter checks if under limit
2. **If At Limit** → Waits until oldest request expires (sliding window)
3. **Makes API Call** → With rate limit protection
4. **If 429 Error** → Retries with exponential backoff (2s, 4s, 8s)
5. **Returns Response** → Or helpful error message

## Testing

1. **Test Rate Limiting**:
   - Send multiple rapid requests
   - Should see requests queued/waiting
   - Check logs for "Rate limit reached. Waiting Xs..."

2. **Test Retry Logic**:
   - If you hit a 429, should see retry attempts in logs
   - Should eventually succeed or show clear error

3. **Check Quota**:
   - Verify quota in Google Cloud Console is not 0
   - Ensure API is enabled

## Troubleshooting

### Issue: Still Getting 429 Errors

**Check**:
1. Google Cloud Console → Quotas → Is quota set to 0?
2. Is API enabled in your project?
3. Check Railway logs for rate limiter messages
4. Are multiple instances running? (Each has its own rate limiter)

**Solution**:
- Request quota increase in Google Cloud Console
- Reduce `max_requests` in rate limiter if needed
- Check if multiple Railway deployments are running

### Issue: Quota Limit is 0

**This means**:
- Quota is disabled or not configured
- API might not be enabled
- Billing might not be set up

**Solution**:
1. Enable Generative AI API in Google Cloud Console
2. Set up billing (even for free tier)
3. Request quota allocation
4. Verify API key has proper permissions

## Files Modified

- ✅ `finq-backend/app/services/rate_limiter.py` (new)
- ✅ `finq-backend/app/services/financial_analyzer.py` (updated)
- ✅ `finq-backend/app/api/chat.py` (updated)
- ✅ `finq-frontend/components/dashboard/tabs/ChatbotTab.tsx` (updated)

## Next Steps

1. **Deploy the fixes** to Railway
2. **Check Google Cloud Console** for quota settings
3. **Request quota increase** if needed (link in error message)
4. **Monitor logs** to see rate limiter in action
5. **Test** with multiple rapid requests

## Additional Recommendations

1. **Consider Caching**: Cache common queries to reduce API calls
2. **User Limits**: Add per-user rate limiting if multiple users
3. **Queue System**: For high traffic, consider a proper queue (Redis, etc.)
4. **Monitoring**: Add metrics to track API usage

