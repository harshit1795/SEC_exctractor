# SEC_exctractor

>
   In today's complex and ever-changing business landscape, access to accurate and up-to-date financial information is crucial for making informed decisions. SEC reports, mandated for public companies, contain comprehensive financial statements that shed light on a company's performance, financial health, and strategic direction. Extracting data from these reports can be a time-consuming and daunting task, but the rewards are immense.
   
>
   By developing an automated system that efficiently extracts financial statement data from SEC reports, I've made it easier for businesses and analysts to access and analyze crucial financial information.

## Getting Started

This guide will walk you through setting up the application for both local development and cloud deployment.

### 1. Firebase Project Setup

1.  **Create a Firebase Project:** Go to the [Firebase Console](https://console.firebase.google.com/) and create a new project.
2.  **Enable Google Authentication:** In your Firebase project, go to **Authentication** > **Sign-in method** and enable the **Google** provider.
3.  **Create a Web App:** In your project settings, create a new **Web App** and take note of the `firebaseConfig` values.
4.  **Generate a Private Key:** In project settings, go to the **Service accounts** tab and generate a new private key for the Admin SDK. This will download a JSON file.

### 2. Configure Streamlit Secrets

Create a file named `secrets.toml` in a `.streamlit` directory in the project root (`.streamlit/secrets.toml`). This file will manage all your credentials for both local and cloud environments.

Populate it with the following keys, using the values from your Firebase project and the JSON file you downloaded:

```toml
# Firebase Web App Configuration
FIREBASE_API_KEY = "your_api_key_from_web_app_config"
FIREBASE_AUTH_DOMAIN = "your_auth_domain_from_web_app_config"
FIREBASE_PROJECT_ID = "your_project_id"
FIREBASE_STORAGE_BUCKET = "your_storage_bucket"
FIREBASE_MESSAGING_SENDER_ID = "your_messaging_sender_id"
FIREBASE_APP_ID = "your_app_id"
FIREBASE_MEASUREMENT_ID = "your_measurement_id"

# Firebase Service Account Credentials (from the downloaded JSON file)
FIREBASE_CRED_TYPE = "service_account"
FIREBASE_CRED_PROJECT_ID = "your_project_id"
FIREBASE_CRED_PRIVATE_KEY_ID = "your_private_key_id"
FIREBASE_CRED_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\n...your_private_key...\n-----END PRIVATE KEY-----\n"
FIREBASE_CRED_CLIENT_EMAIL = "your_client_email"
FIREBASE_CRED_CLIENT_ID = "your_client_id"
FIREBASE_CRED_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
FIREBASE_CRED_TOKEN_URI = "https://oauth2.googleapis.com/token"
FIREBASE_CRED_AUTH_PROVIDER_X509_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"
FIREBASE_CRED_CLIENT_X509_CERT_URL = "your_client_x509_cert_url"
FIREBASE_CRED_UNIVERSE_DOMAIN = "googleapis.com"

# Other API Keys
GEMINI_API_KEY="your_gemini_key"
FRED_API_KEY="your_fred_key"
```

**Important:** The `FIREBASE_CRED_PRIVATE_KEY` must have its newline characters preserved. Copy the entire key from the JSON file, including the `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----` lines, and paste it inside the quotes.

### 3. Install Dependencies

It is recommended to use a Python virtual environment.

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run Home.py
```
The application should now be running locally at `http://localhost:8501`.

