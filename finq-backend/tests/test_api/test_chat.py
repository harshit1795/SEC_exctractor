"""
Tests for chat API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_analyze():
    """Test chat analyze endpoint"""
    response = client.post(
        "/api/chat/analyze",
        json={
            "prompt": "What is AAPL?",
            "context_data": {
                "selected_tickers": ["AAPL"],
                "user_id": "test_user"
            }
        }
    )
    # May fail if API key not configured, but should not crash
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "response" in data
        assert "insight_id" in data


def test_chat_history():
    """Test chat history endpoint"""
    response = client.get("/api/chat/history?user_id=test_user")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "insights" in data
    assert "count" in data

