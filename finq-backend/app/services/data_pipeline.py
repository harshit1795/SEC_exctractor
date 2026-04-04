"""
Data Pipeline Service — writes fundamentals to PostgreSQL instead of parquet.

All data fetched via Yahoo Finance is upserted into the `fundamentals` table,
making the parquet file completely optional for local dev and irrelevant in
production (Render / Railway).
"""
import logging
import time
from typing import List, Dict, Optional

import pandas as pd
import sqlalchemy as sa
import yfinance as yf
from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Row-ID helper (must match seed_fundamentals.py and the model definition)
# ---------------------------------------------------------------------------

def _make_row_id(ticker: str, fiscal_period: str, metric: str, category: str) -> str:
    return f"{ticker}|{fiscal_period}|{metric}|{category}"


# ---------------------------------------------------------------------------
# DataPipeline
# ---------------------------------------------------------------------------

class DataPipeline:
    """Service for fetching and updating fundamentals data in PostgreSQL."""

    # ------------------------------------------------------------------
    # Internal: Yahoo Finance → long-format DataFrame
    # ------------------------------------------------------------------

    @staticmethod
    def _melt_quarterly_data(
        df: pd.DataFrame, ticker: str, category: str
    ) -> pd.DataFrame:
        """
        Convert a quarterly financial statement (wide format, columns = dates)
        into the tall/long format used by the `fundamentals` table.
        """
        if df is None or df.empty:
            return pd.DataFrame()

        # Ensure columns are Timestamps
        cols = []
        for c in df.columns:
            try:
                cols.append(pd.to_datetime(c))
            except (ValueError, TypeError):
                cols.append(pd.NaT)
        df = df.copy()
        df.columns = cols
        df = df.dropna(axis=1, how="all")

        records = []
        for metric, row in df.iterrows():
            for period_end, value in row.items():
                if pd.isna(period_end):
                    continue
                quarter = f"{period_end.year}Q{(period_end.month - 1) // 3 + 1}"
                records.append(
                    {
                        "ticker": str(ticker).upper(),
                        "period_end": period_end.date()
                        if isinstance(period_end, pd.Timestamp)
                        else None,
                        "fiscal_period": quarter,
                        "metric": str(metric),
                        "category": category,
                        "value": float(value) if pd.notna(value) else None,
                    }
                )
        return pd.DataFrame(records)

    async def fetch_ticker_quarterly(self, ticker: str) -> pd.DataFrame:
        """Fetch latest quarterly financials from Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker.upper())
            all_records: list[pd.DataFrame] = []

            for attr, cat in [
                ("quarterly_financials", "IncomeStatement"),
                ("quarterly_balance_sheet", "BalanceSheet"),
                ("quarterly_cashflow", "CashFlow"),
            ]:
                try:
                    raw = getattr(stock, attr)
                    if raw is not None and not raw.empty:
                        melted = self._melt_quarterly_data(raw, ticker, cat)
                        all_records.append(melted)
                        logger.info(
                            f"Fetched {len(melted)} {cat} records for {ticker}"
                        )
                except Exception as exc:
                    logger.warning(f"Error fetching {cat} for {ticker}: {exc}")

            if all_records:
                result = pd.concat(all_records, ignore_index=True)
                logger.info(f"Total records fetched for {ticker}: {len(result)}")
                return result

            logger.warning(f"No data fetched for {ticker}")
            return pd.DataFrame()

        except Exception as exc:
            logger.error(f"Error fetching quarterly data for {ticker}: {exc}")
            return pd.DataFrame()

    # ------------------------------------------------------------------
    # Internal: upsert a DataFrame into the fundamentals table
    # ------------------------------------------------------------------

    @staticmethod
    def _upsert_to_db(df: pd.DataFrame) -> int:
        """
        Bulk-upsert rows into the `fundamentals` table.
        Returns the number of rows processed.
        """
        from app.database import engine  # import here to keep module-level clean

        if df.empty:
            return 0

        rows = []
        for _, row in df.iterrows():
            ticker = str(row["ticker"]).strip().upper()
            fiscal_period = str(row["fiscal_period"]).strip()
            metric = str(row["metric"]).strip()
            category = str(row["category"]).strip()
            period_end = row.get("period_end")
            value = row["value"] if pd.notna(row.get("value")) else None
            row_id = _make_row_id(ticker, fiscal_period, metric, category)
            rows.append(
                {
                    "id": row_id,
                    "ticker": ticker,
                    "period_end": period_end,
                    "fiscal_period": fiscal_period,
                    "metric": metric,
                    "category": category,
                    "value": value,
                }
            )

        upsert_stmt = sa.text(
            """
            INSERT INTO fundamentals
                (id, ticker, period_end, fiscal_period, metric, category, value)
            VALUES
                (:id, :ticker, :period_end, :fiscal_period, :metric, :category, :value)
            ON CONFLICT (ticker, fiscal_period, metric, category)
            DO UPDATE SET
                value      = EXCLUDED.value,
                period_end = EXCLUDED.period_end
            """
        )

        with engine.begin() as conn:
            conn.execute(upsert_stmt, rows)

        return len(rows)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def update_ticker_data(
        self, ticker: str, force_refresh: bool = False
    ) -> Dict:
        """
        Fetch the latest quarterly data for *ticker* from Yahoo Finance and
        upsert it into the `fundamentals` table.

        `force_refresh=True` first deletes all existing rows for the ticker,
        then inserts the freshly fetched data.
        """
        try:
            new_data = await self.fetch_ticker_quarterly(ticker.upper())

            if new_data.empty:
                return {
                    "success": False,
                    "message": f"No data fetched for {ticker}",
                    "ticker": ticker,
                    "new_records": 0,
                }

            if force_refresh:
                from app.database import engine
                with engine.begin() as conn:
                    conn.execute(
                        sa.text(
                            "DELETE FROM fundamentals WHERE ticker = :ticker"
                        ),
                        {"ticker": ticker.upper()},
                    )
                logger.info(f"Deleted existing rows for {ticker} (force_refresh)")

            count = self._upsert_to_db(new_data)
            logger.info(f"Upserted {count} rows for {ticker} into DB")

            return {
                "success": True,
                "message": f"Successfully updated data for {ticker}",
                "ticker": ticker,
                "new_records": count,
            }

        except Exception as exc:
            logger.error(f"Error updating data for {ticker}: {exc}")
            return {
                "success": False,
                "message": f"Error updating {ticker}: {exc}",
                "ticker": ticker,
                "error": str(exc),
            }

    async def update_all_tickers(
        self,
        tickers: Optional[List[str]] = None,
        batch_size: int = 10,
        delay: float = 0.5,
    ) -> Dict:
        """
        Update fundamentals for multiple tickers.
        If *tickers* is None, reads the distinct ticker list from the DB.
        """
        if tickers is None:
            try:
                from app.database import engine
                with engine.connect() as conn:
                    rows = conn.execute(
                        sa.text(
                            "SELECT DISTINCT ticker FROM fundamentals ORDER BY ticker"
                        )
                    ).fetchall()
                tickers = [r[0] for r in rows] if rows else []
            except Exception as exc:
                logger.warning(f"Could not query tickers from DB: {exc}")
                tickers = []

            if not tickers:
                # Sensible default when the table is still empty
                tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]

        results = []
        total_updated = 0
        total_failed = 0

        logger.info(f"Starting batch update for {len(tickers)} tickers")

        for i, ticker in enumerate(tickers, 1):
            logger.info(f"[{i}/{len(tickers)}] Updating {ticker} …")
            result = await self.update_ticker_data(ticker, force_refresh=False)
            results.append(result)

            if result["success"]:
                total_updated += 1
            else:
                total_failed += 1

            if i < len(tickers):
                time.sleep(delay)

        return {
            "success": True,
            "total_tickers": len(tickers),
            "updated": total_updated,
            "failed": total_failed,
            "results": results,
        }

    async def get_latest_periods(self, ticker: Optional[str] = None) -> Dict:
        """
        Return info about the latest fiscal periods stored in the DB.
        """
        try:
            from app.database import engine

            with engine.connect() as conn:
                if ticker:
                    rows = conn.execute(
                        sa.text(
                            """
                            SELECT ticker, fiscal_period, COUNT(*) as cnt
                            FROM fundamentals
                            WHERE ticker = :ticker
                            GROUP BY ticker, fiscal_period
                            ORDER BY fiscal_period DESC
                            """
                        ),
                        {"ticker": ticker.upper()},
                    ).fetchall()
                else:
                    rows = conn.execute(
                        sa.text(
                            """
                            SELECT ticker, fiscal_period, COUNT(*) as cnt
                            FROM fundamentals
                            GROUP BY ticker, fiscal_period
                            ORDER BY ticker, fiscal_period DESC
                            """
                        )
                    ).fetchall()

            if not rows:
                return {
                    "latest_period": None,
                    "ticker_periods": {},
                    "total_records": 0,
                }

            ticker_periods: dict = {}
            for t, fp, cnt in rows:
                if t not in ticker_periods:
                    ticker_periods[t] = {"latest": fp, "all_periods": [], "count": 0}
                ticker_periods[t]["all_periods"].append(fp)
                ticker_periods[t]["count"] += 1

            all_periods = sorted({fp for _, fp, _ in rows})
            latest = all_periods[-1] if all_periods else None

            return {
                "latest_period": latest,
                "ticker_periods": ticker_periods,
                "total_records": sum(cnt for _, _, cnt in rows),
                "total_tickers": len(ticker_periods),
            }

        except Exception as exc:
            logger.error(f"Error getting latest periods: {exc}")
            return {"latest_period": None, "ticker_periods": {}, "total_records": 0}
