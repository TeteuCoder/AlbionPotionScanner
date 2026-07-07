import pytest
from src.domain.market_models import MarketPrice as RawMarketPrice
from src.domain.models import MarketPrice as DomainMarketPrice
from src.services.price_service import (
    PriceService,
    PotionSaleStrategy,
    PriceNotFoundError,
    InvalidPriceError
)

@pytest.fixture
def sample_raw_prices():
    return [
        RawMarketPrice(
            item_id="T4_BURDOCK",
            quality=1,
            sell_price_min=200,
            sell_price_min_date="2026-07-06T12:00:00",
            buy_price_max=180,
            buy_price_max_date="2026-07-06T12:00:00"
        ),
        RawMarketPrice(
            item_id="T4_POTION_HEAL",
            quality=1,
            sell_price_min=1000,
            sell_price_min_date="2026-07-06T12:05:00",
            buy_price_max=950,
            buy_price_max_date="2026-07-06T12:05:00"
        ),
        RawMarketPrice(
            item_id="T4_POTION_HEAL",
            quality=2,
            sell_price_min=1500,
            sell_price_min_date="2026-07-06T12:10:00",
            buy_price_max=1400,
            buy_price_max_date="2026-07-06T12:10:00"
        ),
        RawMarketPrice(
            item_id="ZERO_PRICE_ITEM",
            quality=1,
            sell_price_min=0,
            sell_price_min_date="2026-07-06T12:00:00",
            buy_price_max=0,
            buy_price_max_date="2026-07-06T12:00:00"
        )
    ]

def test_select_price_ingredient_purchase_success(sample_raw_prices):
    """Verify that ingredient purchase successfully selects the lowest sell order price."""
    service = PriceService()
    domain_price = service.select_price(
        raw_prices=sample_raw_prices,
        item_id="T4_BURDOCK",
        role="ingredient purchase",
        quality=1
    )
    
    assert isinstance(domain_price, DomainMarketPrice)
    assert domain_price.item_id == "T4_BURDOCK"
    assert domain_price.quality == 1
    assert domain_price.price_role == "ingredient purchase"
    assert domain_price.price_field == "sell_price_min"
    assert domain_price.unit_price == 200
    assert domain_price.observed_at == "2026-07-06T12:00:00"
    assert domain_price.source == "Albion Online Data Project"


def test_select_price_potion_sale_sell_order_success(sample_raw_prices):
    """Verify that potion sale under SELL_ORDER strategy selects the lowest sell order price."""
    service = PriceService()
    domain_price = service.select_price(
        raw_prices=sample_raw_prices,
        item_id="T4_POTION_HEAL",
        role="potion sale",
        quality=2,
        sale_strategy=PotionSaleStrategy.SELL_ORDER
    )
    
    assert domain_price.item_id == "T4_POTION_HEAL"
    assert domain_price.quality == 2
    assert domain_price.price_role == "potion sale"
    assert domain_price.price_field == "sell_price_min"
    assert domain_price.unit_price == 1500
    assert domain_price.observed_at == "2026-07-06T12:10:00"


def test_select_price_potion_sale_buy_order_success(sample_raw_prices):
    """Verify that potion sale under BUY_ORDER strategy selects the highest buy order price."""
    service = PriceService()
    domain_price = service.select_price(
        raw_prices=sample_raw_prices,
        item_id="T4_POTION_HEAL",
        role="potion sale",
        quality=1,
        sale_strategy=PotionSaleStrategy.BUY_ORDER
    )
    
    assert domain_price.item_id == "T4_POTION_HEAL"
    assert domain_price.quality == 1
    assert domain_price.price_role == "potion sale"
    assert domain_price.price_field == "buy_price_max"
    assert domain_price.unit_price == 950
    assert domain_price.observed_at == "2026-07-06T12:05:00"


def test_select_price_not_found(sample_raw_prices):
    """Verify that looking up a non-existent item or quality raises PriceNotFoundError."""
    service = PriceService()
    
    # Missing item_id
    with pytest.raises(PriceNotFoundError) as exc_info:
        service.select_price(sample_raw_prices, "T8_YARROW", "ingredient purchase")
    assert "Nenhum preco de mercado encontrado para o item 'T8_YARROW'" in str(exc_info.value)
    
    # Missing quality
    with pytest.raises(PriceNotFoundError) as exc_info:
        service.select_price(sample_raw_prices, "T4_BURDOCK", "ingredient purchase", quality=2)
    assert "qualidade 2" in str(exc_info.value)


def test_select_price_invalid_value_zero(sample_raw_prices):
    """Verify that a price entry with zero value raises InvalidPriceError."""
    service = PriceService()
    
    with pytest.raises(InvalidPriceError) as exc_info:
        service.select_price(sample_raw_prices, "ZERO_PRICE_ITEM", "ingredient purchase")
    assert "Preco unitario invalido" in str(exc_info.value)


def test_select_price_invalid_input_parameters(sample_raw_prices):
    """Verify that invalid inputs raise ValueError."""
    service = PriceService()
    
    # Empty item_id
    with pytest.raises(ValueError):
        service.select_price(sample_raw_prices, "", "ingredient purchase")
        
    # Invalid role
    with pytest.raises(ValueError):
        service.select_price(sample_raw_prices, "T4_BURDOCK", "invalid role")
        
    # Invalid quality
    with pytest.raises(ValueError):
        service.select_price(sample_raw_prices, "T4_BURDOCK", "ingredient purchase", quality=0)
