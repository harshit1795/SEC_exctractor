# SEC_exctractor

>
   In today's complex and ever-changing business landscape, access to accurate and up-to-date financial information is crucial for making informed decisions. SEC reports, mandated for public companies, contain comprehensive financial statements that shed light on a company's performance, financial health, and strategic direction. Extracting data from these reports can be a time-consuming and daunting task, but the rewards are immense.
   
>
   By developing an automated system that efficiently extracts financial statement data from SEC reports, I've made it easier for businesses and analysts to access and analyze crucial financial information.

## Getting Started

### For Firebase Studio Workspace

1. **Firebase Setup:**
   - Create a Firebase project in the [Firebase console](https://console.firebase.google.com/).
   - In your Firebase project, go to **Authentication** > **Sign-in method** and enable the **Google** provider.
   - Go to your Firebase project settings and create a **Web App**. Copy the `firebaseConfig` object.
   - In your Firebase project settings, go to the **Service accounts** tab and generate a private key file. Rename it to `firebase-credentials.json` and place it in the root of this project.

2. **Configuration:**
   - In `firebase-config.json`, replace the placeholder values with the `firebaseConfig` object you copied from your Firebase project.

3. **First time setup:**
   ```bash
   nix-shell -p python311 --run "python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
   ```

4. **Run the app:**
   ```bash
   nix-shell -p python311 --run "source venv/bin/activate && streamlit run Home.py --server.headless true --server.enableCORS false"
   ```

### For local setup

**Important:** You must run the `settoken.sh` script before each session.

1.  **Set the token:**
    ```bash
    source settoken.sh
    ```
2.  **Run the app:**
    ```bash
    streamlit run Home.py
    ```