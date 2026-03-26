"""MCP tool definitions for the market-data MCP server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from market_data_mcp.clients import CoinGeckoClient, CryptoPanicClient, FearGreedClient
from market_data_mcp.validation import (
    clamp_history_days,
    clamp_limit,
    normalize_description,
    normalize_vs_currency,
    safe_int,
)


def register_tools(
    app: FastMCP,
    coingecko: CoinGeckoClient,
    fear_greed: FearGreedClient,
    cryptopanic: CryptoPanicClient | None,
) -> None:

    # ── Global market ─────────────────────────────────────────────────────

    @app.tool()
    async def get_global_market() -> dict[str, Any]:
        """
        Get global crypto market overview: total market cap, BTC/ETH dominance,
        24h trading volume, number of active currencies, and market cap change %.
        """
        data = await coingecko.get_global()
        return {
            "total_market_cap_usd": data.get("total_market_cap", {}).get("usd"),
            "total_volume_24h_usd": data.get("total_volume", {}).get("usd"),
            "btc_dominance_pct": round(data.get("market_cap_percentage", {}).get("btc", 0), 2),
            "eth_dominance_pct": round(data.get("market_cap_percentage", {}).get("eth", 0), 2),
            "market_cap_change_24h_pct": round(
                data.get("market_cap_change_percentage_24h_usd", 0), 2
            ),
            "active_cryptocurrencies": data.get("active_cryptocurrencies"),
            "markets": data.get("markets"),
        }

    # ── Fear & Greed ──────────────────────────────────────────────────────

    @app.tool()
    async def get_fear_greed(history_days: int = 7) -> dict[str, Any]:
        """
        Get the Crypto Fear & Greed Index.
        Returns current value + classification, and the past `history_days` days of history.
        Value: 0 = Extreme Fear, 100 = Extreme Greed.
        """
        days = clamp_history_days(history_days)
        current = await fear_greed.get_current()
        history = await fear_greed.get_history(days=days)
        return {
            "current": {
                "value": safe_int(current.get("value", 0)),
                "classification": current.get("value_classification"),
                "timestamp": current.get("timestamp"),
            },
            "history": [
                {
                    "value": safe_int(item.get("value", 0)),
                    "classification": item.get("value_classification"),
                    "timestamp": item.get("timestamp"),
                }
                for item in history
            ],
        }

    # ── Top coins ─────────────────────────────────────────────────────────

    @app.tool()
    async def get_top_coins(limit: int = 20, vs_currency: str = "usd") -> list[dict[str, Any]]:
        """
        Get top cryptocurrencies ranked by market cap with price change data.
        limit: number of coins (max 250, default 20).
        vs_currency: quote currency (default 'usd').
        """
        coins = await coingecko.get_coins_markets(
            vs_currency=normalize_vs_currency(vs_currency),
            limit=clamp_limit(limit),
        )
        return [
            {
                "rank": c.get("market_cap_rank"),
                "id": c.get("id"),
                "symbol": c.get("symbol", "").upper(),
                "name": c.get("name"),
                "price": c.get("current_price"),
                "market_cap": c.get("market_cap"),
                "volume_24h": c.get("total_volume"),
                "change_1h_pct": c.get("price_change_percentage_1h_in_currency"),
                "change_24h_pct": c.get("price_change_percentage_24h"),
                "change_7d_pct": c.get("price_change_percentage_7d_in_currency"),
                "ath": c.get("ath"),
                "ath_change_pct": c.get("ath_change_percentage"),
            }
            for c in coins
        ]

    # ── Single coin ───────────────────────────────────────────────────────

    @app.tool()
    async def get_coin_info(coin_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific coin.
        coin_id: CoinGecko ID (e.g. 'bitcoin', 'ethereum', 'solana').
        Use search_coin to find the correct ID if unsure.
        """
        data = await coingecko.get_coin(coin_id)
        md = data.get("market_data", {})
        return {
            "id": data.get("id"),
            "symbol": data.get("symbol", "").upper(),
            "name": data.get("name"),
            "categories": data.get("categories", [])[:5],
            "description": normalize_description(data.get("description", {}).get("en")),
            "market_cap_rank": data.get("market_cap_rank"),
            "price_usd": md.get("current_price", {}).get("usd"),
            "market_cap_usd": md.get("market_cap", {}).get("usd"),
            "fully_diluted_valuation_usd": md.get("fully_diluted_valuation", {}).get("usd"),
            "volume_24h_usd": md.get("total_volume", {}).get("usd"),
            "change_24h_pct": md.get("price_change_percentage_24h"),
            "change_7d_pct": md.get("price_change_percentage_7d"),
            "change_30d_pct": md.get("price_change_percentage_30d"),
            "change_1y_pct": md.get("price_change_percentage_1y"),
            "ath_usd": md.get("ath", {}).get("usd"),
            "ath_change_pct": md.get("ath_change_percentage", {}).get("usd"),
            "ath_date": md.get("ath_date", {}).get("usd"),
            "atl_usd": md.get("atl", {}).get("usd"),
            "circulating_supply": md.get("circulating_supply"),
            "total_supply": md.get("total_supply"),
            "max_supply": md.get("max_supply"),
        }

    @app.tool()
    async def search_coin(query: str) -> list[dict[str, Any]]:
        """
        Search for a coin by name or symbol to find its CoinGecko ID.
        Use this before get_coin_info if you're unsure of the exact ID.
        Example: query='BTC' or query='bitcoin'
        """
        data = await coingecko.search(query)
        coins = data.get("coins", [])[:10]
        return [
            {
                "id": c.get("id"),
                "symbol": c.get("symbol", "").upper(),
                "name": c.get("name"),
                "market_cap_rank": c.get("market_cap_rank"),
            }
            for c in coins
        ]

    # ── Trending ──────────────────────────────────────────────────────────

    @app.tool()
    async def get_trending() -> dict[str, Any]:
        """
        Get currently trending coins and NFTs on CoinGecko (last 24h search volume).
        Useful for spotting momentum and retail attention shifts.
        """
        data = await coingecko.get_trending()
        coins = [
            {
                "rank": item["item"].get("score", 0) + 1,
                "id": item["item"].get("id"),
                "symbol": item["item"].get("symbol", "").upper(),
                "name": item["item"].get("name"),
                "market_cap_rank": item["item"].get("market_cap_rank"),
                "price_btc": item["item"].get("price_btc"),
            }
            for item in data.get("coins", [])
        ]
        return {"trending_coins": coins}

    # ── News ──────────────────────────────────────────────────────────────

    if cryptopanic is not None:

        @app.tool()
        async def get_news(
            currencies: str | None = None,
            filter: str | None = None,
            limit: int = 20,
        ) -> list[dict[str, Any]]:
            """
            Get latest crypto news from CryptoPanic.
            currencies: comma-separated symbols to filter, e.g. 'BTC,ETH'
            filter: 'rising', 'hot', 'bullish', 'bearish', 'important', 'saved', 'lol'
            limit: number of articles (default 20).
            """
            posts = await cryptopanic.get_posts(
                currencies=currencies,
                filter=filter,
                limit=clamp_limit(limit, maximum=100),
            )
            return [
                {
                    "title": p.get("title"),
                    "published_at": p.get("published_at"),
                    "source": p.get("source", {}).get("title"),
                    "url": p.get("url"),
                    "currencies": [
                        c.get("code") for c in (p.get("currencies") or [])
                    ],
                    "votes": {
                        "positive": p.get("votes", {}).get("positive", 0),
                        "negative": p.get("votes", {}).get("negative", 0),
                        "important": p.get("votes", {}).get("important", 0),
                    },
                }
                for p in posts
            ]

    else:

        @app.tool()
        async def get_news(
            currencies: str | None = None,
            filter: str | None = None,
            limit: int = 20,
        ) -> dict[str, str]:
            """
            Get latest crypto news from CryptoPanic.
            ⚠️ CRYPTOPANIC_API_KEY is not configured — news is unavailable.
            Set CRYPTOPANIC_API_KEY in secrets/market_data.env to enable this tool.
            """
            return {
                "error": "CryptoPanic API key not configured.",
                "action": "Set CRYPTOPANIC_API_KEY in secrets/market_data.env",
            }
