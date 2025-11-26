# ⚠️ CRITICAL SECURITY NOTICE

## Exposed Credentials Found

The following files contain **EXPOSED API KEYS AND CREDENTIALS**:

1. **`settoken.sh`** - Contains:
   - OPENROUTER_API_KEY
   - GEMINI_API_KEY (2 instances)
   - FRED_API_KEY

2. **`user_prefs.json`** - Contains:
   - GEMINI_API_KEY
   - POLYGON_API_KEY

3. **`env.txt`** - Contains:
   - AWS_ACCESS_KEY
   - AWS_SECRET_KEY
   - Other AWS configuration

## ⚠️ IMMEDIATE ACTION REQUIRED

### 1. Rotate All Exposed Keys

**If these files have been committed to git history, you MUST:**

1. **Rotate all exposed API keys immediately:**
   - Generate new GEMINI_API_KEY from Google Cloud Console
   - Generate new FRED_API_KEY from FRED API website
   - Generate new POLYGON_API_KEY from Polygon.io
   - Generate new OPENROUTER_API_KEY from OpenRouter
   - Generate new AWS credentials from AWS IAM

2. **Remove sensitive data from git history** (if already committed):
   ```bash
   # Use git filter-branch or BFG Repo-Cleaner to remove these files from history
   # Or consider creating a new repository without the history
   ```

3. **Verify files are in .gitignore:**
   ```bash
   git check-ignore -v settoken.sh user_prefs.json env.txt
   ```

### 2. Clean Up Local Files

These files should be:
- ✅ Already in `.gitignore` (verified)
- ❌ **NEVER committed to git**
- ❌ **NEVER pushed to public repositories**

### 3. Use Environment Variables Instead

**DO NOT** hardcode API keys in files. Use environment variables:

```bash
# Backend (.env file)
GEMINI_API_KEY=your-key-here
FRED_API_KEY=your-key-here
POLYGON_API_KEY=your-key-here

# Frontend (.env.local file)
NEXT_PUBLIC_FIREBASE_API_KEY=your-key-here
```

## Files Status

| File | In .gitignore? | Contains Keys | Action Required |
|------|----------------|---------------|----------------|
| `settoken.sh` | ✅ Yes | ✅ Yes | Rotate keys, remove from git if committed |
| `user_prefs.json` | ✅ Yes | ✅ Yes | Rotate keys, remove from git if committed |
| `env.txt` | ✅ Yes | ✅ Yes | Rotate AWS keys, remove from git if committed |
| `.streamlit/secrets.toml` | ✅ Yes | Maybe | Verify no keys exposed |

## Verification Commands

Before pushing to public repository:

```bash
# Check if files are tracked
git ls-files | grep -E "(settoken.sh|user_prefs.json|env.txt)"

# Check if files are ignored
git check-ignore -v settoken.sh user_prefs.json env.txt

# Search for potential API keys in code
grep -r "AIza[0-9A-Za-z_-]\{35\}" --exclude-dir=node_modules --exclude-dir=venv .
grep -r "sk-[0-9A-Za-z]\{32,\}" --exclude-dir=node_modules --exclude-dir=venv .
```

## Compliance

✅ **All sensitive files are in `.gitignore`**
✅ **Firebase config uses environment variables**
✅ **Backend config uses environment variables**
❌ **Some files contain hardcoded keys (need cleanup)**

**Before publishing this branch, ensure:**
1. All exposed keys are rotated
2. All sensitive files are removed from git history (if committed)
3. All keys are moved to environment variables
4. `.gitignore` is properly configured (✅ Done)

