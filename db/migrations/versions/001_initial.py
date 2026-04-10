"""Initial schema: tickers + ticks hypertable

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── tickers ───────────────────────────────────────────────────────────────
    op.create_table(
        "tickers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(16), nullable=False),
        sa.Column("name", sa.String(128), nullable=True),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tickers_symbol", "tickers", ["symbol"], unique=True)

    # ── ticks ─────────────────────────────────────────────────────────────────
    op.create_table(
        "ticks",
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("symbol", sa.String(16), nullable=False),
        sa.Column("price", sa.Numeric(18, 6), nullable=False),
        sa.Column("volume", sa.BigInteger(), nullable=True),
        sa.Column("bid", sa.Numeric(18, 6), nullable=True),
        sa.Column("ask", sa.Numeric(18, 6), nullable=True),
        sa.Column("source", sa.String(8), nullable=True),
        sa.PrimaryKeyConstraint("time", "symbol"),
    )

    # Convert to TimescaleDB hypertable, partitioned by time
    op.execute("SELECT create_hypertable('ticks', 'time', if_not_exists => TRUE)")

    # Composite index for fast per-ticker queries
    op.create_index(
        "ix_ticks_symbol_time_desc",
        "ticks",
        ["symbol", sa.text("time DESC")],
    )


def downgrade() -> None:
    op.drop_index("ix_ticks_symbol_time_desc", table_name="ticks")
    op.drop_table("ticks")
    op.drop_index("ix_tickers_symbol", table_name="tickers")
    op.drop_table("tickers")
