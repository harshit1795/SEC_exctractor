# Gemini CLI - Project Context

This document provides critical instructions for developing, troubleshooting, and executing the SEC Extractor application. It is intended to be a living document, updated as the project evolves, to ensure that context is maintained across multiple Gemini CLI sessions.

## Project Overview

The SEC Extractor is a tool designed to automate the extraction of financial statement data from SEC reports. The goal is to make it easier for businesses and analysts to access and analyze crucial financial information from public companies.

## Key Technologies

*   **Backend:** Python
*   **Frontend:** Streamlit
*   **Authentication:** Firebase Authentication (Google Provider)
*   **Database:** Firebase
*   **Environment Management:** nix-shell, venv

## Development Workflow

### Firebase Studio Workspace Setup

1.  **Firebase Setup:**
    *   Create a Firebase project.
    *   Enable Google Authentication.
    *   Create a Web App and copy the `firebaseConfig` object.
    *   Generate a private key file, rename it to `firebase-credentials.json`, and place it in the project root.

2.  **Configuration:**
    *   Update `.streamlit/secrets.toml` with your Firebase service account credentials and Web App config.
    *   Add your Google OAuth client config to `.streamlit/secrets.toml`.

3.  **First-time setup:**
    ```bash
    nix-shell -p python311 --run "python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    ```

4.  **Run the app:**
    ```bash
    nix-shell -p python311 --run "source venv/bin/activate && streamlit run Home.py --server.headless true --server.enableCORS false"
    ```

### Local Setup

1.  **Run the app:**
    To ensure only one instance of the app is running, use the following command to kill all existing Streamlit processes:
    ```bash
    pkill -f streamlit
    source settoken.sh && streamlit run Home.py &
    ```

## Architectural Principles

*   **Multi-page Streamlit Application:** The application is structured as a multi-page Streamlit app.
*   **Entry Point:** `Home.py` serves as the main entry point and handles page routing.
*   **Authentication:** User authentication is managed through `st.session_state` and the `login.py` page.
*   **Modular Pages:** Each distinct feature or section of the application is encapsulated in its own Python file within the `pages/` directory.
*   **Navigation:** A sidebar is used for primary navigation between the different application pages.

## File Structure

*   `Home.py`: Main application entry point and router.
*   `login.py`: Handles user authentication.
*   `pages/`: Contains the individual pages of the application.
*   `.streamlit/`: Configuration files for Streamlit, including secrets.
*   `assets/`: Static assets like logos and images.
*   `requirements.txt`: Python dependencies.
*   `firebase-credentials.json`: Firebase service account credentials.

## Deployment

The application is deployed using Firebase Hosting. The deployment process is not yet documented.


## Critical Files

*   `.streamlit/secrets.toml`: Contains Firebase and OAuth configurations.
*   `firebase-credentials.json`: Firebase service account credentials.
*   `requirements.txt`: Python dependencies.
*   `Home.py`: The main Streamlit application file.
*   `settoken.sh`: Script for local development session setup.

## Memory and Session Log

This section is a living memory to speed up future sessions. Append new entries at the top with date/time and concise notes on what changed or what to try next.

### 2025-08-11

- Repo scan summary
  - Entry point: Home.py (Streamlit multi-page app). Pages under pages/ include Dashboard, Financial_Health_Monitoring, Nexus, Settings. Common sidebar logic in components/shared.py. Auth/init in login.py and auth.py.
  - Data assets expected locally: fundamentals_tall.parquet, sp500_fundamentals.csv, assets/logos/{TICKER}.png.
  - External services: Firebase Admin (service account) and Firebase Web App config (firebase-config.json or Streamlit secrets). Optional OAuth client config in .streamlit/secrets.toml.
  - API usage: yfinance, FRED (via fred_data.py), Google Generative AI (google-generativeai). API keys can be loaded from .streamlit/secrets.toml by auth.load_api_keys().
  - Important: settoken.sh contains hard-coded API keys for OpenRouter, Gemini, and FRED. Prefer moving these into .streamlit/secrets.toml and removing secrets from VCS.

- Run notes
  - Local quick start (assuming Python env ready):
    1) Optional: source settoken.sh (or set env vars via secrets).
    2) pip install -r requirements.txt
    3) streamlit run Home.py
  - Firebase requirements: Place firebase-credentials.json and firebase-config.json in repo root OR configure .streamlit/secrets.toml with firebase_credentials and firebase_config blocks, plus oauth.client_config if needed.
  - Verified dependencies import in this environment (pandas, streamlit, firebase_admin, yfinance, altair, google-generativeai, google-auth-oauthlib): all OK.
  - Attempted headless run: streamlit run Home.py --server.headless true --server.port 8888. Observed warning "ui.hideSidebarNav is not a valid config option" from .streamlit/config.toml. App otherwise started without immediate errors before timeout.

- Observations for Dashboard page
  - Loads fundamentals_tall.parquet and sp500_fundamentals.csv; provides filters and basic header UI. Tabs are defined but content is not implemented yet (up to tab creation as of line ~115). Add tab bodies in a later iteration.

- Next steps
  - Implement tab contents in pages/Dashboard.py (metrics trend charts, snapshot KPIs, earnings summary, price chart with Altair, FRED macro overlays, and a simple chat using google-generativeai if API key present).
  - Harden secrets management: remove plaintext keys from settoken.sh and rely on Streamlit secrets and/or environment variables. Audit README for formatting and completeness (code block fencing) and add Firebase Hosting deployment steps.
  - Add a .streamlit/secrets.toml.example template showing required keys.
  - Update .streamlit/config.toml to remove deprecated [ui] hideSidebarNav config; use CSS-based hiding already implemented in components.shared.hide_default_sidebar().

## Practical Runbook

- One-time setup
  - python3 -m venv venv && source venv/bin/activate
  - pip install -r requirements.txt
  - Provide credentials: either add .streamlit/secrets.toml or drop firebase-credentials.json and firebase-config.json in repo root.

- Daily workflow
  - source venv/bin/activate
  - Optional: source settoken.sh (only if not using secrets.toml)
  - streamlit run Home.py

- Troubleshooting tips
  - If Streamlit shows Firebase credential errors, verify .streamlit/secrets.toml or the firebase-credentials.json file exists and is valid.
  - If no logos appear, ensure assets/logos/{TICKER}.png exists or adjust get_logo_path in Dashboard.
  - If data files are missing, regenerate fundamentals_tall.parquet and sp500_fundamentals.csv or point to correct paths.
