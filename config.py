from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    # Alpaca
    alpaca_api_key: str = Field(..., env="ALPACA_API_KEY")
    alpaca_api_secret: str = Field(..., env="ALPACA_API_SECRET")
    alpaca_ws_url: str = "wss://stream.data.alpaca.markets/v2/iex"

    # Symbols to track
    symbols: List[str] = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]

    # PostgreSQL / TimescaleDB
    database_url: str = Field(
        "postgresql+asyncpg://market:market@localhost:5432/marketfeed",
        env="DATABASE_URL",
    )

    # Redis
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")

    # Ingestor
    batch_flush_ms: int = 500  # milliseconds between batch writes

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
