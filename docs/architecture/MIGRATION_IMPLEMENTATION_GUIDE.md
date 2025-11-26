# 🔧 Migration Implementation Guide

## Quick Start: Phase 1 Setup

### Step 1: Backend API Setup (FastAPI)

```bash
# Create new directory for backend
mkdir finq-backend
cd finq-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic
pip install firebase-admin google-generativeai yfinance fredapi
pip install python-multipart pydantic-settings
```

### Project Structure
```
finq-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── insight.py
│   │   ├── post.py
│   │   └── subscription.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── insight.py
│   │   └── post.py
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── financial.py
│   │   ├── chat.py
│   │   ├── nexus.py
│   │   └── payments.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── data_source_manager.py  # Migrated from Streamlit
│   │   ├── financial_analyzer.py   # Migrated from Streamlit
│   │   ├── nexus_service.py
│   │   └── media_service.py
│   └── utils/
│       ├── __init__.py
│       └── firebase.py
├── alembic/                 # Database migrations
├── requirements.txt
└── .env
```

### Step 2: Database Setup (PostgreSQL)

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/finq")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Step 3: Migrate DataSourceManager

```python
# app/services/data_source_manager.py
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from app.services.fred_data import get_fred_series

class DataSourceManager:
    """Migrated from Streamlit - now API service"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_yahoo_finance_data(
        self, 
        ticker: str, 
        period: str = "1y"
    ) -> Dict[str, Any]:
        """Fetch comprehensive data from Yahoo Finance"""
        cache_key = f"yf_{ticker}_{period}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]
        
        try:
            ticker_obj = yf.Ticker(ticker)
            data = {
                'info': ticker_obj.info,
                'financials': ticker_obj.financials.to_dict(),
                'balance_sheet': ticker_obj.balance_sheet.to_dict(),
                'cashflow': ticker_obj.cashflow.to_dict(),
                'history': ticker_obj.history(period=period).to_dict(),
            }
            self._cache_data(cache_key, data)
            return data
        except Exception as e:
            raise Exception(f"Error fetching Yahoo Finance data: {e}")
    
    def _is_cache_valid(self, key: str) -> bool:
        if key not in self.cache:
            return False
        cache_time, _ = self.cache[key]
        return (datetime.now() - cache_time).seconds < self.cache_ttl
    
    def _cache_data(self, key: str, data: Any) -> None:
        self.cache[key] = (datetime.now(), data)
```

### Step 4: Create API Endpoints

```python
# app/api/financial.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.data_source_manager import DataSourceManager
from typing import List

router = APIRouter(prefix="/api/financial", tags=["financial"])

@router.get("/ticker/{ticker}")
async def get_ticker_data(
    ticker: str,
    period: str = "1y",
    db: Session = Depends(get_db)
):
    """Get financial data for a ticker"""
    manager = DataSourceManager()
    try:
        data = await manager.get_yahoo_finance_data(ticker, period)
        return {"ticker": ticker, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickers")
async def get_multiple_tickers(
    tickers: str,  # Comma-separated
    period: str = "1y",
    db: Session = Depends(get_db)
):
    """Get data for multiple tickers"""
    ticker_list = [t.strip() for t in tickers.split(",")]
    manager = DataSourceManager()
    results = {}
    for ticker in ticker_list:
        try:
            data = await manager.get_yahoo_finance_data(ticker, period)
            results[ticker] = data
        except Exception as e:
            results[ticker] = {"error": str(e)}
    return results
```

### Step 5: Chat API with Persistence

```python
# app/models/insight.py
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid

class Insight(Base):
    __tablename__ = "insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    chat_session_id = Column(String, nullable=True)
    content = Column(JSON, nullable=False)  # Full chat context
    summary = Column(String, nullable=True)
    tickers = Column(JSON, nullable=True)  # List of tickers analyzed
    media_urls = Column(JSON, nullable=True)  # Generated charts/images
    created_at = Column(DateTime, default=datetime.utcnow)
    shared = Column(Boolean, default=False)
```

