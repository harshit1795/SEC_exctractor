"""add_fundamentals_table

Revision ID: c3d4e5f6a7b8
Revises: 13e00d3ad29d
Create Date: 2026-04-04 00:00:00.000000

Migrates financial fundamentals data from fundamentals_tall.parquet
into a proper PostgreSQL table for reliable cloud deployments.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "13e00d3ad29d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fundamentals",
        # Surrogate PK — composite string: ticker|fiscal_period|metric|category
        sa.Column("id", sa.String(512), primary_key=True, nullable=False),
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=True),
        sa.Column("fiscal_period", sa.String(10), nullable=False),
        sa.Column("metric", sa.String(255), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        # Unique business key constraint
        sa.UniqueConstraint(
            "ticker", "fiscal_period", "metric", "category",
            name="uq_fundamentals_row",
        ),
    )
    # Indexes for fast lookups
    op.create_index(
        "ix_fundamentals_ticker",
        "fundamentals",
        ["ticker"],
        unique=False,
    )
    op.create_index(
        "ix_fundamentals_ticker_period",
        "fundamentals",
        ["ticker", "fiscal_period"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_fundamentals_ticker_period", table_name="fundamentals")
    op.drop_index("ix_fundamentals_ticker", table_name="fundamentals")
    op.drop_table("fundamentals")
