"""Input and output normalization helpers for market_data_mcp."""

from __future__ import annotations


def clamp_limit(value: int, *, minimum: int = 1, maximum: int = 250) -> int:
    return max(minimum, min(value, maximum))


def clamp_history_days(value: int) -> int:
    return clamp_limit(value, minimum=1, maximum=365)


def normalize_vs_currency(value: str) -> str:
    normalized = value.strip().lower()
    if not normalized:
        raise ValueError("vs_currency must not be empty")
    return normalized


def safe_int(value: object, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_description(value: str | None, *, limit: int = 500) -> str:
    if not value:
        return ""
    compact = " ".join(value.split())
    return compact[:limit]
