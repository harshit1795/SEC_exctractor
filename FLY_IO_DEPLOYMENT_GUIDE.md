# 🚀 Fly.io Deployment Guide (Always-On Free)

Fly.io offers **always-on** free hosting with no sleep mode. Here's how to deploy your FinQ backend.

## ✅ Why Fly.io?

- ✅ **Always-On**: No sleep, no inactivity timeout
- ✅ **Free Forever**: 2,340 CPU hours/month (enough for always-on)
- ✅ **IPv4 Support**: Full IPv4 support (fixes your Supabase issue)
- ✅ **Easy Setup**: Similar to Railway/Render
- ✅ **Global**: Deploy close to users

## 📋 Prerequisites

1. **Fly.io Account**: Sign up at https://fly.io (free)
2. **Credit Card**: Required but won't be charged on free tier
3. **GitHub Repository**: Your code should be in GitHub

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Install Fly CLI

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows:**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Verify installation:**
```bash
fly version
```

### Step 2: Sign Up / Login

```bash
fly auth signup
# Or if you already have an account:
fly auth login
```

This will open your browser to sign up/login.

### Step 3: Navigate to Backend Directory

```bash
cd finq-backend
```

### Step 4: Launch Your App

```bash
fly launch
```

**What this does:**
- Creates a new Fly.io app
- Detects your Python app
- Asks you to name your app (or use default)
- Asks for region (choose closest to you)
- Creates `fly.toml` configuration file

**Questions it will ask:**
1. **App name**: `finq-backend` (or your choice)
2. **Region**: Choose closest (e.g., `iad` for US East)
3. **Postgres**: Say "No" (you're using Supabase)
4. **Redis**: Say "No" (unless you need it)

### Step 5: Set Environment Variables

```bash
# Set database URL
fly secrets set DATABASE_URL="postgresql://postgres:[PASSWORD]@db.tdebmqhaoiexsdhxwung.supabase.co:5432/postgres?connect_timeout=10&sslmode=require"

# Set API key
fly secrets set GEMINI_API_KEY="your_gemini_api_key_here"

# Set CORS origins (comma-separated, no spaces)
fly secrets set CORS_ORIGINS="https://sec-exctractor.vercel.app,https://sec-exctractor-git-*.vercel.app"

# Optional: Other env vars
fly secrets set APP_NAME="FinQ Backend API"
fly secrets set API_PREFIX="/api"
fly secrets set DEBUG="false"
```

**Note**: Secrets are encrypted and only available at runtime.

### Step 6: Deploy

```bash
fly deploy
```

This will:
- Build your app
- Deploy to Fly.io
- Give you a URL like `https://finq-backend.fly.dev`

### Step 7: Verify Deployment

```bash
# Check app status
fly status

# View logs
fly logs

# Test health endpoint
curl https://your-app.fly.dev/api/health
```

## 🔧 Configuration

### Update fly.toml

The `fly.toml` file is created automatically. You can edit it to customize:

```toml
app = "finq-backend"
primary_region = "iad"  # Change to your preferred region

[http_service]
  internal_port = 8000
  auto_stop_machines = false  # Keep always-on
  min_machines_running = 1    # Always keep 1 machine running

[[vm]]
  memory_mb = 512  # Adjust based on needs
  cpu_kind = "shared"  # Free tier uses shared CPU
```

### Available Regions

- `iad` - US East (Virginia)
- `sjc` - US West (San Jose)
- `lhr` - London
- `fra` - Frankfurt
- `sin` - Singapore
- `syd` - Sydney

See all: `fly regions list`

## 📊 Monitoring

### View Logs

```bash
# Real-time logs
fly logs

# Last 100 lines
fly logs --limit 100
```

### Check Status

```bash
# App status
fly status

# List all apps
fly apps list

# App info
fly info
```

### Metrics

View in Fly.io Dashboard: https://fly.io/dashboard

## 🔄 Updates & Redeployment

### Deploy Updates

```bash
# After making changes, just deploy again
fly deploy
```

### Update Secrets

```bash
# Update a secret
fly secrets set DATABASE_URL="new_url"

# List all secrets
fly secrets list

# Remove a secret
fly secrets unset KEY_NAME
```

## 🐛 Troubleshooting

### Issue: Build Fails

**Error**: `ModuleNotFoundError`

**Solution**:
```bash
# Check requirements.txt is in finq-backend/
# Verify all dependencies are listed
pip install -r requirements.txt  # Test locally first
```

### Issue: Database Connection Fails

**Error**: `connection to server... Network is unreachable`

**Solution**:
1. **Verify DATABASE_URL**:
   ```bash
   fly secrets list  # Check it's set correctly
   ```

2. **Try connection pooler** (port 6543):
   ```bash
   fly secrets set DATABASE_URL="postgresql://postgres:[PASSWORD]@db.tdebmqhaoiexsdhxwung.supabase.co:6543/postgres?connect_timeout=10&sslmode=require"
   ```

3. **Check Supabase Network Restrictions**: Allow all IPs

### Issue: App Crashes

**Check logs**:
```bash
fly logs
```

**Common causes**:
- Missing environment variables
- Database connection issues
- Port mismatch (should be 8000 internally)

### Issue: CORS Errors

**Solution**:
1. **Verify CORS_ORIGINS**:
   ```bash
   fly secrets set CORS_ORIGINS="https://your-frontend.com,https://another.com"
   ```
   (No spaces, comma-separated)

2. **Redeploy**:
   ```bash
   fly deploy
   ```

## 💰 Free Tier Limits

- **CPU**: 2,340 shared CPU hours/month (enough for always-on)
- **Memory**: 256MB shared (512MB+ requires paid)
- **Bandwidth**: 160GB outbound/month
- **Storage**: 3GB persistent storage
- **Machines**: 3 shared VMs

**For your FastAPI app**: Free tier should be sufficient!

## 🎯 Next Steps

1. ✅ **Deploy to Fly.io** (follow steps above)
2. ✅ **Update Vercel**: Change `NEXT_PUBLIC_API_URL` to your Fly.io URL
3. ✅ **Test everything**: Verify all endpoints work
4. ✅ **Monitor**: Check logs and metrics

## 🔗 Useful Commands

```bash
# App management
fly apps list              # List all apps
fly status                 # Check app status
fly info                   # Detailed app info
fly open                   # Open app in browser

# Deployment
fly deploy                 # Deploy latest code
fly deploy --remote-only   # Deploy without building locally

# Secrets
fly secrets list           # List all secrets
fly secrets set KEY=value  # Set a secret
fly secrets unset KEY      # Remove a secret

# Logs & Monitoring
fly logs                   # View logs
fly logs --region iad      # Logs from specific region
fly status                 # App status

# SSH (for debugging)
fly ssh console            # SSH into running machine
fly ssh sftp               # SFTP access
```

## 📚 Resources

- **Fly.io Docs**: https://fly.io/docs
- **Python Guide**: https://fly.io/docs/languages-and-frameworks/python/
- **Dashboard**: https://fly.io/dashboard
- **Support**: https://community.fly.io

---

**Your Fly.io URL**: `https://[your-app-name].fly.dev`

**Need Help?** Check Fly.io community forum or docs!

