# ⚡ SEC Extractor - Quick Reference Guide

## 🚀 **Fast Start Commands**

### **1. Start the App**
```bash
# Activate virtual environment
source venv/bin/activate

# Run the app
streamlit run Home.py

# Access the app
open http://localhost:8501
```

### **2. Install Missing Packages**
```bash
# Core packages
pip install streamlit pandas numpy

# Firebase & Authentication
pip install firebase-admin fb-streamlit-auth

# Financial data
pip install yfinance tabulate lxml html5lib

# AI & APIs
pip install google-generativeai fredapi google-auth-oauthlib
```

### **3. Restart After Changes**
```bash
# Kill all Streamlit processes
pkill -f streamlit

# Clear cache
rm -rf __pycache__ pages/__pycache__ components/__pycache__

# Restart
streamlit run Home.py
```

## 🔧 **Quick Fixes**

### **1. ModuleNotFoundError**
```bash
# Check what's missing
pip list | grep package_name

# Install missing package
pip install package_name

# Add to requirements.txt
echo "package_name" >> requirements.txt
```

### **2. TOML Parsing Errors**
```toml
# ❌ WRONG - Nested structures
[firebase_config]
apiKey = "value"

# ✅ CORRECT - Individual keys
FIREBASE_API_KEY = "value"
FIREBASE_AUTH_DOMAIN = "value"
```

### **3. Firebase Credentials Issues**
```python
# ❌ WRONG - String parsing
creds = st.secrets["firebase_credentials"]

# ✅ CORRECT - Build dictionary
creds = {
    "type": st.secrets["FIREBASE_CRED_TYPE"],
    "project_id": st.secrets["FIREBASE_CRED_PROJECT_ID"],
    # ... other fields
}
```

## 📱 **Streamlit Cloud Setup**

### **1. Secrets Format**
```toml
# API Keys
OPENROUTER_API_KEY = "your_key"
GEMINI_API_KEY = "your_key"
FRED_API_KEY = "your_key"

# Firebase Config
FIREBASE_API_KEY = "your_firebase_api_key"
FIREBASE_AUTH_DOMAIN = "your_project.firebaseapp.com"
FIREBASE_PROJECT_ID = "your_project_id"
FIREBASE_STORAGE_BUCKET = "your_project.appspot.com"
FIREBASE_MESSAGING_SENDER_ID = "your_sender_id"
FIREBASE_APP_ID = "your_app_id"
FIREBASE_MEASUREMENT_ID = "your_measurement_id"

# Firebase Credentials
FIREBASE_CRED_TYPE = "service_account"
FIREBASE_CRED_PROJECT_ID = "your_project_id"
FIREBASE_CRED_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CRED_CLIENT_EMAIL = "firebase-adminsdk-xxx@your_project.iam.gserviceaccount.com"
FIREBASE_CRED_CLIENT_ID = "your_client_id"
FIREBASE_CRED_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
FIREBASE_CRED_TOKEN_URI = "https://oauth2.googleapis.com/token"
FIREBASE_CRED_AUTH_PROVIDER_X509_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"
FIREBASE_CRED_CLIENT_X509_CERT_URL = "https://www.googleapis.com/robot/v1/metadata/x509/..."
FIREBASE_CRED_UNIVERSE_DOMAIN = "googleapis.com"
```

### **2. OAuth Setup**
```bash
# 1. Go to Google Cloud Console
# 2. APIs & Services > Credentials
# 3. Create OAuth 2.0 Client ID
# 4. Add redirect URIs:
#    - https://your-app-name.streamlit.app/
#    - http://localhost:8501/
```

## 🐛 **Common Error Solutions**

### **1. "ui.hideSidebarNav is not a valid config option"**
```toml
# Remove from .streamlit/config.toml
# [ui]
# hideSidebarNav = true

# Use CSS-based hiding instead
```

### **2. "Found invalid character in key name: ':'"**
```toml
# ❌ WRONG
firebase_config = {
    "apiKey": "value"
}

# ✅ CORRECT
FIREBASE_API_KEY = "value"
```

### **3. "Invalid certificate argument"**
```python
# Build credentials dictionary manually
firebase_creds = {
    "type": st.secrets["FIREBASE_CRED_TYPE"],
    "project_id": st.secrets["FIREBASE_CRED_PROJECT_ID"],
    # ... build complete dictionary
}
```

### **4. "Missing optional dependency 'tabulate'"**
```bash
pip install tabulate lxml html5lib
```

## 📊 **Status Check Commands**

### **1. App Status**
```bash
# Check if app is running
ps aux | grep streamlit

# Check port usage
lsof -i :8501

# Test app response
curl -s http://localhost:8501 | head -10
```

### **2. Package Status**
```bash
# List installed packages
pip list

# Check specific package
pip show package_name

# Check virtual environment
which python
```

### **3. Configuration Status**
```bash
# Check Streamlit config
cat .streamlit/config.toml

# Check secrets (don't commit this!)
cat .streamlit/secrets.toml

# Check requirements
cat requirements.txt
```

## 🔄 **Development Workflow**

### **1. Make Changes**
```bash
# Edit files
code Home.py
code login.py
code .streamlit/secrets.toml
```

### **2. Test Changes**
```bash
# Restart app
pkill -f streamlit
streamlit run Home.py

# Check logs
tail -f streamlit.log
```

### **3. Deploy Changes**
```bash
# Commit changes
git add .
git commit -m "Fix: [description of fix]"

# Push to GitHub
git push origin main

# Deploy on Streamlit Cloud (automatic)
```

## 📚 **File Locations**

### **1. Core Application**
- **Main App**: `Home.py`
- **Authentication**: `login.py`
- **Shared Components**: `components/shared.py`
- **Pages**: `pages/Dashboard.py`, `pages/Nexus.py`, etc.

### **2. Configuration**
- **Streamlit Config**: `.streamlit/config.toml`
- **Secrets**: `.streamlit/secrets.toml`
- **Requirements**: `requirements.txt`
- **Firebase Config**: `firebase-config.json`
- **Firebase Credentials**: `firebase-credentials.json`

### **3. Documentation**
- **Project Context**: `gemini.md`
- **Deployment Guide**: `DEPLOYMENT.md`
- **Development Rules**: `SAVED_RULES.md`
- **Session Memory**: `PROJECT_MEMORIES.md`
- **Quick Reference**: `QUICK_REFERENCE.md` (this file)

## 🆘 **Emergency Commands**

### **1. Complete Reset**
```bash
# Kill all processes
pkill -f streamlit

# Clear all cache
rm -rf __pycache__ pages/__pycache__ components/__pycache__

# Remove virtual environment
rm -rf venv

# Recreate environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **2. Fallback to Local Files**
```bash
# If Streamlit secrets fail, ensure local files exist
ls -la firebase-config.json
ls -la firebase-credentials.json

# Copy from backup if needed
cp backup/firebase-config.json .
cp backup/firebase-credentials.json .
```

### **3. Debug Mode**
```bash
# Run with verbose logging
streamlit run Home.py --logger.level=debug

# Check detailed logs
tail -f streamlit.log
```

---

**Last Updated**: 2025-08-16
**Purpose**: Quick access to common commands and solutions
**For Detailed Info**: See `SAVED_RULES.md` and `PROJECT_MEMORIES.md`
