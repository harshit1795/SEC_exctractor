# BYOK (Bring Your Own Key) Implementation Guide

## 📋 Overview

This guide documents the complete implementation of BYOK (Bring Your Own Key) functionality for Google Gemini and FRED API keys in the FinQ application. Users can now add their own API keys through the Settings page, which will be used instead of the global API keys.

## 🎯 Features

### ✅ What's Implemented

1. **Secure API Key Storage**
   - API keys are encrypted using Fernet symmetric encryption
   - Keys are stored in a dedicated `user_api_keys` table
   - Support for both Gemini and FRED API keys

2. **User-Friendly Settings UI**
   - Input fields with show/hide toggle for API keys
   - Visual indicators for key status (set, valid, invalid, not validated)
   - Validate, delete, and update operations for each key
   - Links to obtain API keys from providers

3. **Smart Key Resolution**
   - Backend checks for user-specific keys first
   - Falls back to global keys if user hasn't provided their own
   - Informative error messages when no keys are available

4. **Key Validation**
   - Test API keys with actual service calls
   - Store validation status and timestamp
   - Visual feedback on key validity

## 🏗️ Architecture

### Backend Components

#### 1. Database Model (`finq-backend/app/models/user_api_keys.py`)
```python
class UserAPIKey(Base):
    - id: Primary key
    - user_id: Firebase Auth UID
    - gemini_api_key_encrypted: Encrypted Gemini key
    - fred_api_key_encrypted: Encrypted FRED key
    - gemini_key_last_validated: Validation timestamp
    - fred_key_last_validated: Validation timestamp
    - gemini_key_is_valid: Validation status (bool)
    - fred_key_is_valid: Validation status (bool)
```

#### 2. Encryption Service (`finq-backend/app/services/encryption.py`)
- Uses Fernet symmetric encryption from `cryptography` library
- PBKDF2 key derivation for strong encryption
- Master key from `ENCRYPTION_KEY` environment variable
- Helper methods: `encrypt_api_key()`, `decrypt_api_key()`

#### 3. API Endpoints (`finq-backend/app/api/user_api_keys.py`)
- `GET /api/user-api-keys/status` - Get API keys status (without revealing keys)
- `POST /api/user-api-keys/set` - Set/update an API key
- `POST /api/user-api-keys/validate` - Validate an API key with the service
- `DELETE /api/user-api-keys/delete` - Delete an API key

#### 4. Chat Service Integration (`finq-backend/app/api/chat.py`)
- Modified to check for user-specific keys before using global keys
- Creates per-user `FinancialAnalyzer` instance when custom key is found
- Provides helpful error messages about BYOK when no keys are available

#### 5. Database Migration (`finq-backend/alembic/versions/f7g8h9i0j1k2_create_user_api_keys_table.py`)
- Creates `user_api_keys` table
- Adds indexes for efficient lookup by user_id

### Frontend Components

#### 1. Settings Page (`finq-frontend/app/settings/page.tsx`)
Enhanced with:
- API Keys section with collapsible cards for Gemini and FRED
- Input fields with show/hide password toggle
- Status indicators (has key, validation status, last validated)
- Action buttons (Save, Validate, Delete)
- Loading states and error handling
- Success/error messages with auto-dismiss

#### 2. API Client (`finq-frontend/lib/api.ts`)
New endpoints:
```typescript
- getAPIKeysStatus(userId: string)
- setAPIKey(userId: string, keyType: 'gemini' | 'fred', apiKey: string)
- validateAPIKey(userId: string, keyType: 'gemini' | 'fred')
- deleteAPIKey(userId: string, keyType: 'gemini' | 'fred')
```

## 🚀 Deployment Guide

### Step 1: Backend Environment Variables

Add to your Render environment variables:

```bash
# Required: Encryption key for securing user API keys
ENCRYPTION_KEY=your-secure-encryption-key-here

# Optional: Global fallback keys (can be removed if all users provide their own)
GEMINI_API_KEY=your-global-gemini-key (optional)
FRED_API_KEY=your-global-fred-key (optional)
```

**Generating an Encryption Key:**
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### Step 2: Run Database Migration

The migration will run automatically on startup (in `main.py`), but you can manually run it:

```bash
cd finq-backend
alembic upgrade head
```

### Step 3: Deploy Backend

1. Commit changes to your repository
2. Push to your deployment branch
3. Render will automatically deploy the updated backend
4. Verify the new endpoints in Swagger docs: `https://your-backend-url.com/docs`

### Step 4: Deploy Frontend

1. Commit changes to your repository
2. Push to your deployment branch
3. Vercel will automatically deploy the updated frontend
4. Verify the Settings page shows the new API Keys section

### Step 5: Test the Feature

1. Sign in to your application
2. Navigate to Settings
3. Add a Gemini API key
4. Click "Validate Key" to test it
5. Try using the AI chat feature - it should use your key!

## 🔒 Security Considerations

