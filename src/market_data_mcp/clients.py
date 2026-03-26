"""HTTP clients for CoinGecko, Fear & Greed, and CryptoPanic APIs."""

from __future__ import annotations

from typing import Any

import httpx

from market_data_mcp.config import AppConfig

# Shared timeout for all external API calls
_TIMEOUT = httpx.Timeout(15.0)


class CoinGeckoClient:
    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        headers = {"accept": "application/json"}
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
        self._http = httpx.AsyncClient(
            base_url=base_url, headers=headers, timeout=_TIMEOUT
        )

    async def get_global(self) -> dict[str, Any]:
        r = await self._http.get("/global")
        r.raise_for_status()
        return r.json().get("data", {})

    async def get_coins_markets(
        self,
        vs_currency: str = "usd",
        limit: int = 20,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        r = await self._http.get(
            "/coins/markets",
            params={
                "vs_currency": vs_currency,
                "order": "market_cap_desc",
                "per_page": max(1, min(limit, 250)),
                "page": page,
                "sparkline": False,
                "price_change_percentage": "1h,24h,7d",
            },
        )
        r.raise_for_status()
        return r.json()

    async def get_coin(self, coin_id: str) -> dict[str, Any]:
        r = await self._http.get(
            f"/coins/{coin_id}",
            params={
                "localization": False,
                "tickers": False,
                "market_data": True,
                "community_data": False,
                "developer_data": False,
            },
        )
        r.raise_for_status()
        return r.json()

    async def get_trending(self) -> dict[str, Any]:
        r = await self._http.get("/search/trending")
        r.raise_for_status()
        return r.json()

    async def search(self, query: str) -> dict[str, Any]:
        r = await self._http.get("/search", params={"query": query})
        r.raise_for_status()
        return r.json()

    async def aclose(self) -> None:
        await self._http.aclose()


class FearGreedClient:
    def __init__(self, base_url: str) -> None:
        self._http = httpx.AsyncClient(base_url=base_url, timeout=_TIMEOUT)

    async def get_current(self) -> dict[str, Any]:
        r = await self._http.get("/fng/")
        r.raise_for_status()
        data = r.json()
        return data["data"][0] if data.get("data") else {}

    async def get_history(self, days: int = 7) -> list[dict[str, Any]]:
        r = await self._http.get("/fng/", params={"limit": days})
        r.raise_for_status()
        return r.json().get("data", [])

    async def aclose(self) -> None:
        await self._http.aclose()


class CryptoPanicClient:
    _BASE = "https://cryptopanic.com/api/v1"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._http = httpx.AsyncClient(timeout=_TIMEOUT)

    async def get_posts(
        self,
        currencies: str | None = None,
        kind: str = "news",
        filter: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "auth_token": self._api_key,
            "kind": kind,
            "public": "true",
        }
        if currencies:
            params["currencies"] = currencies
        if filter:
            params["filter"] = filter

        r = await self._http.get(f"{self._BASE}/posts/", params=params)
        r.raise_for_status()
        results = r.json().get("results", [])
        return results[:limit]

    async def aclose(self) -> None:
        await self._http.aclose()


def build_clients(config: AppConfig) -> tuple[CoinGeckoClient, FearGreedClient, CryptoPanicClient | None]:
    coingecko = CoinGeckoClient(
        base_url=config.coingecko_base_url,
        api_key=config.coingecko_api_key,
    )
    fear_greed = FearGreedClient(base_url=config.fear_greed_base_url)
    cryptopanic = (
        CryptoPanicClient(api_key=config.cryptopanic_api_key)
        if config.cryptopanic_api_key
        else None
    )
    return coingecko, fear_greed, cryptopanic
