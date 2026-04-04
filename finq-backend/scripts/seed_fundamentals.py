#!/usr/bin/env python3
"""
Seeder: fundamentals_tall.parquet → PostgreSQL (Neon/Supabase)
================================================================
Reads the local parquet file and bulk-inserts all rows into the
`fundamentals` table using psycopg2's efficient COPY protocol via
execute_values for maximum throughput.

Usage (from finq-backend/ directory):
    source venv/bin/activate
    python scripts/seed_fundamentals.py

Optional env overrides:
    PARQUET_PATH=path/to/fundamentals_tall.parquet   (default: auto-detect)
    BATCH_SIZE=5000                                   (default: 5000)
    TRUNCATE_FIRST=true                               (default: false)
"""

import os
import sys
import time
import logging
from pathlib import Path

# ── Make sure we can import app modules ──────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.environ["DATABASE_URL"]          # must be set
BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "5000"))
TRUNCATE_FIRST: bool = os.getenv("TRUNCATE_FIRST", "false").lower() == "true"

# Parquet path: env override > auto-detect near this script
_PARQUET_CANDIDATES = [
    os.getenv("PARQUET_PATH", ""),
    str(Path(__file__).parent.parent / "fundamentals_tall.parquet"),
    str(Path(__file__).parent.parent.parent / "fundamentals_tall.parquet"),
]
PARQUET_PATH: Path | None = next(
    (Path(p) for p in _PARQUET_CANDIDATES if p and Path(p).exists()), None
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_row_id(ticker: str, fiscal_period: str, metric: str, category: str) -> str:
    """Deterministic surrogate PK matching the model definition."""
    return f"{ticker}|{fiscal_period}|{metric}|{category}"


def _build_dsn(url: str) -> str:
    """
    Strip query-string params that psycopg2 doesn't accept in DSN form
    (e.g. channel_binding) but keep sslmode.
    """
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    # Keep only params psycopg2 understands
    allowed = {"sslmode", "sslcert", "sslkey", "sslrootcert", "application_name"}
    filtered = {k: v for k, v in params.items() if k in allowed}
    new_query = urlencode({k: v[0] for k, v in filtered.items()})
    clean = parsed._replace(query=new_query)
    return urlunparse(clean)


def load_parquet(path: Path) -> pd.DataFrame:
    logger.info(f"Loading parquet from {path} …")
    df = pd.read_parquet(path)
    # Normalise column names to lowercase
    df.columns = [c.lower() for c in df.columns]
    # Rename to match our DB columns
    rename_map = {
        "ticker": "ticker",
        "periodend": "period_end",
        "fiscalperiod": "fiscal_period",
        "metric": "metric",
        "category": "category",
        "value": "value",
    }
    df = df.rename(columns=rename_map)
    required = {"ticker", "fiscal_period", "metric", "category", "value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Parquet is missing columns: {missing}")
    logger.info(f"Loaded {len(df):,} rows, {df['ticker'].nunique()} tickers")
    return df


def seed(df: pd.DataFrame, conn) -> None:
    cur = conn.cursor()

    if TRUNCATE_FIRST:
        logger.warning("TRUNCATE_FIRST=true — deleting all existing rows …")
        cur.execute("TRUNCATE TABLE fundamentals RESTART IDENTITY;")
        conn.commit()

    # Deduplicate rows because PostgreSQL ON CONFLICT DO UPDATE requires all
    # inserted rows in a single statement to be strictly unique on the conflict target.
    # We keep the 'last' occurrence, which assumes order in the file tends towards newer.
    df = df.drop_duplicates(subset=["ticker", "fiscal_period", "metric", "category"], keep="last")
    total = len(df)
    logger.info(f"Deduplicated to {total:,} unique rows.")

    inserted = 0
    skipped = 0
    t0 = time.time()

    for batch_start in range(0, total, BATCH_SIZE):
        batch = df.iloc[batch_start : batch_start + BATCH_SIZE]

        rows = []
        for _, row in batch.iterrows():
            ticker = str(row["ticker"]).strip().upper()
            fiscal_period = str(row["fiscal_period"]).strip()
            metric = str(row["metric"]).strip()
            category = str(row["category"]).strip()
            period_end = row.get("period_end")
            value = row["value"] if pd.notna(row["value"]) else None
            row_id = _make_row_id(ticker, fiscal_period, metric, category)

            # period_end: convert to date string or None
            if pd.notna(period_end) and period_end:
                try:
                    period_end_str = pd.Timestamp(period_end).date().isoformat()
                except Exception:
                    period_end_str = None
            else:
                period_end_str = None

            rows.append((row_id, ticker, period_end_str, fiscal_period, metric, category, value))

        # Upsert: on conflict (unique key) update value and period_end
        execute_values(
            cur,
            """
            INSERT INTO fundamentals
                (id, ticker, period_end, fiscal_period, metric, category, value)
            VALUES %s
            ON CONFLICT (ticker, fiscal_period, metric, category)
            DO UPDATE SET
                value      = EXCLUDED.value,
                period_end = EXCLUDED.period_end
            """,
            rows,
            template="(%s,%s,%s::date,%s,%s,%s,%s)",
            page_size=BATCH_SIZE,
        )
        conn.commit()

        inserted += len(rows)
        elapsed = time.time() - t0
        pct = inserted / total * 100
        rps = inserted / elapsed if elapsed > 0 else 0
        logger.info(
            f"  {inserted:,}/{total:,} rows ({pct:.1f}%) — {rps:,.0f} rows/s"
        )

    logger.info(
        f"Seed complete: {inserted:,} rows inserted/updated, "
        f"{skipped} skipped in {time.time()-t0:.1f}s"
    )
    cur.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if PARQUET_PATH is None:
        logger.error(
            "Could not find fundamentals_tall.parquet. "
            "Set PARQUET_PATH env var or place the file in finq-backend/."
        )
        sys.exit(1)

    logger.info(f"Database URL: {DATABASE_URL[:DATABASE_URL.find('@')+1]}***")
    logger.info(f"Batch size  : {BATCH_SIZE:,}")
    logger.info(f"Truncate    : {TRUNCATE_FIRST}")

    df = load_parquet(PARQUET_PATH)

    dsn = _build_dsn(DATABASE_URL)
    logger.info("Connecting to database …")
    conn = psycopg2.connect(dsn)
    conn.autocommit = False

    try:
        seed(df, conn)
    except Exception:
        conn.rollback()
        logger.exception("Seed failed — transaction rolled back.")
        sys.exit(1)
    finally:
        conn.close()

    logger.info("Done.")


if __name__ == "__main__":
    main()
