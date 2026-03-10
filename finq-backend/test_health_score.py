import asyncio
import pandas as pd
from app.api.financial import get_data_source_manager
from app.api.health_scores import compute_finq_health_scores
import sys
import os

# Ensure the app context works
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test():
    dm = get_data_source_manager()
    print("Manager initialized")
    
    # Let's inspect AAPL fundamentals from the manager
    try:
        funds = await dm.get_fundamentals_data("AAPL")
        if funds.empty:
            print("AAPL Fundamentals are EMPTY")
        else:
            available_metrics = funds["Metric"].unique()
            print("Available Metrics for AAPL (Sample):", available_metrics[:20])
            
            # Print latest values for some key metrics
            print("\nLatest values:")
            for m in available_metrics:
                m_data = funds[funds["Metric"] == m].sort_values("FiscalPeriod")
                print(f"  {m}: {m_data.iloc[-1]['Value']}")
    except Exception as e:
        print("Error getting fundamentals:", e)

    df = await compute_finq_health_scores(dm)
    if not df.empty and "Ticker" in df.columns:
        print("\nScored tickers:", df["Ticker"].tolist())
        if "AAPL" in df["Ticker"].values:
            aapl_data = df[df["Ticker"] == "AAPL"]
            print("\nAAPL Score data:")
            print(aapl_data.to_dict('records'))
        else:
            print("\nAAPL is MISSING from scored dataframe.")

if __name__ == "__main__":
    asyncio.run(test())
