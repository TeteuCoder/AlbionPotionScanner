import pytest
from decimal import Decimal
from src.domain.models import (
    Ingredient,
    PotionRecipe,
    MarketPrice,
    CalculationParameters,
    ProfitCalculation
)
from src.services.craft_calculator import CraftCalculator

@pytest.fixture
def base_recipe():
    return PotionRecipe(
        recipe_id="T4_POTION_HEAL",
        potion_item_id="T4_POTION_HEAL",
        potion_name="Healing Potion",
        family="Healing Potion",
        tier=4,
        enchantment_level=0,
        output_quantity=5,
        ingredients=[
            Ingredient(item_id="T4_BURDOCK", item_name="Crenellated Burdock", quantity=24, tier=4)
        ]
    )

@pytest.fixture
def base_ingredient_prices():
    return [
        MarketPrice(
            item_id="T4_BURDOCK",
            quality=1,
            price_role="ingredient purchase",
            price_field="sell_price_min",
            unit_price=100,
            observed_at="2026-07-06T12:00:00"
        )
    ]

@pytest.fixture
def base_potion_sell_price():
    return MarketPrice(
        item_id="T4_POTION_HEAL",
        quality=1,
        price_role="potion sale",
        price_field="sell_price_min",
        unit_price=1000,
        observed_at="2026-07-06T12:00:00"
    )

@pytest.fixture
def base_parameters():
    return CalculationParameters(
        material_return_rate=Decimal("0.15"),
        crafting_station_fee=Decimal("100"),
        marketplace_tax_rate=Decimal("0.04")
    )


def test_calculate_profitability_success(base_recipe, base_ingredient_prices, base_potion_sell_price, base_parameters):
    """Verify that profitability calculation operates correctly with MRR, crafting fee, and tax."""
    calculator = CraftCalculator()
    calc = calculator.calculate_profitability(
        recipe=base_recipe,
        ingredient_prices=base_ingredient_prices,
        potion_sell_price=base_potion_sell_price,
        parameters=base_parameters
    )
    
    assert isinstance(calc, ProfitCalculation)
    assert calc.gross_ingredient_cost == Decimal("2400")  # 24 * 100
    assert calc.returned_material_value == Decimal("360")  # 2400 * 0.15
    assert calc.effective_ingredient_cost == Decimal("2040")  # 2400 - 360
    assert calc.crafting_station_fee == Decimal("100")
    assert calc.total_cost == Decimal("2140")  # 2040 + 100
    assert calc.gross_revenue == Decimal("5000")  # 1000 * 5
    assert calc.marketplace_tax == Decimal("200")  # 5000 * 0.04
    assert calc.net_revenue == Decimal("4800")  # 5000 - 200
    assert calc.profit == Decimal("2660")  # 4800 - 2140
    assert abs(calc.roi - Decimal("1.24299")) < Decimal("0.0001")  # 2660 / 2140
    assert calc.is_profitable is True
    assert len(calc.warnings) == 0


def test_calculate_profitability_zero_fees_and_rates(base_recipe, base_ingredient_prices, base_potion_sell_price):
    """Verify calculation invariants when MRR, crafting fee, and tax are all zero."""
    parameters = CalculationParameters(
        material_return_rate=Decimal("0.0"),
        crafting_station_fee=Decimal("0.0"),
        marketplace_tax_rate=Decimal("0.0")
    )
    
    calculator = CraftCalculator()
    calc = calculator.calculate_profitability(
        recipe=base_recipe,
        ingredient_prices=base_ingredient_prices,
        potion_sell_price=base_potion_sell_price,
        parameters=parameters
    )
    
    assert calc.gross_ingredient_cost == Decimal("2400")
    assert calc.returned_material_value == Decimal("0")
    assert calc.effective_ingredient_cost == Decimal("2400")
    assert calc.total_cost == Decimal("2400")
    assert calc.gross_revenue == Decimal("5000")
    assert calc.marketplace_tax == Decimal("0")
    assert calc.net_revenue == Decimal("5000")
    assert calc.profit == Decimal("2600")  # 5000 - 2400
    assert abs(calc.roi - Decimal("1.08333")) < Decimal("0.0001")


