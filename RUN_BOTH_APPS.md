# 🚀 Running Both Apps Simultaneously

## Overview

You can run both your **Streamlit app** (Home.py) and the **FastAPI backend** at the same time. They run on different ports and don't interfere with each other.

---

## Quick Start

### Option 1: Two Terminal Windows (Recommended)

**Terminal 1 - FastAPI Backend:**
```bash
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
→ Runs on: http://localhost:8000

**Terminal 2 - Streamlit App:**
```bash
cd /Users/harshitgola/Projects/SEC_exctractor/SEC_exctractor
source venv/bin/activate  # Your existing venv
streamlit run Home.py
```
→ Runs on: http://localhost:8501

---

### Option 2: Background Process

**Start FastAPI in background:**
```bash
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
```

**Then run Streamlit:**
```bash
cd /Users/harshitgola/Projects/SEC_exctractor/SEC_exctractor
source venv/bin/activate
streamlit run Home.py
```

---

## Ports

- **FastAPI Backend**: http://localhost:8000
- **Streamlit App**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs

---

## Testing Both

1. **FastAPI**: Visit http://localhost:8000/docs
2. **Streamlit**: Visit http://localhost:8501

Both should work independently!

---

## Future Integration

Eventually, you can update your Streamlit app to call the FastAPI backend:

```python
# In your Streamlit code
import requests

# Call the API
response = requests.get("http://localhost:8000/api/financial/ticker/AAPL")
data = response.json()
```

But for now, they run independently.

---

## Stopping the Apps

**FastAPI:**
- Press `Ctrl+C` in the terminal, or
- `pkill -f "uvicorn app.main:app"`

**Streamlit:**
- Press `Ctrl+C` in the terminal, or
- `pkill -f streamlit`

---

## Troubleshooting

### Port Already in Use

If port 8501 is already in use:
```bash
# Kill existing Streamlit
pkill -f streamlit

# Or use different port
streamlit run Home.py --server.port 8502
```

### Virtual Environment

Make sure you're using the correct virtual environment:
- **FastAPI**: `finq-backend/venv`
- **Streamlit**: Your existing project `venv` (if you have one)

If you don't have a venv for the main project:
```bash
cd /Users/harshitgola/Projects/SEC_exctractor/SEC_exctractor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run Home.py
```

---

**You're all set!** Both apps can run simultaneously without any conflicts.

