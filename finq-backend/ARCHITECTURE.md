# 🏗️ FinQ Architecture - Migration Overview

## Current Architecture (After Migration)

### **NEW: FastAPI Backend (Phase 1 & 2 Complete)**

```
┌─────────────────────────────────────────────────────────┐
│              Frontend (HTML/JavaScript)                  │
│         http://localhost:8080                           │
│  - Simple HTML/JS UI                                    │
│  - Calls FastAPI endpoints                              │
│  - No Streamlit dependency                              │
└─────────────────────────────────────────────────────────┘
                        ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────┐
│            FastAPI Backend (Python)                     │
│         http://localhost:8000                           │
│                                                          │
│  ┌──────────────────────────────────────────────┐     │
│  │  API Endpoints                                │     │
│  │  - /api/financial/*  (Stock data)            │     │
│  │  - /api/chat/*       (AI analysis)           │     │
│  │  - /api/nexus/*      (Social features)       │     │
│  │  - /api/insights/*   (Sharing)               │     │
│  └──────────────────────────────────────────────┘     │
│                                                          │
│  ┌──────────────────────────────────────────────┐     │
│  │  Services (Migrated from Streamlit)          │     │
│  │  - DataSourceManager (Yahoo, FRED, SEC)      │     │
│  │  - FinancialAnalyzer (AI/Gemini)             │     │
│  │  - SEC Service (Filing parsing)              │     │
│  │  - FRED Service (Economic data)              │     │
│  └──────────────────────────────────────────────┘     │
│                                                          │
│  ┌──────────────────────────────────────────────┐     │
│  │  Database (SQLite/PostgreSQL)                │     │
│  │  - Insights (Chat history)                   │     │
│  │  - Posts (Nexus feed)                        │     │
│  │  - Friends (Social connections)              │     │
│  │  - Comments, Likes                           │     │
│  └──────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### **OLD: Streamlit App (Still Exists, Not Used)**

```
┌─────────────────────────────────────────────────────────┐
│         Streamlit App (Original)                        │
│         pages/dashboard_tabs/chatbot_tab.py              │
│         pages/Nexus.py                                   │
│         components/nexus_firebase.py                      │
│                                                          │
│  ⚠️  This is the OLD codebase                            │
│  ⚠️  Still exists but NOT being used by new frontend    │
│  ⚠️  Can be run separately if needed                     │
└─────────────────────────────────────────────────────────┘
```

---

## Key Differences

### **OLD Architecture (Streamlit)**
- ❌ Monolithic: Everything in one Streamlit app
- ❌ Server-side rendering: Full page reloads
- ❌ Session state: Data lost on refresh
- ❌ Limited UI: Streamlit components only
- ❌ No API: Direct function calls
- ❌ Firebase only: No PostgreSQL

### **NEW Architecture (FastAPI)**
- ✅ API-First: RESTful endpoints
- ✅ Client-side rendering: Fast, responsive UI
- ✅ Database persistence: Data saved to SQLite/PostgreSQL
- ✅ Modern UI: HTML/CSS/JavaScript (can be Next.js later)
- ✅ Scalable: Can handle multiple clients
- ✅ Real-time ready: WebSocket support planned

---

## File Structure

### **New FastAPI Backend** (`finq-backend/`)
```
finq-backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── api/
│   │   ├── financial.py     # Stock/economic data endpoints
│   │   ├── chat.py          # AI analysis endpoints
│   │   ├── nexus.py         # Social features endpoints
│   │   ├── insights.py       # Insight sharing endpoints
│   │   └── health.py         # Health check
│   ├── services/
│   │   ├── data_source_manager.py  # Migrated from Streamlit
│   │   ├── financial_analyzer.py   # Migrated from Streamlit
│   │   ├── fred_service.py         # FRED API wrapper
│   │   └── sec_service.py          # SEC filing parser
│   ├── models/
│   │   ├── insight.py       # Database models
│   │   ├── post.py          # Post models
│   │   └── friend.py        # Friend models
│   └── schemas/
│       ├── financial.py     # Request/response schemas
│       ├── chat.py          # Chat schemas
│       └── nexus.py         # Nexus schemas
├── frontend/
│   └── index.html           # Simple HTML/JS frontend
└── requirements.txt         # Python dependencies
```

### **Old Streamlit App** (Root directory)
```
SEC_exctractor/
├── pages/
│   ├── dashboard_tabs/
│   │   └── chatbot_tab.py   # OLD Streamlit chatbot
│   └── Nexus.py              # OLD Streamlit Nexus
├── components/
│   └── nexus_firebase.py     # OLD Firebase helpers
└── home.py                   # OLD Streamlit entry point
```

---

## How It Works Now

### 1. **Frontend (HTML/JS)**
- Runs on `http://localhost:8080`
- Makes HTTP requests to FastAPI backend
- No Python/Streamlit needed
- Pure JavaScript

