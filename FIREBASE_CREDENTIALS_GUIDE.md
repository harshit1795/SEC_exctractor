# 🔑 Firebase Credentials Guide for Railway

## ⚠️ Important: Firebase Credentials are **OPTIONAL**

The backend **does NOT require** Firebase credentials to start. The app uses PostgreSQL-based authentication, not Firebase.

`FIREBASE_CREDENTIALS_B64` is only needed if you want to:
- Run the Firestore migration script
- Use Firebase Admin SDK features

**If you're just trying to get the backend running, you can leave `FIREBASE_CREDENTIALS_B64` empty or remove it.**

---

## 📋 If You Need to Set Firebase Credentials

### Step 1: Get Firebase Service Account JSON

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click the **⚙️ Settings** icon → **Project Settings**
4. Go to **Service Accounts** tab
5. Click **"Generate New Private Key"**
6. Click **"Generate Key"** in the confirmation dialog
7. A JSON file will download (e.g., `your-project-firebase-adminsdk-xxxxx.json`)

### Step 2: Base64 Encode the JSON File

**On macOS/Linux:**
```bash
# Replace 'firebase-credentials.json' with your actual file name
base64 -i firebase-credentials.json | tr -d '\n'
```

**On Windows (PowerShell):**
```powershell
# Replace 'firebase-credentials.json' with your actual file name
[Convert]::ToBase64String([IO.File]::ReadAllBytes("firebase-credentials.json"))
```

**Or use an online tool:**
- Go to https://www.base64encode.org/
- Paste the entire contents of your JSON file
- Click "Encode"
- Copy the result

### Step 3: Set in Railway

1. Go to Railway → Your Service → **Variables** tab
2. Find `FIREBASE_CREDENTIALS_B64`
3. Click the **⋮** (three dots) → **Edit**
4. Paste the base64-encoded string (no quotes, no spaces)
5. Click **Save**
6. Redeploy your service

---

## ✅ What the JSON File Looks Like

Your Firebase service account JSON should look like this:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

---

## 🔍 Troubleshooting

### Error: "Failed to decode FIREBASE_CREDENTIALS_B64"
- Make sure you base64-encoded the **entire JSON file**, not just parts of it
- Ensure there are no line breaks or spaces in the base64 string
- Try re-encoding the JSON file

### Error: "Firebase credentials not found"
- This is **normal** if you're not using Firebase features
- The backend will still work without Firebase credentials
- Only set this if you need Firebase Admin SDK features

---

## 🎯 For Your Current 502 Error

**The 502 error is likely NOT related to Firebase credentials.** 

Focus on checking:
1. ✅ `DATABASE_URL` - **This is critical!** Must be set correctly
2. ✅ Railway start command - Should be `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. ✅ Railway logs - Check for actual error messages

Firebase credentials can be left empty for now.

