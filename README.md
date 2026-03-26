# market-data-mcp

`market-data-mcp` is an MCP server that combines broad crypto market data from CoinGecko, the Crypto Fear & Greed Index, and optional CryptoPanic news into one tool surface for agents.

## What It Covers

- Global market overview
- Fear & Greed index with history
- Top coins by market cap
- Detailed coin lookups by CoinGecko ID
- Search for CoinGecko IDs
- Trending assets
- Optional news feed from CryptoPanic

## Why This Server Exists

Most agent tasks need a quick high-level market snapshot before deeper exchange or derivatives analysis. This server provides that common layer with:

- public market data sources
- simple MCP tool contracts
- bounded input handling
- optional news support without requiring it for the rest of the server

## Requirements

- Python 3.11+
- No API key is required for the core tools
- Optional keys improve rate limits or enable news

## Quick Start

1. Create your local env file:

```bash
cp secrets/market_data.env.example secrets/market_data.env
```

2. Optionally set:

- `COINGECKO_API_KEY`
- `CRYPTOPANIC_API_KEY`

3. Run locally:

```bash
pip install -e .
python -m market_data_mcp
```

## Docker

```bash
docker build -t market-data-mcp .
docker run --rm -p 38089:38089 --env-file secrets/market_data.env market-data-mcp
```

## Claude / Codex MCP Registration

```bash
claude mcp add market-data --transport http http://127.0.0.1:38089/mcp
```

## Tools

| Tool | Source | Notes |
|------|--------|-------|
| `get_global_market` | CoinGecko | Global market cap, dominance, volume |
| `get_fear_greed` | alternative.me | Current value plus history |
| `get_top_coins` | CoinGecko | Ranked by market cap |
| `get_coin_info` | CoinGecko | Detailed market data for one asset |
| `search_coin` | CoinGecko | Resolve CoinGecko IDs |
| `get_trending` | CoinGecko | Current trending assets |
| `get_news` | CryptoPanic | Requires `CRYPTOPANIC_API_KEY` |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `COINGECKO_API_KEY` | empty | Optional demo key for better CoinGecko limits |
| `CRYPTOPANIC_API_KEY` | empty | Enables `get_news` |
| `COINGECKO_BASE_URL` | `https://api.coingecko.com/api/v3` | CoinGecko base URL |
| `FEAR_GREED_BASE_URL` | `https://api.alternative.me` | Fear & Greed API base URL |
| `MCP_TRANSPORT` | `http` | `http`, `streamable-http`, `sse`, or `stdio` |
| `MCP_HOST` | `0.0.0.0` | Bind host |
| `PORT` | `38089` | HTTP listen port |
| `MCP_PATH` | `/mcp` | MCP endpoint path |
| `MCP_ALLOWED_HOSTS` | empty | Extra allowed hosts, comma-separated |
| `MCP_ALLOWED_ORIGINS` | empty | Extra allowed origins, comma-separated |

## Rate Limits

- CoinGecko free tier is limited; a demo key helps substantially
- Fear & Greed generally works without authentication
- CryptoPanic free tier is limited and news is optional in this server

## Development

Install test dependencies and run tests:

```bash
pip install -e ".[test]"
pytest
```

## Security Notes

- Do not commit `secrets/market_data.env`
- If you expose HTTP externally, put it behind your own auth or trusted network boundary
