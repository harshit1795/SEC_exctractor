# FinQ Frontend - Demo UI

A simple, beautiful web interface to interact with the FinQ FastAPI backend.

## Features

- 📈 **Stock Data**: Get real-time financial data for any ticker
- 📊 **Economic Data**: Fetch FRED economic indicators
- 💬 **AI Analysis**: Get AI-powered financial insights
- 📋 **Available Tickers**: Browse available ticker symbols

## Access

1. **Start the FastAPI backend** (if not already running):
   ```bash
   cd finq-backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Start the frontend server**:
   ```bash
   cd finq-backend
   python3 -m http.server 8080 --directory frontend
   ```

3. **Open in browser**: http://localhost:8080

## Usage

### Stock Data Tab
- Enter a ticker symbol (e.g., AAPL, MSFT, GOOGL)
- Select a time period
- Click "Get Stock Data" to see company information, financials, and metrics

### Economic Data Tab
- Enter FRED series IDs (comma-separated)
- Set date range
- Click "Get Economic Data" to fetch economic indicators

### AI Analysis Tab
- Enter your question about a company or financial topic
- Optionally specify tickers to analyze
- Click "Analyze with AI" to get AI-powered insights

### Available Tickers Tab
- Click "Load Available Tickers" to see all available ticker symbols

## API Endpoints Used

- `GET /api/health` - Health check
- `GET /api/financial/ticker/{ticker}` - Stock data
- `GET /api/financial/fred` - Economic data
- `POST /api/chat/analyze` - AI analysis
- `GET /api/financial/tickers/available` - Available tickers

## Notes

- The frontend connects to `http://localhost:8000` (FastAPI backend)
- Make sure CORS is configured in the backend (already done)
- The UI is responsive and works on mobile devices

