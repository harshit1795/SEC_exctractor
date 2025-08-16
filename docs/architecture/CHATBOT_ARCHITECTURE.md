# FinQ Chatbot - MCP Architecture Documentation

## Overview

The FinQ Chatbot has been completely redesigned using **Model Context Protocol (MCP) architecture** to provide universal access to financial data sources and intelligent analysis capabilities.

## 🏗️ Architecture Components

### 1. DataSourceManager (MCP Core)
The central data access layer that provides unified access to multiple financial data sources:

- **Yahoo Finance Integration**: Real-time stock data, financial statements, earnings
- **FRED Economic Data**: Federal Reserve economic indicators
- **SEC Filing Data**: Local storage of company filings
- **Fundamentals Data**: Historical financial metrics from parquet files
- **Intelligent Caching**: 5-minute TTL caching for performance optimization

### 2. FinancialAnalyzer (AI Engine)
Advanced AI-powered analysis using Google's Gemini model:

- **Context-Aware Prompts**: Dynamic prompt building based on available data
- **Multi-Source Analysis**: Combines data from all available sources
- **Professional Financial Expertise**: Specialized in financial analysis and insights
- **Risk Assessment**: Identifies potential risks and opportunities

### 3. ChatbotInterface (User Experience)
Streamlit-based interface with enhanced user experience:

- **Data Source Selection**: Choose companies and economic indicators
- **Context-Aware Chat**: AI responses based on selected data sources
- **Quick Actions**: Pre-built analysis templates
- **Real-time Data Loading**: Dynamic data fetching and caching

## 🚀 Key Features

### Universal Data Access
- **No Limitations**: Access any datapoint from multiple sources
- **Dynamic Context**: AI adapts responses based on available data
- **Real-time Updates**: Live data from Yahoo Finance and FRED
- **Historical Analysis**: Access to years of financial data

### Intelligent Analysis
- **Multi-Dimensional Insights**: Combines company, market, and economic data
- **Trend Identification**: Automatic pattern recognition and analysis
- **Risk Assessment**: Comprehensive risk evaluation
- **Actionable Recommendations**: Data-driven investment insights

### Enhanced User Experience
- **Context Selection**: Choose relevant data sources for analysis
- **Quick Actions**: One-click analysis templates
- **Chat History**: Persistent conversation context
- **Loading States**: Clear feedback during data processing

## 📊 Data Sources

### 1. Company Financial Data (Yahoo Finance)
```python
# Available data types
- Company info and business summary
- Financial statements (annual/quarterly)
- Balance sheets and cash flow
- Stock price history
- Earnings and recommendations
```

### 2. Economic Indicators (FRED)
```python
# Key economic series
- GDP (GDP, GDPC1)
- Unemployment (UNRATE)
- Inflation (CPIAUCSL)
- Interest rates (DGS10, FEDFUNDS)
- Custom series support
```

### 3. SEC Filings (Local Storage)
```python
# Available companies
- AAPL, AMZN, GOOGL, MSFT, NVDA, TSLA, V, BRK-B, META
- Annual and quarterly filings
- Metadata and file information
```

### 4. Fundamentals Data
```python
# Historical metrics
- Income statement data
- Balance sheet metrics
- Cash flow information
- Quarterly and annual data
```

## 🔧 Configuration

### API Keys Setup
Create `.streamlit/secrets.toml` with your API keys:

```toml
# Google Generative AI API Key
GOOGLE_API_KEY = "your_google_api_key_here"

# FRED API Key
FRED_API_KEY = "your_fred_api_key_here"

# SEC API Key (optional)
SEC_API_KEY = "your_sec_api_key_here"
```

### Environment Variables
Alternatively, set environment variables:

```bash
export GOOGLE_API_KEY="your_key_here"
export FRED_API_KEY="your_key_here"
```

## 💡 Usage Examples

### Basic Company Analysis
1. **Select Company**: Choose from available tickers
2. **Load Data**: Click "Load Company Data"
3. **Ask Questions**: "What is the company's financial health?"
4. **Get Insights**: AI provides comprehensive analysis

