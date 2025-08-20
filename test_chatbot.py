#!/usr/bin/env python3
"""
Test script for the enhanced FinQ Chatbot with MCP architecture
Run this to verify all components are working correctly
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Google Generative AI import failed: {e}")
        return False
    
    try:
        import yfinance as yf
        print("✅ yfinance imported successfully")
    except ImportError as e:
        print(f"❌ yfinance import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        from fred_data import get_fred_series, get_multiple_fred_series
        print("✅ FRED data module imported successfully")
    except ImportError as e:
        print(f"❌ FRED data module import failed: {e}")
        return False
    
    try:
        from auth import load_api_keys
        print("✅ Auth module imported successfully")
    except ImportError as e:
        print(f"❌ Auth module import failed: {e}")
        return False
    
    return True

def test_data_sources():
    """Test data source availability"""
    print("\n🔍 Testing data sources...")
    
    # Test data directory
    data_dir = Path("data")
    if data_dir.exists():
        tickers = [d.name for d in data_dir.iterdir() if d.is_dir()]
        print(f"✅ Data directory found with {len(tickers)} companies: {', '.join(tickers[:5])}{'...' if len(tickers) > 5 else ''}")
    else:
        print("❌ Data directory not found")
        return False
    
    # Test fundamentals file
    fundamentals_file = Path("fundamentals_tall.parquet")
    if fundamentals_file.exists():
        print(f"✅ Fundamentals data file found ({fundamentals_file.stat().st_size / (1024*1024):.1f} MB)")
    else:
        print("⚠️  Fundamentals data file not found (optional)")
    
    return True

def test_api_keys():
    """Test API key configuration"""
    print("\n🔍 Testing API key configuration...")
    
    # Check environment variables
    google_key = os.environ.get("GOOGLE_API_KEY")
    fred_key = os.environ.get("FRED_API_KEY")
    
    if google_key:
        print(f"✅ Google API key found (length: {len(google_key)})")
    else:
        print("⚠️  Google API key not found in environment variables")
    
    if fred_key:
        print(f"✅ FRED API key found (length: {len(fred_key)})")
    else:
        print("⚠️  FRED API key not found in environment variables")
    
    # Check secrets file
    secrets_file = Path(".streamlit/secrets.toml")
    if secrets_file.exists():
        print("✅ Streamlit secrets file found")
    else:
        print("⚠️  Streamlit secrets file not found")
    
    return True

def test_chatbot_components():
    """Test chatbot component classes"""
    print("\n🔍 Testing chatbot components...")
    
    try:
        # Import the chatbot components
        from pages.dashboard_tabs.chatbot_tab import DataSourceManager, FinancialAnalyzer, ChatbotInterface
        
        # Test DataSourceManager
        data_manager = DataSourceManager()
        print("✅ DataSourceManager instantiated successfully")
        
        # Test available tickers
        tickers = data_manager.get_available_tickers()
        print(f"✅ Available tickers retrieved: {len(tickers)} companies")
        
        # Test fundamentals data loading
        fundamentals = data_manager.get_fundamentals_data()
        if not fundamentals.empty:
            print(f"✅ Fundamentals data loaded: {len(fundamentals)} rows")
        else:
            print("⚠️  No fundamentals data available")
        
        print("✅ All chatbot components working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Chatbot component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_yahoo_finance():
    """Test Yahoo Finance data access"""
    print("\n🔍 Testing Yahoo Finance integration...")
    
    try:
        import yfinance as yf
        
        # Test basic ticker info
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        if info and 'longBusinessSummary' in info:
            print("✅ Yahoo Finance data access working")
            print(f"   Company: {info.get('longName', 'N/A')}")
            print(f"   Sector: {info.get('sector', 'N/A')}")
            return True
        else:
            print("❌ Yahoo Finance data incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Yahoo Finance test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting FinQ Chatbot Architecture Tests\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Data Source Tests", test_data_sources),
        ("API Key Tests", test_api_keys),
        ("Chatbot Component Tests", test_chatbot_components),
        ("Yahoo Finance Tests", test_yahoo_finance),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The chatbot architecture is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
