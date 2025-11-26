# 🧪 Development Testing & Deployment Guide

## Overview

This guide covers:
- Testing the FastAPI backend during development
- Running both Streamlit and FastAPI simultaneously
- Deployment options and costs
- Migration path from Streamlit Cloud

---

## 🚀 Local Development Testing

### Running FastAPI Backend

```bash
# Navigate to backend directory
cd finq-backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the API
python -m app.main

# Or with auto-reload (recommended for development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API will be available at:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/health

### Running Streamlit App (Existing)

```bash
# In project root directory
cd /Users/harshitgola/Projects/SEC_exctractor/SEC_exctractor

# Activate your existing venv (or create one)
source venv/bin/activate

# Run Streamlit
streamlit run Home.py
```

**Streamlit will be available at:**
- http://localhost:8501

### Running Both Simultaneously

You can run both apps at the same time:

**Terminal 1 (FastAPI Backend):**
```bash
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Streamlit Frontend):**
```bash
cd /Users/harshitgola/Projects/SEC_exctractor/SEC_exctractor
source venv/bin/activate
streamlit run Home.py
```

### Testing API from Streamlit (Optional Integration)

Once endpoints are ready, you can test integration by updating Streamlit to call the API:

```python
# In Streamlit code (example)
import requests

# Test health check
response = requests.get("http://localhost:8000/api/health")
print(response.json())

# Test financial endpoint (when ready)
response = requests.get("http://localhost:8000/api/financial/ticker/AAPL")
print(response.json())
```

---

## 🧪 Testing Strategies

### 1. Unit Tests

```bash
cd finq-backend
pytest tests/ -v
```

### 2. API Testing (Manual)

**Using Browser:**
- Visit http://localhost:8000/docs
- Interactive Swagger UI for testing endpoints

**Using curl:**
```bash
# Health check
curl http://localhost:8000/api/health

# Financial data (when ready)
curl http://localhost:8000/api/financial/ticker/AAPL
```

**Using Python:**
```python
import requests

response = requests.get("http://localhost:8000/api/health")
print(response.json())
```

### 3. Integration Testing

Test the full flow:
1. Start FastAPI backend
2. Start Streamlit app
3. Use Streamlit to call API endpoints
4. Verify data flows correctly

---

## 🌐 Deployment Options & Costs

### Option 1: Free Tier (Recommended for Start)

**Best for**: Testing, MVP, low traffic

#### Backend: Railway (Free Tier)
- **Cost**: FREE (with limits)
- **Limits**: 
  - 500 hours/month free
  - $5 credit/month
  - Sleeps after inactivity
- **Setup**: Very easy, connects to GitHub
- **Database**: Included PostgreSQL (limited)

**Alternative: Render (Free Tier)**
- **Cost**: FREE
- **Limits**: Sleeps after 15 min inactivity
- **Database**: Separate free PostgreSQL

#### Frontend: Vercel (Free Tier)
- **Cost**: FREE
- **Limits**: 
  - 100GB bandwidth/month
  - Unlimited deployments
  - No sleep
- **Setup**: Connect GitHub, auto-deploy

**Total Cost: $0/month** ✅

**Limitations:**
- Backend may sleep (wake-up delay ~30s)
- Limited database storage
- Not ideal for production with high traffic

---

### Option 2: Low-Cost Production (Recommended for Growth)

**Best for**: Production, reliable uptime, growing user base

#### Backend: Railway (Paid)
- **Cost**: ~$5-20/month
- **Features**:
  - No sleep
  - Better performance
  - More resources
  - Better database

#### Database: Supabase (Free/Paid)
- **Free Tier**: 
  - 500MB database
  - 2GB bandwidth
  - Good for testing
- **Pro Tier**: $25/month
  - 8GB database
  - 50GB bandwidth
  - Better performance

#### Frontend: Vercel (Free/Pro)
- **Free**: Sufficient for most use cases
- **Pro**: $20/month (if needed)
  - More bandwidth
  - Better analytics

**Total Cost: $5-45/month**
- Minimum: $5/month (Railway + Supabase Free)
- Recommended: $30/month (Railway + Supabase Pro)

---

### Option 3: Enterprise Scale

**Best for**: High traffic, enterprise features

#### Backend: AWS/GCP/Azure
- **Cost**: $50-200+/month
- **Features**: Full control, scaling, enterprise support

#### Database: Managed PostgreSQL
- **Cost**: $15-100+/month
- **Features**: High availability, backups, scaling

**Total Cost: $65-300+/month**

---

## 💰 Cost Comparison

| Option | Backend | Database | Frontend | Total/Month | Best For |
|-------|---------|----------|----------|-------------|----------|
| **Free** | Railway Free | Supabase Free | Vercel Free | **$0** | Testing, MVP |
| **Low-Cost** | Railway $5 | Supabase Free | Vercel Free | **$5** | Small production |
| **Recommended** | Railway $10 | Supabase Pro $25 | Vercel Free | **$35** | Growing app |
| **Enterprise** | AWS $50+ | RDS $15+ | Vercel Pro $20 | **$85+** | High scale |

---

## 🚀 Deployment Platforms (Detailed)

### Backend: Railway (Recommended)

**Why Railway?**
- ✅ Easy setup (GitHub integration)
- ✅ Free tier available
- ✅ Automatic deployments
- ✅ Built-in PostgreSQL
- ✅ Environment variables management
- ✅ Logs and monitoring

**Setup Steps:**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project
4. Deploy from GitHub repo
5. Add PostgreSQL service
6. Set environment variables
7. Deploy!

**Cost:**
- Free tier: 500 hours/month
- Paid: $5/month (starter), $20/month (pro)