### Market Analysis
1. **Select Economic Indicators**: Choose FRED series
2. **Load Economic Data**: Fetch current economic data
3. **Ask Questions**: "How do current economic conditions affect markets?"
4. **Receive Analysis**: AI combines company and economic data

### Quick Actions
- **Company Overview**: Comprehensive business analysis
- **Market Analysis**: Economic and market insights
- **Investment Ideas**: Data-driven recommendations

## 🏛️ MCP Architecture Benefits

### 1. Modularity
- **Separation of Concerns**: Clear boundaries between data, analysis, and UI
- **Easy Maintenance**: Independent component updates
- **Scalability**: Add new data sources without affecting other components

### 2. Data Consistency
- **Unified Interface**: Single access point for all data sources
- **Caching Strategy**: Optimized performance with intelligent caching
- **Error Handling**: Graceful degradation when sources are unavailable

### 3. AI Enhancement
- **Context Awareness**: AI understands available data sources
- **Dynamic Prompts**: Adapts analysis based on data availability
- **Multi-Source Synthesis**: Combines insights from multiple sources

### 4. User Experience
- **Intuitive Interface**: Clear data source selection
- **Real-time Feedback**: Loading states and progress indicators
- **Persistent Context**: Maintains analysis context across sessions

## 🔍 Advanced Features

### Custom Analysis
```python
# The AI can handle complex queries like:
- "Compare AAPL and MSFT financial performance over the last 5 years"
- "How do interest rate changes affect tech sector valuations?"
- "What are the key risks for the current portfolio based on economic indicators?"
```

### Data Export
- **Analysis Results**: Export AI insights to markdown
- **Data Snapshots**: Save current data context
- **Report Generation**: Create comprehensive financial reports

### Integration Capabilities
- **Webhook Support**: Real-time data updates
- **API Endpoints**: RESTful API for external integrations
- **Database Storage**: Persistent storage of analysis results

## 🚨 Error Handling

### Graceful Degradation
- **Source Failures**: Continue operation with available data
- **API Limits**: Intelligent retry mechanisms
- **Network Issues**: Offline mode with cached data

### User Feedback
- **Clear Error Messages**: Informative error descriptions
- **Recovery Suggestions**: Actionable steps to resolve issues
- **Fallback Options**: Alternative data sources when primary fails

## 🔮 Future Enhancements

### Planned Features
- **Machine Learning Models**: Predictive analytics and forecasting
- **Natural Language Queries**: Conversational data exploration
- **Real-time Alerts**: Market condition notifications
- **Portfolio Integration**: Multi-asset portfolio analysis

### Extensibility
- **Plugin System**: Third-party data source integration
- **Custom Models**: User-defined analysis models
- **API Marketplace**: Community-contributed data sources

## 📚 Best Practices

### 1. Data Source Selection
- **Relevance**: Choose data sources relevant to your analysis
- **Freshness**: Consider data update frequency
- **Completeness**: Ensure sufficient data for meaningful analysis

### 2. Question Formulation
- **Specificity**: Ask specific questions for better insights
- **Context**: Provide relevant context for complex queries
- **Follow-up**: Use AI responses to refine your analysis

### 3. Performance Optimization
- **Caching**: Leverage built-in caching for repeated queries
- **Batch Loading**: Load multiple data sources simultaneously
- **Selective Updates**: Update only necessary data sources

## 🆘 Troubleshooting

### Common Issues
1. **API Key Errors**: Verify API keys in secrets.toml
2. **Data Loading Failures**: Check network connectivity and API limits
3. **AI Response Errors**: Verify Google API key and quota
4. **Performance Issues**: Clear browser cache and restart app

### Debug Mode
Enable debug logging for detailed error information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

For technical support or feature requests:
- **Documentation**: Check this file and inline code comments
- **Logs**: Review Streamlit logs for error details
- **Community**: Share issues and solutions with the team

---

*This architecture represents a significant upgrade from the previous limited chatbot, providing enterprise-grade financial analysis capabilities with universal data access.*
