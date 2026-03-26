"""Configuration for the market-data MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _parse_csv_env(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class AppConfig:
    # API endpoints
    coingecko_base_url: str
    coingecko_api_key: str | None   # optional — increases free rate limits
    cryptopanic_api_key: str | None  # optional — news disabled if absent
    fear_greed_base_url: str

    # Server
    transport: str
    host: str
    port: int
    path: str
    allowed_hosts: list[str]
    allowed_origins: list[str]


def load_app_config() -> AppConfig:
    default_allowed_hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
    default_allowed_origins = [
        "http://127.0.0.1:*",
        "http://localhost:*",
        "http://[::1]:*",
    ]

    return AppConfig(
        coingecko_base_url=os.getenv(
            "COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3"
        ),
        coingecko_api_key=os.getenv("COINGECKO_API_KEY") or None,
        cryptopanic_api_key=os.getenv("CRYPTOPANIC_API_KEY") or None,
        fear_greed_base_url=os.getenv(
            "FEAR_GREED_BASE_URL", "https://api.alternative.me"
        ),
        transport=os.getenv("MCP_TRANSPORT", "http"),
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "38089")),
        path=os.getenv("MCP_PATH", "/mcp"),
        allowed_hosts=default_allowed_hosts + _parse_csv_env(os.getenv("MCP_ALLOWED_HOSTS")),
        allowed_origins=default_allowed_origins
        + _parse_csv_env(os.getenv("MCP_ALLOWED_ORIGINS")),
    )
