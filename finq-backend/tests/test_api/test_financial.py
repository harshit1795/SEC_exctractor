"""
Tests for financial API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_ticker_data():
    """Test single ticker endpoint"""
    response = client.get("/api/financial/ticker/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert "data" in data
    assert "info" in data["data"]


def test_get_multiple_tickers():
    """Test multiple tickers endpoint"""
    response = client.get("/api/financial/tickers?tickers=AAPL,MSFT")
    assert response.status_code == 200
    data = response.json()
    assert "AAPL" in data["tickers"]
    assert "MSFT" in data["tickers"]
    assert "data" in data


def test_get_available_tickers():
    """Test available tickers endpoint"""
    response = client.get("/api/financial/tickers/available")
    assert response.status_code == 200
    data = response.json()
    assert "tickers" in data
    assert "count" in data


def test_get_fred_data():
    """Test FRED data endpoint"""
    response = client.get(
        "/api/financial/fred?series_ids=UNRATE&start_date=2023-01-01&end_date=2024-01-01"
    )
    # May return 404 if no data, but should not return 500
    assert response.status_code in [200, 404]


def test_invalid_ticker():
    """Test error handling for invalid ticker"""
    response = client.get("/api/financial/ticker/INVALIDTICKER123")
    # Should return 404 or 500, not crash
    assert response.status_code in [404, 500]

