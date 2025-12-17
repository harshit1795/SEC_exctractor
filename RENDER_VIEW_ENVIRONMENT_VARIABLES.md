# 👀 How to View Environment Variables in Render

## 🎯 Quick Steps

### Step 1: Go to Render Dashboard

1. **Open Render Dashboard**: https://dashboard.render.com
2. **Sign in** to your account

### Step 2: Select Your Service

1. **Click on your backend service** (e.g., `finq-backend`)
   - You'll see it in the list of services on the dashboard

### Step 3: View Environment Variables

1. **Click on the "Environment" tab** (top navigation)
   - It's next to "Logs", "Metrics", "Settings", etc.

2. **You'll see all environment variables** listed:
   - Variable names on the left
   - Values on the right (masked for security - click "Reveal" to see values)
   - Environment scope (if applicable)

---

## 📋 What You'll See

In the Environment tab, you'll see variables like:

| Variable Name | Value | Actions |
|---------------|-------|---------|
| `DATABASE_URL` | `••••••••` | Edit / Delete |
| `GEMINI_API_KEY` | `••••••••` | Edit / Delete |
| `CORS_ORIGINS` | `https://...` | Edit / Delete |
| `FRED_API_KEY` | `••••••••` | Edit / Delete |

---

## 🔍 Viewing Variable Values

### For Security (Masked Values):

- **Sensitive variables** (like API keys, passwords) are **masked** by default
- You'll see dots: `••••••••`
- **Click "Reveal"** button to see the actual value
- Values are hidden again after a few seconds

### For Non-Sensitive Values:

- **Non-sensitive variables** (like URLs, paths) are **visible** directly
- Example: `CORS_ORIGINS` shows the full value

---

## 📝 Step-by-Step with Screenshots Guide

### 1. Navigate to Your Service

```
Render Dashboard
  └── Services
      └── finq-backend (click here)
```

### 2. Open Environment Tab

```
Service Page
  ├── Overview
  ├── Logs
  ├── Metrics
  ├── Environment ← Click here!
  ├── Settings
  └── ...
```

### 3. View Variables

You'll see a table/list of all environment variables with:
- **Name**: Variable name (e.g., `DATABASE_URL`)
- **Value**: Masked or visible value
- **Actions**: Edit / Delete buttons

---

## 🔧 Common Variables You Should See

For your FinQ backend, you should see:

1. **`DATABASE_URL`** - PostgreSQL connection string
2. **`GEMINI_API_KEY`** - Google Gemini API key
3. **`CORS_ORIGINS`** - Allowed frontend URLs
4. **`FRED_API_KEY`** - FRED API key (optional)
5. **`APP_NAME`** - Application name
6. **`API_PREFIX`** - API prefix (usually `/api`)
7. **`DEBUG`** - Debug mode flag

---

## ✏️ How to Edit a Variable

1. **Click "Edit"** button next to the variable
2. **Update the value** in the popup/form
3. **Click "Save"**
4. **Render will auto-redeploy** with the new value

---

## ➕ How to Add a New Variable

1. **In the Environment tab**, scroll down
2. **Click "Add Environment Variable"** or **"Add New"** button
3. **Enter**:
   - **Key**: Variable name (e.g., `NEW_VARIABLE`)
   - **Value**: Variable value
4. **Click "Save"**
5. **Render will auto-redeploy**

---

## 🗑️ How to Delete a Variable

1. **Click "Delete"** button next to the variable
2. **Confirm deletion** in the popup
3. **Render will auto-redeploy** without that variable

---

## 🔒 Security Notes

- **Sensitive values are masked** - Click "Reveal" to see them
- **Values auto-hide** after viewing for security
- **Be careful** when sharing screenshots - values might be visible

---

## 📍 Direct URL Path

If you know your service name, you can go directly to:

```
https://dashboard.render.com/web/[your-service-name]/environment
```

Replace `[your-service-name]` with your actual service name.

---

## ✅ Quick Checklist

- [ ] Logged into Render Dashboard
- [ ] Selected your backend service
- [ ] Clicked "Environment" tab
- [ ] Can see all environment variables
- [ ] Can reveal masked values if needed

---

## 🎯 What to Check

When viewing your environment variables, verify:

1. **`DATABASE_URL`** is set correctly
2. **`GEMINI_API_KEY`** is set (for FinQ Chat)
3. **`CORS_ORIGINS`** includes your Vercel URL:
   ```
   https://sec-exctractor.vercel.app,https://finq-frontend-render-git-*.vercel.app
   ```

---

**Need Help?** If you can't find the Environment tab, make sure you're viewing the correct service (your backend service, not a database or other service).

