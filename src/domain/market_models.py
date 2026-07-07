from dataclasses import dataclass

@dataclass(frozen=True)
class MarketPrice:
    """Immutable representation of market price data for a single item from the Albion Online Data Project."""
    item_id: str
    quality: int
    sell_price_min: int
    sell_price_min_date: str
    buy_price_max: int
    buy_price_max_date: str