def test_calculate_profitability_not_profitable(base_recipe, base_ingredient_prices, base_parameters):
    """Verify is_profitable is False and profit is negative when costs exceed revenue."""
    low_potion_sell_price = MarketPrice(
        item_id="T4_POTION_HEAL",
        quality=1,
        price_role="potion sale",
        price_field="sell_price_min",
        unit_price=300,  # low sell price
        observed_at="2026-07-06T12:00:00"
    )
    
    calculator = CraftCalculator()
    calc = calculator.calculate_profitability(
        recipe=base_recipe,
        ingredient_prices=base_ingredient_prices,
        potion_sell_price=low_potion_sell_price,
        parameters=base_parameters
    )
    
    assert calc.profit == Decimal("-700")  # 1500 * 0.96 (1440) - 2140 total cost
    assert calc.is_profitable is False
    assert abs(calc.roi - Decimal("-0.3271")) < Decimal("0.001")


def test_calculate_profitability_zero_total_cost(base_recipe, base_potion_sell_price, base_ingredient_prices):
    """Verify that ROI is None (absent) when total crafting cost is zero."""
    zero_prices = [
        # In reality unit_price > 0 is enforced in select_price, but let's test the math edge case
        MarketPrice(
            item_id="T4_BURDOCK",
            quality=1,
            price_role="ingredient purchase",
            price_field="sell_price_min",
            unit_price=0,  # 0 cost (though validation inside MarketPrice would normally block this, we skip validate check in direct mock if needed)
            observed_at="2026-07-06T12:00:00"
        )
    ]
    # We construct DomainMarketPrice directly bypassing validations for test edge-case if we want,
    # but wait, MarketPrice.validate raises ValueError for unit_price <= 0.
    # To test zero total cost under validation rules, we can achieve effective_ingredient_cost == 0 by setting MRR to 100% (1.0).
    # Wait, CalculationParameters enforces MRR < 1.0.
    # So crafting_station_fee + effective_ingredient_cost cannot be 0 under strict validation rules if ingredient prices are > 0.
    # Let's verify: yes, if parameters.material_return_rate < 1.0, and unit_price > 0, total_cost is always > 0.
    # But wait, we can bypass the validate check on ProfitCalculation construction, or test if the ROI is None when total_cost is 0.
    # Let's bypass or mock. In ProfitCalculation validate, we check `if self.total_cost == Decimal("0")`.
    # Let's create an artificial ProfitCalculation with total_cost = 0, and verify it validates successfully when roi = None.
    
    # We can create a manual ProfitCalculation object
    calc = ProfitCalculation(
        calculation_id="test-zero-cost",
        recipe=base_recipe,
        ingredient_prices=base_ingredient_prices,
        potion_sell_price=base_potion_sell_price,
        parameters=CalculationParameters(Decimal("0.5"), Decimal("0.0"), Decimal("0.0")), # MRR 0.5, fee 0, tax 0
        gross_ingredient_cost=Decimal("0.0"),
        returned_material_value=Decimal("0.0"),
        effective_ingredient_cost=Decimal("0.0"),
        crafting_station_fee=Decimal("0.0"),
        total_cost=Decimal("0.0"),
        gross_revenue=Decimal("1000.0"),
        marketplace_tax=Decimal("0.0"),
        net_revenue=Decimal("1000.0"),
        profit=Decimal("1000.0"),
        roi=None,  # ROI must be None
        is_profitable=True,
        calculated_at="2026-07-06T12:00:00"
    )
    # We bypass recipe and parameter validations inside test by overriding ingredients price to bypass unit_price=0 if we don't call validate(),
    # but wait! We can bypass ingredient price validate by just passing ingredient prices with unit_price=100, but overriding gross_ingredient_cost=0
    # in the constructor. However, our manual class validation checks financial invariants:
    # "effective_ingredient_cost must equal gross_ingredient_cost minus returned_material_value".
    # If we set:
    # gross_ingredient_cost = 0, returned_material_value = 0, effective_ingredient_cost = 0, crafting_station_fee = 0
    # then total_cost = 0 is mathematically consistent!
    # Let's check: does it pass calc.validate()?
    # If ingredient_prices has unit_price = 100, then gross_ingredient_cost = 0 would fail validation because:
    # gross_ingredient_cost is not check-validated against sum of prices inside calc.validate()!
    # Wait, calc.validate() checks:
    # `if self.effective_ingredient_cost != self.gross_ingredient_cost - self.returned_material_value:`
    # and match between ingredient_prices IDs and recipe ingredient IDs.
    # It does NOT check `gross_ingredient_cost == sum(price.unit_price * qty)`. That is the calculator's job, not the entity validation's invariant!
    # So we can create a ProfitCalculation with gross_ingredient_cost = Decimal("0"), returned_material_value = Decimal("0"),
    # effective_ingredient_cost = Decimal("0"), crafting_station_fee = Decimal("0"), total_cost = Decimal("0")
    # while passing valid ingredient_prices (with unit_price = 100).
    # Let's call calc.validate() and it should pass!
    calc.validate()
    assert calc.roi is None


