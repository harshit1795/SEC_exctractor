# 🚀 SEC Extractor - Saved Rules & Development Guidelines

## 🔧 **Critical Fixes Applied**

### **1. Dependency Management Rules**
- **ALWAYS install packages one by one** if `pip install -r requirements.txt` fails with dependency resolution errors
- **Install core packages first**: `streamlit`, `pandas`, `numpy`
- **Then install specialized packages**: `firebase-admin`, `yfinance`, `google-generativeai`
- **Add missing dependencies** to `requirements.txt` as they're discovered

### **2. Firebase Authentication Rules**
- **NEVER use nested TOML structures** in `.streamlit/secrets.toml` - they cause parsing issues
- **Use individual key-value pairs** for Firebase configuration
- **Prefix all Firebase keys** with `FIREBASE_` for clarity
- **Handle both local and cloud environments** with fallback logic

### **3. Streamlit Configuration Rules**
- **Remove deprecated config options** like `ui.hideSidebarNav`
- **Use proper TOML syntax** with `[section]` headers
- **Set server options** in `[server]` section for cloud deployment
- **Restart Streamlit** after config changes

### **4. Error Handling Rules**
- **Always check for missing packages** when ModuleNotFoundError occurs
- **Verify TOML syntax** when secrets parsing fails
- **Use try-catch blocks** for Firebase initialization
- **Provide fallback authentication** options for demo/testing

## 🚫 **What NOT to Do**

### **1. TOML Configuration**
```toml
# ❌ WRONG - Nested structures cause parsing issues
[firebase_config]
apiKey = "value"
authDomain = "value"

# ✅ CORRECT - Individual key-value pairs
FIREBASE_API_KEY = "value"
FIREBASE_AUTH_DOMAIN = "value"
```

### **2. Firebase Credentials**
```python
# ❌ WRONG - Trying to parse string representations
firebase_creds = st.secrets["firebase_credentials"]

# ✅ CORRECT - Build dictionary from individual values
firebase_creds = {
    "type": st.secrets["FIREBASE_CRED_TYPE"],
    "project_id": st.secrets["FIREBASE_CRED_PROJECT_ID"],
    # ... other fields
}
```

### **3. Package Installation**
```bash
# ❌ WRONG - Can cause dependency resolution issues
pip install -r requirements.txt

# ✅ CORRECT - Install packages individually
pip install streamlit pandas numpy
pip install firebase-admin yfinance
pip install google-generativeai fredapi
```

## ✅ **What ALWAYS Works**

### **1. Local Development Setup**
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install core packages first
pip install streamlit pandas numpy

# 3. Install specialized packages
pip install firebase-admin yfinance google-generativeai

# 4. Run the app
streamlit run Home.py
```

### **2. Firebase Configuration**
```toml
# Individual secrets that always work
FIREBASE_API_KEY = "your_api_key"
FIREBASE_AUTH_DOMAIN = "your_project.firebaseapp.com"
FIREBASE_PROJECT_ID = "your_project_id"
FIREBASE_STORAGE_BUCKET = "your_project.appspot.com"
FIREBASE_MESSAGING_SENDER_ID = "your_sender_id"
FIREBASE_APP_ID = "your_app_id"
FIREBASE_MEASUREMENT_ID = "your_measurement_id"
```

### **3. Error Recovery**
```python
# Always provide fallback options
try:
    # Try to get from Streamlit secrets
    config = st.secrets["FIREBASE_API_KEY"]
except (KeyError, FileNotFoundError):
    # Fallback to local file
    if os.path.exists("firebase-config.json"):
        with open("firebase-config.json") as f:
            config = json.load(f)
    else:
        st.error("Configuration not found")
        st.stop()
```

## 🔍 **Troubleshooting Rules**

### **1. ModuleNotFoundError**
- **Check if package is installed**: `pip list | grep package_name`
- **Install missing package**: `pip install package_name`
- **Add to requirements.txt**: Update file and commit

### **2. TOML Parsing Errors**
- **Check TOML syntax**: Use individual key-value pairs
- **Remove nested structures**: Flatten all configuration
- **Verify quotes**: Ensure proper string formatting

### **3. Firebase Authentication Errors**
- **Check credentials format**: Must be proper dictionary, not string
- **Verify secret names**: Match exactly with code
- **Test locally first**: Ensure Firebase setup works

### **4. Streamlit Configuration Errors**
- **Remove deprecated options**: Check for old config syntax
- **Restart after changes**: Config changes require restart
- **Check logs**: Look for configuration warnings

## 📱 **Deployment Rules**

### **1. Streamlit Cloud**
- **Use individual secrets**: Never nested structures
- **Test locally first**: Ensure app works before deploying
- **Check all dependencies**: Include in requirements.txt
- **Monitor logs**: Watch for runtime errors

### **2. Local vs Cloud**
- **Local**: Use local files (`firebase-config.json`, `firebase-credentials.json`)
- **Cloud**: Use Streamlit secrets (individual key-value pairs)
- **Fallback logic**: Always provide both options

## 🎯 **Success Patterns**

### **1. Working Authentication Flow**
```python
# 1. Initialize Firebase with fallback
firebase_config = init_firebase()

# 2. Render login form with error handling
try:
    user = fb_streamlit_auth(firebase_config)
    if user:
        # Handle successful login
        st.session_state["logged_in"] = True
except Exception as e:
    # Provide fallback options
    st.error(f"Authentication error: {str(e)}")
```

### **2. Robust Configuration Loading**
```python
# Always try secrets first, fallback to files
try:
    config = st.secrets["CONFIG_KEY"]
except:
    config = load_from_local_file()
```

### **3. Comprehensive Error Handling**
```python
# Provide user-friendly error messages
# Include fallback options
# Log errors for debugging
# Guide users to solutions
```

## 📚 **Reference Links**

- **Firebase Admin SDK**: https://firebase.google.com/docs/admin/setup
- **Streamlit Secrets**: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
- **TOML Syntax**: https://toml.io/en/
- **Python Virtual Environments**: https://docs.python.org/3/tutorial/venv.html

---

**Last Updated**: 2025-08-16
**Version**: 1.0
**Status**: All critical issues resolved, app working locally and ready for cloud deployment
