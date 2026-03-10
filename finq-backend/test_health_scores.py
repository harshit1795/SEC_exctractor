import asyncio
import pandas as pd
from app.api.health_scores import compute_finq_health_scores, get_custom_health_scores
from app.services.data_source_manager import DataSourceManager
from app.database import SessionLocal

async def main():
    """
    Test script for health score functions.
    """
    print("--- Starting Health Score Test Script ---")

    # Create a DataSourceManager instance
    data_manager = DataSourceManager()

    # --- Test compute_finq_health_scores ---
    print("\n--- Testing compute_finq_health_scores ---")
    try:
        # Test with a specific ticker
        print("\nTesting with ticker 'AAPL'...")
        finq_scores_aapl = await compute_finq_health_scores(data_manager, ticker="AAPL")
        if not finq_scores_aapl.empty:
            print("Successfully computed FinQ health score for AAPL:")
            print(finq_scores_aapl.head())
        else:
            print("compute_finq_health_scores returned an empty DataFrame for AAPL.")

        # Test with a category
        print("\nTesting with category 'Technology'...")
        finq_scores_tech = await compute_finq_health_scores(data_manager, category="Technology")
        if not finq_scores_tech.empty:
            print("Successfully computed FinQ health scores for Technology category:")
            print(finq_scores_tech.head())
        else:
            print("compute_finq_health_scores returned an empty DataFrame for Technology category.")

    except Exception as e:
        print(f"\n--- ERROR in compute_finq_health_scores test ---")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    # --- Test get_custom_health_scores ---
    print("\n--- Testing get_custom_health_scores ---")
    try:
        # Test with a specific ticker and metrics
        print("\nTesting with ticker 'MSFT' and custom metrics...")
        db = SessionLocal()
        custom_scores_msft = await get_custom_health_scores(
            metrics="Revenue Growth,Net Margin,P/E Ratio",
            weights="0.5,0.3,0.2",
            ticker="MSFT",
            limit=10, # Pass an integer for the limit
            db=db
        )
        if custom_scores_msft and custom_scores_msft.get("scores"):
            print("Successfully computed custom health score for MSFT:")
            print(custom_scores_msft)
        else:
            print("get_custom_health_scores returned no scores for MSFT.")
        db.close()

    except Exception as e:
        print(f"\n--- ERROR in get_custom_health_scores test ---")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


    print("\n--- Health Score Test Script Finished ---")

if __name__ == "__main__":
    asyncio.run(main())