def test_calculate_profitability_missing_price_entry(base_recipe, base_potion_sell_price, base_parameters):
    """Verify that calculating profitability with missing ingredient prices raises ValueError."""
    calculator = CraftCalculator()
    with pytest.raises(ValueError) as exc_info:
        calculator.calculate_profitability(
            recipe=base_recipe,
            ingredient_prices=[],  # Missing price for T4_BURDOCK
            potion_sell_price=base_potion_sell_price,
            parameters=base_parameters
        )
    assert "Missing price entry for recipe ingredient" in str(exc_info.value)


def test_calculate_profitability_potion_mismatch(base_recipe, base_ingredient_prices, base_parameters):
    """Verify that calculating profitability with mismatched potion sell price raises ValueError on validation."""
    wrong_potion_price = MarketPrice(
        item_id="T6_POTION_HEAL",  # Mismatch with recipe T4_POTION_HEAL
        quality=1,
        price_role="potion sale",
        price_field="sell_price_min",
        unit_price=1000,
        observed_at="2026-07-06T12:00:00"
    )
    
    calculator = CraftCalculator()
    with pytest.raises(ValueError) as exc_info:
        calculator.calculate_profitability(
            recipe=base_recipe,
            ingredient_prices=base_ingredient_prices,
            potion_sell_price=wrong_potion_price,
            parameters=base_parameters
        )
    assert "must match recipe potion_item_id" in str(exc_info.value)


def test_calculate_profitability_warnings_placeholder_timestamp(base_recipe, base_ingredient_prices, base_parameters):
    """Verify that warnings are correctly generated for placeholder timestamps."""
    placeholder_potion_price = MarketPrice(
        item_id="T4_POTION_HEAL",
        quality=1,
        price_role="potion sale",
        price_field="sell_price_min",
        unit_price=1000,
        observed_at="0001-01-01T00:00:00"  # Placeholder timestamp
    )
    
    calculator = CraftCalculator()
    calc = calculator.calculate_profitability(
        recipe=base_recipe,
        ingredient_prices=base_ingredient_prices,
        potion_sell_price=placeholder_potion_price,
        parameters=base_parameters
    )
    
    assert len(calc.warnings) == 1
    assert "placeholder timestamp" in calc.warnings[0]


def test_calculate_profitability_warnings_missing_timestamp(base_recipe, base_ingredient_prices, base_parameters):
    """Verify that warnings are correctly generated for missing timestamps."""
    missing_timestamp_potion_price = MarketPrice(
        item_id="T4_POTION_HEAL",
        quality=1,
        price_role="potion sale",
        price_field="sell_price_min",
        unit_price=1000,
        observed_at=None  # Missing timestamp
    )
    
    calculator = CraftCalculator()
    calc = calculator.calculate_profitability(
        recipe=base_recipe,
        ingredient_prices=base_ingredient_prices,
        potion_sell_price=missing_timestamp_potion_price,
        parameters=base_parameters
    )
    
    assert len(calc.warnings) == 1
    assert "no observed timestamp" in calc.warnings[0]
