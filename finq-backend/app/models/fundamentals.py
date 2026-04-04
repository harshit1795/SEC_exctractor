"""
SQLAlchemy model for financial fundamentals (migrated from parquet).

Schema mirrors the long/tall format of fundamentals_tall.parquet:
  Ticker | PeriodEnd | FiscalPeriod | Metric | Category | Value
"""
from sqlalchemy import (
    Column, String, Float, Date, Index, UniqueConstraint
)
from app.database import Base


class Fundamental(Base):
    __tablename__ = "fundamentals"

    # ── Columns ──────────────────────────────────────────────────────────────
    ticker: str = Column(String(20), nullable=False)
    period_end = Column(Date, nullable=True)
    fiscal_period: str = Column(String(10), nullable=False)   # e.g. "2024Q3"
    metric: str = Column(String(255), nullable=False)
    category: str = Column(String(50), nullable=False)        # IncomeStatement | BalanceSheet | CashFlow
    value = Column(Float, nullable=True)

    # ── Composite primary key ─────────────────────────────────────────────────
    __table_args__ = (
        UniqueConstraint(
            "ticker", "fiscal_period", "metric", "category",
            name="uq_fundamentals_row",
        ),
        # Fast lookup by ticker (the primary query path)
        Index("ix_fundamentals_ticker", "ticker"),
        # Allows efficient "latest N periods for ticker" queries
        Index("ix_fundamentals_ticker_period", "ticker", "fiscal_period"),
        # Synthetic PK so SQLAlchemy / Alembic are happy
        {"extend_existing": True},
    )

    # SQLAlchemy requires exactly one primary key column; use a surrogate.
    id = Column(
        String(512),   # ticker|fiscal_period|metric|category
        primary_key=True,
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Fundamental ticker={self.ticker} period={self.fiscal_period} "
            f"metric={self.metric} value={self.value}>"
        )