```python
# app/api/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.insight import Insight
from app.services.financial_analyzer import FinancialAnalyzer
from app.schemas.insight import InsightCreate, InsightResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/analyze")
async def analyze_financial_data(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Analyze financial data and store insight"""
    analyzer = FinancialAnalyzer()
    
    # Generate analysis (migrated from Streamlit)
    response = await analyzer.analyze_financial_data(
        request.prompt,
        request.context_data
    )
    
    # Store insight in database
    insight = Insight(
        user_id=current_user["uid"],
        chat_session_id=request.session_id,
        content={
            "prompt": request.prompt,
            "response": response,
            "context": request.context_data
        },
        tickers=request.context_data.get("selected_tickers", []),
        created_at=datetime.utcnow()
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    
    return {
        "response": response,
        "insight_id": str(insight.id)
    }

@router.post("/insights/{insight_id}/share")
async def share_insight(
    insight_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Share insight to Nexus Community"""
    insight = db.query(Insight).filter(Insight.id == insight_id).first()
    if not insight or insight.user_id != current_user["uid"]:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    # Generate media if needed
    media_service = MediaService()
    media_urls = await media_service.generate_insight_media(insight)
    
    # Update insight
    insight.media_urls = media_urls
    insight.shared = True
    db.commit()
    
    # Create post in Nexus (Firestore)
    from app.services.nexus_service import NexusService
    nexus = NexusService()
    post_id = await nexus.create_post_from_insight(insight)
    
    return {
        "insight_id": str(insight.id),
        "post_id": post_id,
        "media_urls": media_urls
    }
```

### Step 6: Update Streamlit to Use New API

```python
# pages/dashboard_tabs/chatbot_tab.py (Modified)
import requests

class ChatbotInterface:
    def __init__(self):
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        # Keep local DataSourceManager for now (gradual migration)
        self.data_manager = DataSourceManager(self.cik_df)
    
    def _generate_response(self, prompt: str) -> str:
        """Generate AI response using new API"""
        context_data = self._gather_context_data()
        
        # Call new API endpoint
        response = requests.post(
            f"{self.api_base_url}/api/chat/analyze",
            json={
                "prompt": prompt,
                "context_data": context_data,
                "session_id": st.session_state.get("chat_session_id")
            },
            headers={"Authorization": f"Bearer {st.session_state.get('auth_token')}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            # Store insight_id for sharing
            st.session_state["last_insight_id"] = data["insight_id"]
            return data["response"]
        else:
            return "Error: Could not generate response"
    
    def _render_share_button(self):
        """Add share to Nexus button"""
        if "last_insight_id" in st.session_state:
            if st.button("📤 Share to Nexus Community"):
                response = requests.post(
                    f"{self.api_base_url}/api/chat/insights/{st.session_state['last_insight_id']}/share",
                    headers={"Authorization": f"Bearer {st.session_state.get('auth_token')}"}
                )
                if response.status_code == 200:
                    st.success("Insight shared to Nexus Community!")
```

---

## Frontend Migration (Next.js)

### Step 1: Initialize Next.js Project

```bash
npx create-next-app@latest finq-frontend --typescript --tailwind --app
cd finq-frontend
npm install @tanstack/react-query zustand socket.io-client
npm install @stripe/stripe-js recharts firebase
```

### Step 2: API Client Setup

```typescript
// lib/api/client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = {
  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = await getAuthToken(); // Firebase auth token
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  },
  
  // Financial endpoints
  financial: {
    getTicker: (ticker: string) => 
      apiClient.request(`/api/financial/ticker/${ticker}`),
    getMultipleTickers: (tickers: string[]) =>
      apiClient.request(`/api/financial/tickers?tickers=${tickers.join(',')}`),
  },
  
  // Chat endpoints
  chat: {
    analyze: (prompt: string, context: any) =>
      apiClient.request('/api/chat/analyze', {
        method: 'POST',
        body: JSON.stringify({ prompt, context_data: context }),
      }),
    shareInsight: (insightId: string) =>
      apiClient.request(`/api/chat/insights/${insightId}/share`, {
        method: 'POST',
      }),
  },
  
  // Nexus endpoints
  nexus: {
    getFeed: () => apiClient.request('/api/nexus/feed'),
    createPost: (content: string, insightId?: string) =>
      apiClient.request('/api/nexus/posts', {
        method: 'POST',
        body: JSON.stringify({ content, insight_id: insightId }),
      }),
  },
};
```

### Step 3: FinQ Chat Component

