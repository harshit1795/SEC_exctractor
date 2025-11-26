# Security & Credentials Management

## ⚠️ Important Security Notice

This repository does **NOT** contain any hardcoded API keys, credentials, or sensitive information. All sensitive data is managed through environment variables and configuration files that are excluded from version control.

## Protected Files

The following files and patterns are excluded from version control via `.gitignore`:

### Environment Files
- `.env`
- `.env.*` (all variants)
- `.env.local`
- `.env.production`
- `.env.development`

### Credentials & Keys
- `firebase-credentials.json`
- `*firebase*.json`
- `*google*.json`
- `*credentials*.json`
- `serviceAccount*.json`
- `google-services.json`
- `GoogleService-Info.plist`
- `*.key`
- `*.pem`
- `*.p12`
- `*.pfx`

### Configuration Files
- `.streamlit/secrets.toml`
- `secrets*.toml`
- `secrets*.json`
- `user_prefs.json`
- `settoken.sh`
- `env.txt`

### Database Files
- `*.db`
- `*.sqlite`
- `*.sqlite3`

## Setting Up Environment Variables

### Frontend (Next.js)

1. Copy the example file:
   ```bash
   cd finq-frontend
   cp .env.example .env.local
   ```

2. Fill in your Firebase credentials from Firebase Console:
   - Go to Firebase Console > Project Settings > General
   - Scroll to "Your apps" section
   - Copy the config values to `.env.local`

### Backend (FastAPI)

1. Copy the example file:
   ```bash
   cd finq-backend
   cp .env.example .env
   ```

2. Fill in your configuration:
   - `DATABASE_URL`: Your database connection string
   - `SECRET_KEY`: Generate a random secret key
   - Other API keys as needed

## Firebase Configuration

Firebase credentials are loaded from environment variables in the frontend. The Firebase config object is built from `NEXT_PUBLIC_*` environment variables, which are safe to expose in the browser (they're public by design for Firebase Web SDK).

**Note**: Firebase API keys for web apps are safe to expose publicly. They are restricted by domain and Firebase security rules. However, we still manage them through environment variables for consistency and easy configuration.

## Verifying No Secrets Are Committed

Before pushing to a public repository, verify no secrets are included:

```bash
# Check for potential API keys
grep -r "AIza[0-9A-Za-z_-]\{35\}" --exclude-dir=node_modules --exclude-dir=venv .

# Check for common secret patterns
grep -r "sk-[0-9A-Za-z]\{32,\}" --exclude-dir=node_modules --exclude-dir=venv .

# Verify .gitignore is working
git check-ignore -v .env .env.local firebase-credentials.json
```

## Best Practices

1. **Never commit** `.env` files or credential files
2. **Always use** `.env.example` files as templates
3. **Rotate keys** if accidentally exposed
4. **Use environment variables** for all sensitive configuration
5. **Review** all commits before pushing to public repositories

## Compliance

This repository follows security best practices:
- ✅ No hardcoded credentials
- ✅ All sensitive files in `.gitignore`
- ✅ Environment variables for configuration
- ✅ Example files provided for setup
- ✅ Firebase keys are public-safe (domain-restricted)

