# 🔌 Railway Port Configuration

## When Railway Asks: "What port is your app listening on?"

### ✅ Answer: Use `$PORT` (Railway's Environment Variable)

Your app is configured to listen on the port that Railway provides via the `$PORT` environment variable.

---

## Option 1: Leave Blank or Use Default (Recommended)

**If Railway gives you an option to:**
- Leave it blank
- Use default
- Auto-detect

**→ Choose that option!** Railway will automatically use the port from `$PORT`.

---

## Option 2: Check Railway's Assigned Port

If Railway requires a specific port number:

1. **Check Environment Variables**:
   - Go to Railway → Your Service → **Variables** tab
   - Look for `PORT` environment variable
   - Railway automatically sets this (usually something like `3000`, `8000`, or a random port)

2. **Or Check Deployment Logs**:
   - Go to Railway → Your Service → **Deployments** tab
   - Click on latest deployment
   - Look for logs showing: `Uvicorn running on http://0.0.0.0:PORT`
   - The PORT number will be shown there

---

## Option 3: Tell Railway It Uses `$PORT`

If Railway has a text field, you can enter:
```
$PORT
```
or
```
Dynamic (uses $PORT environment variable)
```

---

## ✅ Our Configuration

Our start command already uses `$PORT`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

This means:
- Railway sets `$PORT` automatically
- Our app reads `$PORT` and listens on that port
- Railway's public networking will route traffic to that port

---

## 🎯 Most Common Answer

**Just leave it blank or select "Auto-detect"** - Railway will figure it out from your start command!

---

## 📝 After Setting Port

Once you've configured the port (or left it auto-detect), Railway will:
1. Generate your public domain
2. Route traffic from the public URL to your app on the correct port
3. Show you the public URL like: `https://your-app.up.railway.app`

---

**TL;DR: Leave it blank/auto-detect, or check the `PORT` variable in Railway Variables tab!** 🚀