```typescript
// components/dashboard/FinQChat.tsx
'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';

export function FinQChat() {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedTickers, setSelectedTickers] = useState<string[]>([]);
  
  const analyzeMutation = useMutation({
    mutationFn: async (userPrompt: string) => {
      const context = {
        selected_tickers: selectedTickers,
        // ... other context
      };
      return apiClient.chat.analyze(userPrompt, context);
    },
    onSuccess: (data) => {
      setMessages(prev => [
        ...prev,
        { role: 'user', content: prompt },
        { role: 'assistant', content: data.response, insightId: data.insight_id }
      ]);
      setPrompt('');
    },
  });
  
  const shareMutation = useMutation({
    mutationFn: (insightId: string) => apiClient.chat.shareInsight(insightId),
    onSuccess: () => {
      alert('Shared to Nexus Community!');
    },
  });
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <p>{msg.content}</p>
            {msg.role === 'assistant' && msg.insightId && (
              <button
                onClick={() => shareMutation.mutate(msg.insightId!)}
                className="btn-share"
              >
                📤 Share to Nexus
              </button>
            )}
          </div>
        ))}
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          analyzeMutation.mutate(prompt);
        }}
      >
        <input
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ask about financial data..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```

### Step 4: Nexus Feed with Real-time Updates

```typescript
// components/nexus/Feed.tsx
'use client';

import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { io } from 'socket.io-client';
import { apiClient } from '@/lib/api/client';

export function NexusFeed() {
  const [socket, setSocket] = useState<any>(null);
  
  const { data: posts, refetch } = useQuery({
    queryKey: ['nexus-feed'],
    queryFn: () => apiClient.nexus.getFeed(),
  });
  
  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const newSocket = io(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000');
    
    newSocket.on('new_post', () => {
      refetch(); // Refresh feed when new post arrives
    });
    
    setSocket(newSocket);
    
    return () => newSocket.close();
  }, [refetch]);
  
  return (
    <div className="feed">
      {posts?.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          insight={post.insight} // If shared from Dashboard
        />
      ))}
    </div>
  );
}
```

---

## Database Migrations

### Alembic Setup

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Create insights and posts tables"

# Apply migration
alembic upgrade head
```

### Migration Script Example

```python
# alembic/versions/001_create_insights.py
"""Create insights and posts tables

Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('chat_session_id', sa.String(), nullable=True),
        sa.Column('content', postgresql.JSON(), nullable=False),
        sa.Column('summary', sa.String(), nullable=True),
        sa.Column('tickers', postgresql.JSON(), nullable=True),
        sa.Column('media_urls', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('shared', sa.Boolean(), default=False),
    )
    op.create_index('ix_insights_user_id', 'insights', ['user_id'])
    op.create_index('ix_insights_created_at', 'insights', ['created_at'])

def downgrade():
    op.drop_table('insights')
```

---

## Testing Strategy

### Backend Tests

```python
# tests/test_chat_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_endpoint():
    response = client.post(
        "/api/chat/analyze",
        json={
            "prompt": "What is AAPL's revenue?",
            "context_data": {"selected_tickers": ["AAPL"]}
        },
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    assert "insight_id" in response.json()
```

### Frontend Tests

```typescript
// __tests__/FinQChat.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { FinQChat } from '@/components/dashboard/FinQChat';

test('shares insight to Nexus', async () => {
  render(<FinQChat />);
  const input = screen.getByPlaceholderText('Ask about financial data...');
  fireEvent.change(input, { target: { value: 'Test question' } });
  fireEvent.submit(input);
  
  // Wait for response
  await waitFor(() => {
    expect(screen.getByText('📤 Share to Nexus')).toBeInTheDocument();
  });
});
```

---

## Deployment Checklist

### Backend Deployment
- [ ] Set up PostgreSQL database (Supabase/AWS RDS)
- [ ] Configure environment variables
- [ ] Run database migrations
- [ ] Deploy to Railway/Render
- [ ] Set up health check endpoint
- [ ] Configure CORS for frontend domain
- [ ] Set up monitoring (Sentry)

### Frontend Deployment
- [ ] Build Next.js app (`npm run build`)
- [ ] Deploy to Vercel
- [ ] Configure environment variables
- [ ] Set up custom domain
- [ ] Configure Firebase Auth domains
- [ ] Test authentication flow

### Integration
- [ ] Test API connectivity
- [ ] Verify authentication
- [ ] Test data sharing flow
- [ ] Load testing
- [ ] Security audit

---

This guide provides the foundation for migrating from Streamlit to a modern, scalable architecture while maintaining current functionality.