### 2. **Backend (FastAPI)**
- Runs on `http://localhost:8000`
- Receives HTTP requests
- Processes using migrated services
- Returns JSON responses
- Saves to database

### 3. **Services (Migrated Code)**
- **DataSourceManager**: Same logic as Streamlit version, but async
- **FinancialAnalyzer**: Same AI logic, but API endpoint
- **SEC/FRED Services**: Same parsing logic, but RESTful

---

## Migration Status

### ✅ **Migrated (Phase 1 & 2)**
- [x] DataSourceManager → `/api/financial/*`
- [x] FinancialAnalyzer → `/api/chat/analyze`
- [x] Nexus features → `/api/nexus/*`
- [x] Insight sharing → `/api/insights/*`
- [x] Database models (Insights, Posts, Friends)
- [x] All core functionality

### 🚧 **Not Yet Migrated**
- [ ] Media generation (charts to images)
- [ ] WebSocket real-time updates
- [ ] User authentication (still using user_id parameter)
- [ ] Next.js frontend (currently simple HTML)

### ❌ **Not Needed**
- Streamlit UI (replaced by HTML/JS)
- Streamlit session state (replaced by database)
- Streamlit components (replaced by HTML/CSS)

---

## Running the Application

### **Start FastAPI Backend**
```bash
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload
# Runs on http://localhost:8000
```

### **Start Frontend**
```bash
cd finq-backend
python3 -m http.server 8080 --directory frontend
# Runs on http://localhost:8080
```

### **Old Streamlit (Optional)**
```bash
# If you want to run the old app separately
streamlit run home.py
# Runs on http://localhost:8501
```

---

## Data Flow Example

### **User Requests Stock Data**

1. **Frontend** (`index.html`)
   ```javascript
   fetch('http://localhost:8000/api/financial/ticker/AAPL')
   ```

2. **FastAPI** (`app/api/financial.py`)
   ```python
   @router.get("/ticker/{ticker}")
   async def get_ticker_data(...):
       data = await manager.get_yahoo_finance_data(ticker)
       return data
   ```

3. **Service** (`app/services/data_source_manager.py`)
   ```python
   async def get_yahoo_finance_data(self, ticker):
       # Same logic as old Streamlit version
       ticker_obj = yf.Ticker(ticker)
       return ticker_obj.info
   ```

4. **Response** → Frontend displays data

---

## Why "Failed to Fetch"?

Common causes:
1. **Backend not running** - Check `http://localhost:8000/api/health`
2. **CORS issue** - Should be fixed now
3. **Wrong URL** - Frontend should call `http://localhost:8000/api/...`
4. **Network error** - Check browser console

---

## Next Steps

1. **Fix any remaining issues** - Debug "Failed to fetch"
2. **Add authentication** - Replace `user_id` parameter with auth tokens
3. **Build Next.js frontend** - Replace simple HTML with React
4. **Add WebSocket** - Real-time feed updates
5. **Deploy** - Production deployment

---

**Summary**: The new architecture is **completely separate** from Streamlit. The old `.py` files still exist but are **not used** by the new frontend. Everything has been migrated to FastAPI endpoints.