### Encryption
- All API keys are encrypted at rest using Fernet symmetric encryption
- Master encryption key is stored as an environment variable
- Keys are only decrypted when needed for API calls
- Decrypted keys are never exposed to the frontend

### Best Practices
1. **Encryption Key**: Use a strong, randomly generated encryption key
2. **Key Rotation**: Consider rotating the encryption key periodically (requires re-encrypting all keys)
3. **Access Control**: Only authenticated users can access their own keys
4. **Audit Logging**: Consider adding audit logs for key operations (future enhancement)
5. **Rate Limiting**: Consider adding rate limits to prevent abuse (future enhancement)

## 📚 User Guide

### For End Users

#### How to Add Your API Key

1. **Navigate to Settings**
   - Click on your profile icon
   - Select "Settings"

2. **Scroll to API Keys Section**
   - Find "API Keys (Bring Your Own Key)"

3. **Add Gemini API Key**
   - Click on the Gemini API key section
   - Enter your API key
   - Click "Save Gemini Key"
   - (Optional) Click "Validate Key" to test it

4. **Add FRED API Key** (Optional)
   - Same process as Gemini key

#### How to Get API Keys

**Google Gemini:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in FinQ Settings

**FRED API:**
1. Visit [FRED API Key Request](https://fred.stlouisfed.org/docs/api/api_key.html)
2. Create a free account
3. Request an API key
4. Copy the key and paste it in FinQ Settings

#### Key Validation

- **Green checkmark**: Your key is valid and working
- **Red X**: Your key is invalid or has issues
- **Gray "Not validated"**: You haven't validated the key yet

## 🔧 Configuration Options

### Backend Configuration

In `finq-backend/app/config.py`:

```python
class Settings(BaseSettings):
    # ... other settings ...
    
    # API Keys (now optional - users can provide their own)
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    fred_api_key: str = Field(default="", env="FRED_API_KEY")
    
    # Encryption key for BYOK
    encryption_key: str = Field(default="", env="ENCRYPTION_KEY")
```

### Environment Variables Priority

1. **User-specific key** (from database) - Highest priority
2. **Global key** (from environment variable) - Fallback
3. **No key** - Returns error with instructions to add key in Settings

## 🐛 Troubleshooting

### Issue: "Failed to save API key"

**Cause**: Encryption service not properly initialized or invalid encryption key

**Solution**:
1. Verify `ENCRYPTION_KEY` is set in environment variables
2. Check backend logs for encryption errors
3. Generate a new encryption key if needed

### Issue: "API key validation failed"

**Cause**: Invalid API key or service is down

**Solution**:
1. Verify the API key is correct
2. Check if you've copied the entire key (no spaces)
3. Try generating a new API key from the provider
4. Check if the service (Gemini/FRED) is operational

### Issue: "No API key configured"

**Cause**: Neither user-specific nor global key is available

**Solution**:
1. Add your own API key in Settings
2. Or ask administrator to set global keys in Render

## 📈 Future Enhancements

Potential improvements for the BYOK feature:

1. **Key Usage Analytics**
   - Track API call counts per user
   - Show usage statistics in Settings
   - Notify users when approaching quota limits

2. **Multiple Keys Support**
   - Support multiple keys per service
   - Automatic failover between keys
   - Load balancing across keys

3. **Key Sharing**
   - Allow teams to share API keys
   - Organization-level key management

4. **Enhanced Security**
   - Key rotation policies
   - Automatic key expiration
   - Two-factor authentication for key operations

5. **Audit Logging**
   - Log all key operations (create, update, delete)
   - Track key validation attempts
   - Alert on suspicious activity

## 📝 Migration Notes

### For Existing Deployments

1. **Backup**: Create database backup before migration
2. **Encryption Key**: Generate and set `ENCRYPTION_KEY` before deploying
3. **Global Keys**: Existing global keys will continue to work as fallback
4. **User Notification**: Inform users about the new BYOK feature

### Rollback Plan

If issues arise, you can rollback by:

1. Revert code changes
2. Optionally drop the `user_api_keys` table:
   ```sql
   DROP TABLE user_api_keys;
   ```
3. Redeploy previous version

## ✅ Testing Checklist

- [ ] Backend migration runs successfully
- [ ] API endpoints are accessible in Swagger docs
- [ ] Settings page loads without errors
- [ ] Can save a Gemini API key
- [ ] Can validate a Gemini API key
- [ ] Can delete a Gemini API key
- [ ] Can save a FRED API key
- [ ] Can validate a FRED API key
- [ ] Can delete a FRED API key
- [ ] Chat uses user-specific key when available
- [ ] Chat falls back to global key when user hasn't provided one
- [ ] Error messages are clear and helpful
- [ ] Keys are encrypted in database (verify manually)

## 📞 Support

For issues or questions:

1. Check backend logs in Render dashboard
2. Check browser console for frontend errors
3. Verify environment variables are set correctly
4. Test endpoints in Swagger docs (`/docs`)

---

**Implementation Date**: February 3, 2026  
**Status**: ✅ Complete and ready for deployment  
**Version**: 1.0.0
