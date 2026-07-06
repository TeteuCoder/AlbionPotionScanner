# Albion Online Data Project

## Purpose

The Albion Online Data Project provides market data collected from Albion Online
clients. AlbionPotionScanner uses this as the single source of truth for market
prices.

For V1, all market data requests must use Brecilien only. Ingredient purchase
prices, crafting assumptions, and potion sale prices all use Brecilien as the
fixed operating city.

## Region

The project targets the Americas / West API:

```text
https://west.albion-online-data.com
```

## Current Price Endpoint

Use the current price endpoint for item pricing:

```text
GET /api/v2/stats/prices/{item_ids}.json
```

Example:

```text
https://west.albion-online-data.com/api/v2/stats/prices/T4_POTION_HEAL.json
```

Optional query parameters:

- `locations`: fixed to `Brecilien` for V1
- `qualities`: comma-separated quality values

Example with filters:

```text
https://west.albion-online-data.com/api/v2/stats/prices/T4_POTION_HEAL.json?locations=Brecilien&qualities=2
```

Observed response shape:

```json
[
  {
    "item_id": "T4_POTION_HEAL",
    "city": "Brecilien",
    "quality": 2,
    "sell_price_min": 0,
    "sell_price_min_date": "0001-01-01T00:00:00",
    "sell_price_max": 0,
    "sell_price_max_date": "0001-01-01T00:00:00",
    "buy_price_min": 0,
    "buy_price_min_date": "0001-01-01T00:00:00",
    "buy_price_max": 0,
    "buy_price_max_date": "0001-01-01T00:00:00"
  }
]
```

## Batch Requests

The endpoint accepts multiple comma-separated item IDs:

```text
https://west.albion-online-data.com/api/v2/stats/prices/T4_POTION_HEAL,T4_POTION_ENERGY.json?locations=Brecilien
```

Although the endpoint supports multiple locations, V1 must not use that
capability. Future implementation should batch item lookups for Brecilien where
practical to avoid duplicated API requests.

## Rate Limits

Rate limit behavior must be confirmed against the current API documentation
before implementation. Until confirmed, future clients should be conservative,
cache responses, and avoid repeated identical requests.

## Data Handling Notes

- A price value of `0` means no current observed price for that field, not a
  free item.
- Price timestamps should be retained for transparency.
- Market access should be isolated in a future API client service.
- The V1 API client should expose the operating city as project-wide
  configuration fixed to `Brecilien`, not as user input.
