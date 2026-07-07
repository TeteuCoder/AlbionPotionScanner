from enum import Enum
from typing import List, Optional
from src.domain.market_models import MarketPrice as RawMarketPrice
from src.domain.models import MarketPrice as DomainMarketPrice

class PriceServiceError(Exception):
    """Base exception for all PriceService errors."""
    pass

class PriceNotFoundError(PriceServiceError):
    """Raised when a price cannot be found for a given item and quality."""
    pass

class InvalidPriceError(PriceServiceError):
    """Raised when a price entry exists but its price value is invalid (e.g. <= 0)."""
    pass


class PotionSaleStrategy(str, Enum):
    """Strategy for selecting the market sell price of a crafted potion."""
    SELL_ORDER = "sell_price_min"  # Sell by creating a sell order, competing with the lowest sell price
    BUY_ORDER = "buy_price_max"    # Sell immediately by filling the highest existing buy order


class PriceService:
    """Service responsible for selecting, validating, and converting raw market prices into domain-level prices."""

    def select_price(
        self,
        raw_prices: List[RawMarketPrice],
        item_id: str,
        role: str,
        quality: int = 1,
        sale_strategy: PotionSaleStrategy = PotionSaleStrategy.SELL_ORDER
    ) -> DomainMarketPrice:
        """
        Selects a price from raw market prices for the given item and quality under a specific role.

        Args:
            raw_prices: List of RawMarketPrice data fetched from the API.
            item_id: The Albion item ID to look for.
            role: The role of the price. Must be 'ingredient purchase' or 'potion sale'.
            quality: The quality level of the item. Defaults to 1 (Normal).
            sale_strategy: The strategy to use for potion sales. Defaults to PotionSaleStrategy.SELL_ORDER.

        Returns:
            A validated DomainMarketPrice object.

        Raises:
            ValueError: If input arguments are invalid.
            PriceNotFoundError: If no raw price matching item_id and quality is found.
            InvalidPriceError: If the price is zero, negative, or contains invalid data.
        """
        if not item_id:
            raise ValueError("item_id cannot be empty")
        if role not in ("ingredient purchase", "potion sale"):
            raise ValueError("role must be 'ingredient purchase' or 'potion sale'")
        if quality <= 0:
            raise ValueError("quality must be greater than zero")

        # Find the matching raw price
        matching_raw: Optional[RawMarketPrice] = None
        for raw in raw_prices:
            if raw.item_id == item_id and raw.quality == quality:
                matching_raw = raw
                break

        if not matching_raw:
            raise PriceNotFoundError(
                f"Nenhum preco de mercado encontrado para o item '{item_id}' com qualidade {quality}"
            )

        # Determine price field and unit price based on the role and strategy
        if role == "ingredient purchase":
            price_field = "sell_price_min"
            unit_price = matching_raw.sell_price_min
            observed_at = matching_raw.sell_price_min_date
        else:
            # role == "potion sale"
            price_field = sale_strategy.value
            if sale_strategy == PotionSaleStrategy.SELL_ORDER:
                unit_price = matching_raw.sell_price_min
                observed_at = matching_raw.sell_price_min_date
            elif sale_strategy == PotionSaleStrategy.BUY_ORDER:
                unit_price = matching_raw.buy_price_max
                observed_at = matching_raw.buy_price_max_date
            else:
                raise ValueError(f"Unknown PotionSaleStrategy: {sale_strategy}")

        # Validate the unit price value
        if unit_price <= 0:
            if role == "ingredient purchase":
                raise InvalidPriceError(
                    f"Preco unitario invalido ({unit_price}) para o ingrediente '{item_id}' (campo '{price_field}'). "
                    f"O ingrediente pode estar em falta ou sem ordens de venda no mercado."
                )
            else:
                raise InvalidPriceError(
                    f"Preco unitario invalido ({unit_price}) para a pocao '{item_id}' (campo '{price_field}'). "
                    f"A pocao pode estar sem ordens de compra/venda ativas no mercado."
                )

        domain_price = DomainMarketPrice(
            item_id=item_id,
            quality=quality,
            price_role=role,
            price_field=price_field,
            unit_price=unit_price,
            observed_at=observed_at,
            source="Albion Online Data Project"
        )
        domain_price.validate()
        return domain_price
