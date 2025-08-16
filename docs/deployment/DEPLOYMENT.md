# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites

1. **Firebase Project Setup**
   - Ensure your Firebase project has Google Authentication enabled
   - Create a Web App in Firebase Console
   - Enable Google Sign-In provider

2. **OAuth Client Configuration**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to APIs & Services > Credentials
   - Create or update OAuth 2.0 Client ID for web application
   - Add authorized redirect URIs:
     - `https://your-app-name.streamlit.app/`
     - `http://localhost:8501/` (for local testing)

## Deployment Steps

### 1. Update Streamlit Secrets

In your Streamlit Cloud dashboard, add these secrets:

```toml
# API Keys
OPENROUTER_API_KEY="your_openrouter_key"
GEMINI_API_KEY="your_gemini_key"
FRED_API_KEY="your_fred_key"

# Firebase Configuration
firebase_config = {
    "apiKey": "your_firebase_api_key",
    "authDomain": "your-project.firebaseapp.com",
    "projectId": "your-project-id",
    "storageBucket": "your-project.appspot.com",
    "messagingSenderId": "your_sender_id",
    "appId": "your_app_id",
    "measurementId": "your_measurement_id"
}

# Firebase Service Account Credentials
firebase_credentials = {
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "your_private_key_id",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com",
    "client_id": "your_client_id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/...",
    "universe_domain": "googleapis.com"
}

# OAuth Configuration
oauth = {
    "client_config": {
        "web": {
            "client_id": "your_oauth_client_id.apps.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "your_oauth_client_secret",
            "redirect_uris": [
                "https://your-app-name.streamlit.app/",
                "http://localhost:8501/"
            ]
        }
    }
}
```

### 2. Firebase Console Configuration

1. **Authentication > Sign-in method**
   - Enable Google provider
   - Add authorized domains: `your-app-name.streamlit.app`

2. **Project Settings > General**
   - Copy Web API Key, Auth Domain, Project ID, etc.

3. **Service Accounts**
   - Generate new private key for admin SDK
   - Download JSON file and extract credentials

### 3. Deploy to Streamlit Cloud

1. **Connect Repository**
   - Connect your GitHub repository to Streamlit Cloud
   - Set main file path: `Home.py`
   - Set Python version: 3.9 or higher

2. **Environment Variables**
   - Add all secrets from step 1
   - Ensure proper formatting (no extra quotes)

3. **Deploy**
   - Click "Deploy" button
   - Wait for build to complete
   - Test authentication flow

## Troubleshooting

### Common Issues

1. **"Firebase credentials not found"**
   - Check secrets are properly formatted in Streamlit Cloud
   - Verify all required fields are present

2. **OAuth popup not appearing**
   - Ensure OAuth client ID is correct
   - Check redirect URIs include your Streamlit Cloud URL
   - Verify Google Sign-In is enabled in Firebase

3. **Authentication errors**
   - Check Firebase project settings
   - Verify service account has proper permissions
   - Ensure domain is authorized in Firebase

### Debug Steps

1. **Check Streamlit Cloud logs**
   - Look for authentication errors
   - Verify secrets are loading correctly

2. **Test locally first**
   - Ensure app works with local Firebase config
   - Test OAuth flow locally

3. **Verify Firebase setup**
   - Test Firebase project in Firebase Console
   - Verify Google Sign-In provider is working

## Security Notes

- **Never commit secrets to Git**
- **Use environment variables in production**
- **Regularly rotate API keys**
- **Monitor authentication logs**

## Support

If you continue to have issues:
1. Check Streamlit Cloud documentation
2. Review Firebase Console logs
3. Test with minimal configuration
4. Contact Firebase support if needed
