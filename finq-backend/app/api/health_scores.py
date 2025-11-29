"""
Financial Health Score API endpoints
Calculates health scores for companies based on financial metrics
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.services.data_source_manager import DataSourceManager
from app.api.financial import get_data_source_manager
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health-scores", tags=["health-scores"])


def calculate_percentile_rank(series: pd.Series) -> pd.Series:
    """Calculate percentile rank (0-1) for a series"""
    return series.rank(pct=True, na_option="keep")


async def compute_finq_health_scores(
    data_manager: DataSourceManager,
    category: Optional[str] = None
) -> pd.DataFrame:
    """
    Compute FinQ health scores for all tickers
    
    Health Score Formula: (Growth_score + NetMargin_score + FCFMargin_score + (1 - DebtEquity_score)) / 4
    
    Args:
        data_manager: DataSourceManager instance
        category: Optional category filter (Technology, Manufacturing, etc.)
    
    Returns:
        DataFrame with health scores and metrics
    """
    try:
        # Load all fundamentals data at once (more efficient)
        from pathlib import Path
        from app.config import settings
        
        # Try multiple possible paths
        # Railway runs from finq-backend/, so check current directory first
        possible_paths = [
            Path("fundamentals_tall.parquet"),  # Current directory (finq-backend/)
            Path(settings.fundamentals_path),
            Path(__file__).parent.parent.parent.parent / settings.fundamentals_path,
            Path(__file__).parent.parent.parent.parent / "fundamentals_tall.parquet",
            Path("../fundamentals_tall.parquet"),
        ]
        
        fundamentals_path = None
        for path in possible_paths:
            if path.exists():
                fundamentals_path = path
                break
        
        if not fundamentals_path:
            logger.warning(f"Fundamentals file not found. Tried: {possible_paths}")
            return pd.DataFrame()
        
        logger.info(f"Loading all fundamentals from {fundamentals_path}")
        all_fundamentals = pd.read_parquet(fundamentals_path)
        
        # Note: Category filtering will be done after computing scores
        # by getting ticker metadata and mapping sectors to categories
        
        # Get unique tickers
        ticker_col = None
        for col in ['ticker', 'Ticker', 'TICKER']:
            if col in all_fundamentals.columns:
                ticker_col = col
                break
        
        if not ticker_col:
            logger.warning("No ticker column found in fundamentals data")
            return pd.DataFrame()
        
        tickers = all_fundamentals[ticker_col].unique()[:100]  # Limit to first 100 for performance
        
        records = []
        for ticker in tickers:
            try:
                # Filter fundamentals for this ticker
                ticker_fundamentals = all_fundamentals[all_fundamentals[ticker_col].str.upper() == ticker.upper()].copy()
                
                if ticker_fundamentals.empty or len(ticker_fundamentals) < 5:
                    continue
                
                # Pivot to wide format
                wide = ticker_fundamentals.pivot_table(
                    index="FiscalPeriod",
                    columns="Metric",
                    values="Value",
                    aggfunc="first"
                ).sort_index()
                
                if wide.empty or len(wide) < 5:
                    continue
                
                latest = wide.iloc[-1]
                
                # Get key metrics - try multiple variations
                revenue_col = None
                for col_name in ["Total Revenue", "Revenue", "Total Revenue (ttm)"]:
                    if col_name in wide.columns:
                        revenue_col = col_name
                        break
                
                if revenue_col is None:
                    continue
                
                # Calculate Growth (YoY - 5 quarters ago)
                try:
                    rev_latest = latest[revenue_col]
                    if len(wide) >= 5:
                        rev_prev = wide.iloc[-5][revenue_col]
                    else:
                        rev_prev = wide.iloc[0][revenue_col] if len(wide) > 0 else np.nan
                    
                    growth = (rev_latest - rev_prev) / abs(rev_prev) if pd.notna(rev_latest) and pd.notna(rev_prev) and rev_prev != 0 else np.nan
                except Exception:
                    growth = np.nan
                
                # Calculate Net Margin - try multiple variations
                try:
                    net_income = None
                    for col_name in ["Net Income", "Net Income (ttm)", "Net Income To Common"]:
                        if col_name in wide.columns:
                            net_income = latest.get(col_name, np.nan)
                            break
                    
                    net_margin = net_income / rev_latest if pd.notna(rev_latest) and rev_latest != 0 and pd.notna(net_income) else np.nan
                except Exception:
                    net_margin = np.nan
                
                # Calculate FCF Margin - try multiple variations
                try:
                    fcf = None
                    for col_name in ["Free Cash Flow", "Free Cash Flow (ttm)", "FreeCashFlow"]:
                        if col_name in wide.columns:
                            fcf = latest.get(col_name, np.nan)
                            break
                    
                    fcf_margin = fcf / rev_latest if pd.notna(rev_latest) and rev_latest != 0 and pd.notna(fcf) else np.nan
                except Exception:
                    fcf_margin = np.nan
                
                # Calculate Debt to Equity - try multiple variations
                # Check all available metric names first
                available_metrics = list(wide.columns)
                debt_equity = np.nan
                
                try:
                    # Try to find liabilities metric - check all variations
                    total_liabilities = None
                    liability_variations = [
                        "Total Liabilities",
                        "Total Liabilities Net Minority Interest", 
                        "Total Liab",
                        "Total Liabilities And Equity",
                    ]
                    # Also check for any metric containing "liabilit"
                    for col_name in available_metrics:
                        if col_name in liability_variations:
                            total_liabilities = latest.get(col_name, np.nan)
                            if pd.notna(total_liabilities):
                                break
                    
                    # If not found in exact matches, search for partial matches
                    if total_liabilities is None or pd.isna(total_liabilities):
                        for col_name in available_metrics:
                            if "liabilit" in col_name.lower() and "total" in col_name.lower():
                                total_liabilities = latest.get(col_name, np.nan)
                                if pd.notna(total_liabilities):
                                    logger.debug(f"Found liabilities metric: {col_name} for {ticker}")
                                    break
                    
                    # Try to find equity metric - check all variations
                    shareholder_equity = None
                    equity_variations = [
                        "Shareholder Equity",
                        "Total Stockholder Equity",
                        "Total Stockholders Equity",
                        "Stockholders Equity",
                        "Stockholder Equity",
                    ]
                    # Also check for any metric containing "equit" or "stockholder"
                    for col_name in available_metrics:
                        if col_name in equity_variations:
                            shareholder_equity = latest.get(col_name, np.nan)
                            if pd.notna(shareholder_equity):
                                break
                    
                    # If not found in exact matches, search for partial matches
                    if shareholder_equity is None or pd.isna(shareholder_equity):
                        for col_name in available_metrics:
                            if ("equit" in col_name.lower() or "stockholder" in col_name.lower()) and "total" in col_name.lower():
                                shareholder_equity = latest.get(col_name, np.nan)
                                if pd.notna(shareholder_equity):
                                    logger.debug(f"Found equity metric: {col_name} for {ticker}")
                                    break
                    
                    # Calculate ratio
                    if pd.notna(shareholder_equity) and shareholder_equity != 0 and pd.notna(total_liabilities):
                        debt_equity = total_liabilities / shareholder_equity
                    else:
                        logger.debug(f"Could not calculate D/E for {ticker}: liabilities={total_liabilities}, equity={shareholder_equity}")
                except Exception as e:
                    logger.debug(f"Error calculating D/E for {ticker}: {e}")
                    debt_equity = np.nan
                
                # Build insight text
                insight_parts = []
                if pd.notna(growth):
                    insight_parts.append(f"Revenue {'grew' if growth > 0 else 'declined'} {growth*100:,.1f}% YoY")
                if pd.notna(net_margin):
                    insight_parts.append(f"Net margin {net_margin*100:,.1f}%")
                if pd.notna(fcf_margin):
                    insight_parts.append(f"FCF margin {fcf_margin*100:,.1f}%")
                if pd.notna(debt_equity):
                    insight_parts.append(f"D/E {debt_equity:,.2f}")
                
                risk_flags = []
                if pd.notna(growth) and growth < 0:
                    risk_flags.append("Revenue contraction")
                if pd.notna(net_margin) and net_margin < 0:
                    risk_flags.append("Negative profitability")
                if pd.notna(fcf_margin) and fcf_margin < 0:
                    risk_flags.append("Cash burn")
                if pd.notna(debt_equity) and debt_equity > 1.5:
                    risk_flags.append("High leverage")
                
                insight = "; ".join(insight_parts)
                if risk_flags:
                    insight += " • Risk: " + ", ".join(risk_flags)
                
                records.append({
                    "Ticker": ticker,
                    "Growth": growth,
                    "NetMargin": net_margin,
                    "FCFMargin": fcf_margin,
                    "DebtEquity": debt_equity,
                    "Insight": insight,
                })
            except Exception as e:
                logger.warning(f"Error processing {ticker}: {e}")
                continue
        
        if not records:
            return pd.DataFrame()
        
        score_df = pd.DataFrame(records)
        
        # Calculate percentile ranks
        for col in ["Growth", "NetMargin", "FCFMargin"]:
            score_df[col + "_score"] = calculate_percentile_rank(score_df[col])
        
        # DebtEquity: lower is better, so invert
        score_df["DebtEquity_score"] = 1 - calculate_percentile_rank(score_df["DebtEquity"])
        
        # Calculate overall health score
        score_cols = [c for c in score_df.columns if c.endswith("_score")]
        score_df["HealthScore"] = score_df[score_cols].mean(axis=1, skipna=True)
        
        # Remove rows with no health score
        score_df = score_df.dropna(subset=["HealthScore"])
        
        # Add category information by getting ticker metadata
        # Map sectors to categories
        sector_map = {
            "Information Technology": "Technology",
            "Technology": "Technology",
            "Communication Services": "Technology",
            "Consumer Discretionary": "Manufacturing",
            "Consumer Cyclical": "Manufacturing",
            "Industrials": "Manufacturing",
            "Materials": "Manufacturing",
            "Energy": "Manufacturing",
            "Health Care": "Public Sector",
            "Healthcare": "Public Sector",
            "Utilities": "Public Sector",
            "Real Estate": "Public Sector",
            "Financials": "Finance",
            "Financial Services": "Finance",
            "Consumer Staples": "Finance",
        }
        
        # Try to get sector info from ticker data (batch process for efficiency)
        ticker_categories = {}
        unique_tickers = score_df["Ticker"].unique()
        
        # First, try to get sector from fundamentals data if it has a Sector column
        if "Sector" in all_fundamentals.columns:
            logger.info("Using Sector column from fundamentals data")
            for ticker in unique_tickers:
                ticker_data = all_fundamentals[all_fundamentals[ticker_col].str.upper() == ticker.upper()]
                if not ticker_data.empty:
                    sector = ticker_data["Sector"].iloc[0] if "Sector" in ticker_data.columns else None
                    if sector and pd.notna(sector):
                        ticker_categories[ticker] = sector_map.get(str(sector), "Other")
                    else:
                        ticker_categories[ticker] = "Other"
                else:
                    ticker_categories[ticker] = "Other"
        else:
            # Fallback: Get sector info from ticker data API
            logger.info(f"Fundamentals data doesn't have Sector column, fetching from API for {len(unique_tickers)} tickers")
            # Process in smaller batches to avoid overwhelming the API
            for i, ticker in enumerate(unique_tickers[:100]):  # Increased limit
                try:
                    ticker_data = await data_manager.get_yahoo_finance_data(ticker, "1y")
                    if ticker_data and "info" in ticker_data:
                        sector = ticker_data["info"].get("sector", "Unknown")
                        ticker_categories[ticker] = sector_map.get(sector, "Other")
                    else:
                        ticker_categories[ticker] = "Other"
                except Exception as e:
                    logger.debug(f"Could not get sector for {ticker}: {e}")
                    ticker_categories[ticker] = "Other"
        
        # Set category for remaining tickers to "Other"
        for ticker in unique_tickers:
            if ticker not in ticker_categories:
                ticker_categories[ticker] = "Other"
        
        # Add category column
        score_df["Category"] = score_df["Ticker"].map(ticker_categories).fillna("Other")
        
        # Log category distribution before filtering
        logger.info(f"Category distribution before filter: {score_df['Category'].value_counts().to_dict()}")
        
        # Filter by category if provided
        if category:
            before_filter = len(score_df)
            score_df = score_df[score_df["Category"] == category]
            after_filter = len(score_df)
            logger.info(f"Category filter '{category}': {before_filter} -> {after_filter} tickers")
            if after_filter == 0:
                available_cats = list(set(ticker_categories.values()))
                logger.warning(f"No tickers found for category '{category}'. Available categories: {available_cats}")
            logger.info(f"Category filter '{category}': {before_filter} -> {after_filter} tickers")
            if after_filter == 0:
                available_cats = score_df["Category"].unique() if len(score_df) > 0 else []
                logger.warning(f"No tickers found for category '{category}'. Available categories: {list(available_cats)}")
        
        return score_df.sort_values("HealthScore", ascending=False)
        
    except Exception as e:
        logger.error(f"Error computing health scores: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error computing health scores: {str(e)}")


@router.get("/finq")
async def get_finq_health_scores(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, description="Number of top companies to return"),
    db: Session = Depends(get_db)
):
    """
    Get FinQ health scores for all companies
    
    Health Score Formula: (Growth_score + NetMargin_score + FCFMargin_score + (1 - DebtEquity_score)) / 4
    
    Args:
        category: Optional category filter
        limit: Number of top companies to return
        db: Database session
    
    Returns:
        List of companies with health scores
    """
    try:
        from app.api.financial import get_data_source_manager
        data_manager = get_data_source_manager()
        score_df = await compute_finq_health_scores(data_manager, category)
        
        if score_df.empty:
            return {"scores": [], "message": "No health scores available"}
        
        # Convert to list of dicts
        top_scores = score_df.head(limit)
        scores_list = []
        for _, row in top_scores.iterrows():
            scores_list.append({
                "ticker": row["Ticker"],
                "healthScore": float(row["HealthScore"]) if pd.notna(row["HealthScore"]) else None,
                "growth": float(row["Growth"]) if pd.notna(row["Growth"]) else None,
                "netMargin": float(row["NetMargin"]) if pd.notna(row["NetMargin"]) else None,
                "fcfMargin": float(row["FCFMargin"]) if pd.notna(row["FCFMargin"]) else None,
                "debtEquity": float(row["DebtEquity"]) if pd.notna(row["DebtEquity"]) else None,
                "insight": row.get("Insight", ""),
            })
        
        return {"scores": scores_list, "total": len(score_df)}
        
    except Exception as e:
        logger.error(f"Error getting health scores: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting health scores: {str(e)}")


@router.get("/custom")
async def get_custom_health_scores(
    metrics: str = Query(..., description="Comma-separated list of metrics"),
    limit: int = Query(10, description="Number of top companies to return"),
    db: Session = Depends(get_db)
):
    """
    Get custom health scores based on user-selected metrics
    
    Args:
        metrics: Comma-separated list of metric names
        limit: Number of top companies to return
        db: Database session
    
    Returns:
        List of companies with custom health scores
    """
    try:
        metric_list = [m.strip() for m in metrics.split(",") if m.strip()]
        
        if not metric_list:
            raise HTTPException(status_code=400, detail="No metrics provided")
        
        from app.api.financial import get_data_source_manager
        data_manager = get_data_source_manager()
        tickers = data_manager.get_available_tickers()
        
        records = []
        for ticker in tickers[:100]:  # Limit for performance
            try:
                fundamentals = await data_manager.get_fundamentals_data(ticker)
                
                if fundamentals.empty:
                    continue
                
                # Filter to selected metrics
                filtered = fundamentals[fundamentals["Metric"].isin(metric_list)]
                
                if filtered.empty:
                    continue
                
                # Get latest values for each metric
                latest_values = {}
                for metric in metric_list:
                    metric_data = filtered[filtered["Metric"] == metric]
                    if not metric_data.empty:
                        # Get most recent value
                        latest = metric_data.sort_values("FiscalPeriod").iloc[-1]
                        latest_values[metric] = latest["Value"]
                
                if not latest_values:
                    continue
                
                records.append({
                    "Ticker": ticker,
                    **latest_values
                })
            except Exception as e:
                logger.warning(f"Error processing {ticker}: {e}")
                continue
        
        if not records:
            return {"scores": [], "message": "No data available for selected metrics"}
        
        score_df = pd.DataFrame(records)
        
        # Calculate percentile ranks for each metric
        for metric in metric_list:
            if metric in score_df.columns:
                score_df[metric + "_score"] = calculate_percentile_rank(score_df[metric])
        
        # Calculate average health score
        score_cols = [c for c in score_df.columns if c.endswith("_score")]
        if score_cols:
            score_df["HealthScore"] = score_df[score_cols].mean(axis=1, skipna=True)
            score_df = score_df.dropna(subset=["HealthScore"])
            score_df = score_df.sort_values("HealthScore", ascending=False)
        
        # Convert to response format
        top_scores = score_df.head(limit)
        scores_list = []
        for _, row in top_scores.iterrows():
            score_data: Dict[str, Any] = {
                "ticker": row["Ticker"],
                "healthScore": float(row["HealthScore"]) if pd.notna(row["HealthScore"]) else None,
            }
            
            # Add metric values
            for metric in metric_list:
                if metric in row:
                    score_data[metric] = float(row[metric]) if pd.notna(row[metric]) else None
            
            scores_list.append(score_data)
        
        return {"scores": scores_list, "total": len(score_df)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error computing custom health scores: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error computing custom health scores: {str(e)}")

