from market_data_mcp.validation import (
    clamp_history_days,
    clamp_limit,
    normalize_description,
    normalize_vs_currency,
    safe_int,
)


def test_clamp_limit_enforces_range() -> None:
    assert clamp_limit(-5) == 1
    assert clamp_limit(999) == 250


def test_clamp_history_days_allows_reasonable_value() -> None:
    assert clamp_history_days(30) == 30


def test_normalize_vs_currency_requires_value() -> None:
    try:
        normalize_vs_currency("   ")
    except ValueError as exc:
        assert "vs_currency must not be empty" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_safe_int_handles_missing_values() -> None:
    assert safe_int(None) == 0
    assert safe_int("12") == 12


def test_normalize_description_compacts_whitespace() -> None:
    assert normalize_description("hello \n  world") == "hello world"
