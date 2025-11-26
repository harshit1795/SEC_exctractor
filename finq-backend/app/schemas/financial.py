"""
Pydantic schemas for financial data endpoints
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime


class TickerDataResponse(BaseModel):
    """Response schema for ticker data"""
    ticker: str
    period: str
    data: Dict[str, Any]
    cached: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MultipleTickersResponse(BaseModel):
    """Response schema for multiple tickers"""
    tickers: List[str]
    period: str
    data: Dict[str, Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FredDataResponse(BaseModel):
    """Response schema for FRED data"""
    series_ids: List[str]
    start_date: str
    end_date: str
    data: List[Dict[str, Any]]  # DataFrame converted to list of dicts
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SecFilingResponse(BaseModel):
    """Response schema for SEC filing data"""
    ticker: str
    filings: Dict[str, Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SecSectionResponse(BaseModel):
    """Response schema for SEC section data"""
    ticker: str
    sections: Dict[str, str]
    filing_type: str  # "10-K" or "10-Q"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FundamentalsResponse(BaseModel):
    """Response schema for fundamentals data"""
    ticker: str
    data: List[Dict[str, Any]]  # DataFrame converted to list of dicts
    timestamp: datetime = Field(default_factory=datetime.utcnow)

