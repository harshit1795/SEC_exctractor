"""
Definition of Gemini Function Calling tools and router for the Agentic Workflow.
"""
from typing import Dict, Any, Callable
import google.generativeai as genai

# Define the tools available to the Gemini Model
FINANCIAL_TOOLS = [
    genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="get_stock_price",
                description="Get historical stock price data for a given ticker and period.",
                parameters={
                    "type": "OBJECT",
                    "properties": {
                        "ticker": {"type": "STRING", "description": "The stock ticker symbol (e.g., AAPL)."},
                        "period": {"type": "STRING", "description": "The time period (e.g., '1mo', '1y', 'ytd', 'max')."}
                    },
                    "required": ["ticker", "period"]
                }
            ),
            genai.types.FunctionDeclaration(
                name="get_company_financials",
                description="Get fundamental financial data (Income Statement, Balance Sheet, Cash Flow) for a company.",
                parameters={
                    "type": "OBJECT",
                    "properties": {
                        "ticker": {"type": "STRING", "description": "The stock ticker symbol."}
                    },
                    "required": ["ticker"]
                }
            ),
            genai.types.FunctionDeclaration(
                name="get_macro_indicators",
                description="Get macroeconomic data from FRED (e.g., GDP, Inflation, Interest Rates).",
                parameters={
                    "type": "OBJECT",
                    "properties": {
                        "series_ids": {
                            "type": "ARRAY", 
                            "items": {"type": "STRING"},
                            "description": "List of FRED series IDs (e.g., ['GDP', 'UNRATE', 'CPIAUCSL'])."
                        }
                    },
                    "required": ["series_ids"]
                }
            ),
            genai.types.FunctionDeclaration(
                name="get_sec_filings_overview",
                description="Get an overview of recent SEC filings and extraction metadata for a company.",
                parameters={
                    "type": "OBJECT",
                    "properties": {
                        "ticker": {"type": "STRING", "description": "The stock ticker symbol."}
                    },
                    "required": ["ticker"]
                }
            ),
            genai.types.FunctionDeclaration(
                name="get_10k_section_data",
                description="Get specific sections from the latest 10-K annual report for a company.",
                parameters={
                    "type": "OBJECT",
                    "properties": {
                        "ticker": {"type": "STRING", "description": "The stock ticker symbol."},
                        "sections": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"},
                            "description": "List of section keys (e.g. ['business', 'risk', 'mda', 'financials'])."
                        }
                    },
                    "required": ["ticker", "sections"]
                }
            )
        ]
    )
]

async def execute_tool(data_manager, function_call: Any) -> Dict[str, Any]:

    """Execute the tool function matched by name using the DataSourceManager."""
    name = function_call.name
    args = {k: v for k, v in function_call.args.items()}
    
    try:
        if name == "get_stock_price":
            return await data_manager.get_yahoo_finance_data(ticker=args["ticker"], period=args.get("period", "1y"))
        
        elif name == "get_company_financials":
            # get_fundamentals_data returns a Pandas DataFrame; we convert it via to_dict() inside the route or manager
            df = await data_manager.get_fundamentals_data(ticker=args["ticker"])
            if df.empty:
                return {"error": f"No fundamental data found for {args['ticker']}"}
            # Return last 3 periods to keep context size manageable
            return {"financials": df.tail(3).to_dict(orient="records")}
            
        elif name == "get_macro_indicators":
            df = await data_manager.get_fred_economic_data(series_ids=args["series_ids"])
            if df.empty:
                return {"error": "No macro data found."}
            return {"macro_data": df.tail(12).to_dict(orient="records")} # Last 12 periods
            
        elif name == "get_sec_filings_overview":
            return await data_manager.get_sec_filing_data(ticker=args["ticker"])
            
        elif name == "get_10k_section_data":
            return await data_manager.get_10k_section_data(ticker=args["ticker"], sections=args["sections"])
            
        else:
            return {"error": f"Unknown tool: {name}"}
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}
