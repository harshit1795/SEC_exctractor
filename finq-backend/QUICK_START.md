# ⚡ Quick Start Guide

## 🚀 Get Running in 5 Minutes

### 1. Install Dependencies

```bash
cd finq-backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env (minimum required):
# DATABASE_URL=sqlite:///./finq.db  # For quick testing
# GEMINI_API_KEY=your_key_here
# FRED_API_KEY=your_key_here
```

### 3. Run the API

```bash
# Simple run
python -m app.main

# Or with auto-reload (recommended)
uvicorn app.main:app --reload
```

### 4. Test It

Open your browser:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## 🧪 Quick Test

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Or in Python
python -c "import requests; print(requests.get('http://localhost:8000/api/health').json())"
```

---

## 📝 Development Workflow

### Terminal 1: Backend API
```bash
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Streamlit (Existing App)
```bash
cd /Users/harshitgola/Projects/SEC_exctractor/SEC_exctractor
source venv/bin/activate
streamlit run Home.py
```

### Terminal 3: Run Tests
```bash
cd finq-backend
pytest -v
```

---

## 🌐 Deploy to Railway (Free)

1. **Sign up**: [railway.app](https://railway.app) (GitHub login)
2. **Create Project**: New Project → Deploy from GitHub
3. **Select Repo**: Choose your repository
4. **Add PostgreSQL**: New → Database → PostgreSQL
5. **Set Variables**: 
   - `DATABASE_URL` (from Railway PostgreSQL)
   - `GEMINI_API_KEY`
   - `FRED_API_KEY`
6. **Deploy**: Railway auto-deploys on push

**Cost**: FREE (500 hours/month)

---

## 📊 What's Working

✅ Health check endpoint  
✅ API documentation (Swagger)  
✅ Database models  
✅ Configuration system  
🚧 Financial endpoints (in progress)  
🚧 Chat API (in progress)  

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Import Errors
```bash
# Make sure you're in finq-backend directory
# And virtual environment is activated
which python  # Should show venv path
```

### Database Connection
```bash
# For quick testing, use SQLite
# In .env: DATABASE_URL=sqlite:///./finq.db
```

---

**Need Help?** See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions.


