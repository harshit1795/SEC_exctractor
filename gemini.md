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
    nix-shell -p python311 --run "source venv/bin/activate && streamlit run login.py --server.headless true --server.enableCORS false"
    ```

### Local Setup

1.  **Run the app:**
    To ensure only one instance of the app is running, use the following command to kill all existing Streamlit processes:
    ```bash
    pkill -f streamlit
    source settoken.sh && streamlit run login.py &
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