### Database: Supabase (Recommended)

**Why Supabase?**
- ✅ Free tier (500MB)
- ✅ PostgreSQL (industry standard)
- ✅ Easy migrations
- ✅ Built-in auth (if needed later)
- ✅ Real-time features

**Setup Steps:**
1. Go to [supabase.com](https://supabase.com)
2. Create free account
3. Create new project
4. Copy connection string
5. Use in Railway environment variables

**Cost:**
- Free: 500MB database
- Pro: $25/month (8GB)

### Frontend: Vercel (Recommended)

**Why Vercel?**
- ✅ Free tier (generous)
- ✅ Zero-config Next.js deployment
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ No sleep

**Setup Steps:**
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import repository
4. Configure build settings
5. Deploy!

**Cost:**
- Free: 100GB bandwidth/month
- Pro: $20/month (if needed)

---

## 📋 Deployment Checklist

### Pre-Deployment

- [ ] All tests passing locally
- [ ] Environment variables documented
- [ ] Database migrations ready
- [ ] API endpoints tested
- [ ] Error handling in place
- [ ] Logging configured

### Backend Deployment (Railway)

- [ ] Create Railway account
- [ ] Connect GitHub repository
- [ ] Create new project
- [ ] Add PostgreSQL service
- [ ] Set environment variables:
  - `DATABASE_URL` (from Railway PostgreSQL)
  - `GEMINI_API_KEY`
  - `FRED_API_KEY`
  - `FIREBASE_CREDENTIALS_JSON`
- [ ] Deploy
- [ ] Test health endpoint
- [ ] Monitor logs

### Database Setup (Supabase)

- [ ] Create Supabase account
- [ ] Create new project
- [ ] Run migrations:
  ```bash
  # Set DATABASE_URL to Supabase connection string
  alembic upgrade head
  ```
- [ ] Test database connection
- [ ] Verify tables created

### Frontend Deployment (Vercel) - Future

- [ ] Create Vercel account
- [ ] Connect GitHub repository
- [ ] Configure build settings
- [ ] Set environment variables
- [ ] Deploy
- [ ] Test frontend

---

## 🔄 Migration Path from Streamlit Cloud

### Phase 1: Parallel Deployment (Current)
- ✅ Keep Streamlit Cloud running
- ✅ Deploy FastAPI backend to Railway
- ✅ Test integration
- ✅ No downtime

### Phase 2: Gradual Migration
- Streamlit calls new API endpoints
- Both systems running
- Monitor performance

### Phase 3: Full Migration
- Deploy Next.js frontend to Vercel
- Streamlit Cloud deprecated
- All traffic to new infrastructure

---

## 🧪 Testing During Development

### Daily Workflow

1. **Start Backend:**
   ```bash
   cd finq-backend
   uvicorn app.main:app --reload
   ```

2. **Test Endpoints:**
   - Visit http://localhost:8000/docs
   - Test new endpoints
   - Check logs for errors

3. **Run Tests:**
   ```bash
   pytest -v
   ```

4. **Test Integration:**
   - Start Streamlit
   - Test API calls from Streamlit
   - Verify data flow

### Before Committing

- [ ] All tests pass
- [ ] Code formatted (black)
- [ ] No linting errors
- [ ] Documentation updated
- [ ] Tested locally

---

## 📊 Monitoring & Logs

### Railway Logs
- View in Railway dashboard
- Real-time logs
- Error tracking

### Local Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Health Monitoring
- Set up health check endpoint
- Monitor `/api/health`
- Set up alerts (future)

---

## 💡 Cost Optimization Tips

1. **Start Free**: Use free tiers initially
2. **Monitor Usage**: Track API calls, database size
3. **Optimize Caching**: Reduce external API calls
4. **Database Indexing**: Improve query performance
5. **CDN Usage**: Use Vercel CDN for static assets
6. **Scale Gradually**: Upgrade only when needed

---

## 🎯 Recommended Setup for Your Use Case

### Phase 1 (Now - Testing)
- **Backend**: Railway Free Tier
- **Database**: Supabase Free Tier
- **Cost**: **$0/month**
- **Limitations**: Backend may sleep, 500MB database

### Phase 2 (Production - Growing)
- **Backend**: Railway $10/month
- **Database**: Supabase Pro $25/month
- **Frontend**: Vercel Free
- **Cost**: **$35/month**
- **Benefits**: No sleep, reliable, scalable

### Phase 3 (Scale - If Needed)
- **Backend**: Railway Pro $20/month
- **Database**: Supabase Pro $25/month
- **Frontend**: Vercel Pro $20/month (if needed)
- **Cost**: **$65/month**
- **Benefits**: Enterprise features, high performance

---

## 🚨 Important Notes

1. **Free Tiers Have Limits**: 
   - Railway free tier sleeps after inactivity
   - Supabase free tier: 500MB database limit
   - Monitor usage to avoid surprises

2. **Start Small**: 
   - Begin with free tiers
   - Upgrade when you hit limits
   - Don't over-provision initially

3. **Backup Strategy**: 
   - Regular database backups
   - Environment variable backups
   - Code in version control

4. **Security**: 
   - Never commit API keys
   - Use environment variables
   - Enable HTTPS (automatic on Vercel/Railway)

---

## 📚 Next Steps

1. **Set up Railway account** (free tier)
2. **Set up Supabase account** (free tier)
3. **Deploy backend** to Railway
4. **Test deployment** with health endpoint
5. **Set up database** migrations
6. **Monitor costs** and usage

---

**Remember**: Start free, scale as needed. The free tiers are generous enough for development and initial production use.

