from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Ticker(Base):
    """Tracked symbols — populated on startup from config."""

    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(16), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=text("NOW()"))


class Tick(Base):
    """
    Raw price ticks — stored in a TimescaleDB hypertable partitioned by time.

    The hypertable is created via Alembic migration (see
    db/migrations/versions/001_initial.py) using:
        SELECT create_hypertable('ticks', 'time');
    """

    __tablename__ = "ticks"

    # TimescaleDB requires the partition key to be part of the primary key
    # when the table is a hypertable. We use a composite PK.
    time = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    symbol = Column(String(16), primary_key=True, nullable=False)
    price = Column(Numeric(18, 6), nullable=False)
    volume = Column(BigInteger, nullable=True)
    bid = Column(Numeric(18, 6), nullable=True)
    ask = Column(Numeric(18, 6), nullable=True)
    source = Column(String(8), nullable=True)  # "trade" | "quote"

    __table_args__ = (
        # Fast per-ticker time-range queries
        Index("ix_ticks_symbol_time_desc", "symbol", text("time DESC")),
    )
