import pytest
from decimal import Decimal
from typing import List, Optional
from src.domain.market_models import MarketPrice as RawMarketPrice
from src.domain.models import (
    Ingredient,
    PotionRecipe,
    MarketPrice as DomainMarketPrice,
    CalculationParameters,
    ProfitCalculation,
    ScanResult
)
from src.services.price_service import PriceService, PotionSaleStrategy
from src.services.craft_calculator import CraftCalculator
from src.services.potion_scanner import PotionScanner

# Mock Repository
class MockRecipeRepository:
    def __init__(self, recipes: List[PotionRecipe]):
        self.recipes = recipes
    def get_all(self) -> List[PotionRecipe]:
        return self.recipes

# Mock Data Client
class MockDataClient:
    def __init__(self, raw_prices: List[RawMarketPrice]):
        self.raw_prices = raw_prices
        self.last_queried_ids = None

    def fetch_prices(self, item_ids: List[str], qualities: Optional[List[int]] = None) -> List[RawMarketPrice]:
        self.last_queried_ids = item_ids
        # Return only the raw prices matching the requested IDs to simulate real API filtering
        return [p for p in self.raw_prices if p.item_id in item_ids]


@pytest.fixture
def mock_recipes():
    return [
        PotionRecipe(
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
        ),
        PotionRecipe(
            recipe_id="T4_POTION_ENERGY",
            potion_item_id="T4_POTION_ENERGY",
            potion_name="Energy Potion",
            family="Energy Potion",
            tier=4,
            enchantment_level=0,
            output_quantity=5,
            ingredients=[
                Ingredient(item_id="T4_BURDOCK", item_name="Crenellated Burdock", quantity=12, tier=4),
                Ingredient(item_id="T4_MILK", item_name="Goat's Milk", quantity=6, tier=4)
            ]
        )
    ]

@pytest.fixture
def mock_raw_prices():
    return [
        RawMarketPrice(
            item_id="T4_BURDOCK",
            quality=1,
            sell_price_min=100,
            sell_price_min_date="2026-07-06T12:00:00",
            buy_price_max=90,
            buy_price_max_date="2026-07-06T12:00:00"
        ),
        RawMarketPrice(
            item_id="T4_MILK",
            quality=1,
            sell_price_min=50,
            sell_price_min_date="2026-07-06T12:00:00",
            buy_price_max=40,
            buy_price_max_date="2026-07-06T12:00:00"
        ),
        RawMarketPrice(
            item_id="T4_POTION_HEAL",
            quality=1,
            sell_price_min=1000,
            sell_price_min_date="2026-07-06T12:00:00",
            buy_price_max=900,
            buy_price_max_date="2026-07-06T12:00:00"
        ),
        RawMarketPrice(
            item_id="T4_POTION_ENERGY",
            quality=1,
            sell_price_min=800,
            sell_price_min_date="2026-07-06T12:00:00",
            buy_price_max=700,
            buy_price_max_date="2026-07-06T12:00:00"
        )
    ]

@pytest.fixture
def calc_parameters():
    return CalculationParameters(
        material_return_rate=Decimal("0.15"),
        crafting_station_fee=Decimal("100"),
        marketplace_tax_rate=Decimal("0.04")
    )


def test_scan_success(mock_recipes, mock_raw_prices, calc_parameters):
    """Verify that a successful scan processes all recipes, queries client in a batch, and identifies the best calculation."""
    repo = MockRecipeRepository(mock_recipes)
    client = MockDataClient(mock_raw_prices)
    price_service = PriceService()
    calculator = CraftCalculator()
    
    scanner = PotionScanner(repo, client, price_service, calculator)
    result = scanner.scan(calc_parameters)
    
    assert isinstance(result, ScanResult)
    assert result.scanned_recipe_count == 2
    assert result.valid_calculation_count == 2
    assert result.skipped_recipe_count == 0
    assert len(result.calculations) == 2
    
    # Verify that the client was queried in one batch with all unique item IDs
    assert client.last_queried_ids is not None
    assert set(client.last_queried_ids) == {"T4_BURDOCK", "T4_MILK", "T4_POTION_HEAL", "T4_POTION_ENERGY"}
    
    # Verify that the calculations match expected profits
    # Heal: 5 * 1000 = 5000 revenue. Tax: 200. Net revenue: 4800.
    # Cost: Gross (2400) - MRR (360) = 2040. Station fee: 100. Total Cost: 2140. Profit: 2660.
    # Energy: 5 * 800 = 4000 revenue. Tax: 160. Net revenue: 3840.
    # Cost: Gross (12 * 100 + 6 * 50 = 1500) - MRR (225) = 1275. Station fee: 100. Total Cost: 1375. Profit: 2465.
    # Heal is the best calculation
    heal_calc = next(c for c in result.calculations if c.recipe.recipe_id == "T4_POTION_HEAL")
    energy_calc = next(c for c in result.calculations if c.recipe.recipe_id == "T4_POTION_ENERGY")
    
    assert heal_calc.profit == Decimal("2660")
    assert energy_calc.profit == Decimal("2465")
    
    assert result.best_calculation_id == heal_calc.calculation_id


def test_scan_skipped_recipe(mock_recipes, mock_raw_prices, calc_parameters):
    """Verify that a recipe is skipped if any required price is missing, updating counts and warnings."""
    # Omit T4_MILK price
    incomplete_prices = [p for p in mock_raw_prices if p.item_id != "T4_MILK"]
    
    repo = MockRecipeRepository(mock_recipes)
    client = MockDataClient(incomplete_prices)
    price_service = PriceService()
    calculator = CraftCalculator()
    
    scanner = PotionScanner(repo, client, price_service, calculator)
    result = scanner.scan(calc_parameters)
    
    assert result.scanned_recipe_count == 2
    assert result.valid_calculation_count == 1  # Only Heal succeeds
    assert result.skipped_recipe_count == 1  # Energy skips due to missing T4_MILK price
    assert len(result.warnings) == 1
    assert "ENERGY" in result.warnings[0]
    
    # Best calculation id matches the only success (Heal)
    heal_calc = result.calculations[0]
    assert result.best_calculation_id == heal_calc.calculation_id


def test_scan_all_skipped(mock_recipes, calc_parameters):
    """Verify scanner outcome when all recipes are skipped."""
    repo = MockRecipeRepository(mock_recipes)
    client = MockDataClient([])  # No prices available
    price_service = PriceService()
    calculator = CraftCalculator()
    
    scanner = PotionScanner(repo, client, price_service, calculator)
    result = scanner.scan(calc_parameters)
    
    assert result.scanned_recipe_count == 2
    assert result.valid_calculation_count == 0
    assert result.skipped_recipe_count == 2
    assert result.best_calculation_id is None
    assert len(result.warnings) == 2


def test_scan_empty_repository(calc_parameters):
    """Verify scanner outcome when the recipe repository is empty."""
    repo = MockRecipeRepository([])
    client = MockDataClient([])
    price_service = PriceService()
    calculator = CraftCalculator()
    
    scanner = PotionScanner(repo, client, price_service, calculator)
    result = scanner.scan(calc_parameters)
    
    assert result.scanned_recipe_count == 0
    assert result.valid_calculation_count == 0
    assert result.skipped_recipe_count == 0
    assert result.best_calculation_id is None


def test_scan_tie_breaker_by_roi(calc_parameters):
    """Verify deterministic tie-breaker selects recipe with higher ROI when profits are identical."""
    # We craft two recipes that have the exact same profit, but different ROIs.
    # Recipe A: Total Cost = 100, Net Revenue = 200, Profit = 100 (ROI = 1.0)
    # Recipe B: Total Cost = 200, Net Revenue = 300, Profit = 100 (ROI = 0.5)
    # A should win because ROI 1.0 > 0.5
    recipe_a = PotionRecipe(
        recipe_id="T4_POTION_A", potion_item_id="T4_POTION_A",
        potion_name="Potion A", family="A", tier=4, enchantment_level=0, output_quantity=1,
        ingredients=[Ingredient("T4_ING_A", "Ing A", 1, 4)]
    )
    recipe_b = PotionRecipe(
        recipe_id="T4_POTION_B", potion_item_id="T4_POTION_B",
        potion_name="Potion B", family="B", tier=4, enchantment_level=0, output_quantity=1,
        ingredients=[Ingredient("T4_ING_B", "Ing B", 2, 4)]
    )
    
    raw_prices = [
        RawMarketPrice("T4_ING_A", 1, 100, "2026-07-06T12:00:00", 90, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_ING_B", 1, 100, "2026-07-06T12:00:00", 90, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_POTION_A", 1, 200, "2026-07-06T12:00:00", 190, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_POTION_B", 1, 300, "2026-07-06T12:00:00", 290, "2026-07-06T12:00:00")
    ]
    
    # Set parameters: MRR=0, fee=0, tax=0 to make math simple:
    # A: Cost = 100 * 1 = 100. Revenue = 200. Profit = 100. ROI = 1.0.
    # B: Cost = 100 * 2 = 200. Revenue = 300. Profit = 100. ROI = 0.5.
    params = CalculationParameters(Decimal("0.0"), Decimal("0.0"), Decimal("0.0"))
    
    repo = MockRecipeRepository([recipe_a, recipe_b])
    client = MockDataClient(raw_prices)
    price_service = PriceService()
    calculator = CraftCalculator()
    
    scanner = PotionScanner(repo, client, price_service, calculator)
    result = scanner.scan(params)
    
    calc_a = next(c for c in result.calculations if c.recipe.recipe_id == "T4_POTION_A")
    calc_b = next(c for c in result.calculations if c.recipe.recipe_id == "T4_POTION_B")
    
    assert calc_a.profit == calc_b.profit == Decimal("100")
    assert calc_a.roi == Decimal("1.0")
    assert calc_b.roi == Decimal("0.5")
    
    # A has higher ROI, so A must be the best calculation
    assert result.best_calculation_id == calc_a.calculation_id


def test_scan_tie_breaker_by_alphabetical_id(calc_parameters):
    """Verify deterministic tie-breaker selects alphabetically first potion_item_id when profit and ROI are identical."""
    # Recipe C: Potion ID "T4_POTION_C"
    # Recipe D: Potion ID "T4_POTION_D"
    # Both: Total Cost = 100, Net Revenue = 200, Profit = 100 (ROI = 1.0)
    # C should win because T4_POTION_C is alphabetically before T4_POTION_D
    recipe_c = PotionRecipe(
        recipe_id="T4_POTION_C", potion_item_id="T4_POTION_C",
        potion_name="Potion C", family="C", tier=4, enchantment_level=0, output_quantity=1,
        ingredients=[Ingredient("T4_ING", "Ing", 1, 4)]
    )
    recipe_d = PotionRecipe(
        recipe_id="T4_POTION_D", potion_item_id="T4_POTION_D",
        potion_name="Potion D", family="D", tier=4, enchantment_level=0, output_quantity=1,
        ingredients=[Ingredient("T4_ING", "Ing", 1, 4)]
    )
    
    raw_prices = [
        RawMarketPrice("T4_ING", 1, 100, "2026-07-06T12:00:00", 90, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_POTION_C", 1, 200, "2026-07-06T12:00:00", 190, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_POTION_D", 1, 200, "2026-07-06T12:00:00", 190, "2026-07-06T12:00:00")
    ]
    
    params = CalculationParameters(Decimal("0.0"), Decimal("0.0"), Decimal("0.0"))
    
    # We pass [recipe_d, recipe_c] in reverse order to ensure order in repository doesn't affect sorting
    repo = MockRecipeRepository([recipe_d, recipe_c])
    client = MockDataClient(raw_prices)
    price_service = PriceService()
    calculator = CraftCalculator()
    
    scanner = PotionScanner(repo, client, price_service, calculator)
    result = scanner.scan(params)
    
    calc_c = next(c for c in result.calculations if c.recipe.recipe_id == "T4_POTION_C")
    calc_d = next(c for c in result.calculations if c.recipe.recipe_id == "T4_POTION_D")
    
    assert calc_c.profit == calc_d.profit == Decimal("100")
    assert calc_c.roi == calc_d.roi == Decimal("1.0")
    
    # C is alphabetically first, so C must be the best calculation
    assert result.best_calculation_id == calc_c.calculation_id


def test_scan_one_profitable_recipe():
    """Verify scanner state when exactly one recipe is profitable and others are negative."""
    recipe_a = PotionRecipe(
        recipe_id="T4_POTION_A", potion_item_id="T4_POTION_A",
        potion_name="Potion A", family="A", tier=4, enchantment_level=0, output_quantity=1,
        ingredients=[Ingredient("T4_ING_A", "Ing A", 1, 4)]
    )
    recipe_b = PotionRecipe(
        recipe_id="T4_POTION_B", potion_item_id="T4_POTION_B",
        potion_name="Potion B", family="B", tier=4, enchantment_level=0, output_quantity=1,
        ingredients=[Ingredient("T4_ING_B", "Ing B", 1, 4)]
    )
    raw_prices = [
        RawMarketPrice("T4_ING_A", 1, 100, "2026-07-06T12:00:00", 90, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_POTION_A", 1, 200, "2026-07-06T12:00:00", 190, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_ING_B", 1, 150, "2026-07-06T12:00:00", 90, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_POTION_B", 1, 100, "2026-07-06T12:00:00", 190, "2026-07-06T12:00:00")
    ]
    params = CalculationParameters(Decimal("0.0"), Decimal("0.0"), Decimal("0.0"))
    repo = MockRecipeRepository([recipe_a, recipe_b])
    client = MockDataClient(raw_prices)
    price_service = PriceService()
    calculator = CraftCalculator()
    scanner = PotionScanner(repo, client, price_service, calculator)
    result = scanner.scan(params)

    assert result.has_profitable_opportunities is True
    assert result.best_calculation_id == next(c.calculation_id for c in result.calculations if c.recipe.recipe_id == "T4_POTION_A")


def test_scan_multiple_profitable_recipes():
    """Verify scanner state when multiple recipes are profitable."""
    recipe_a = PotionRecipe(
        recipe_id="T4_POTION_A", potion_item_id="T4_POTION_A",
        potion_name="Potion A", family="A", tier=4, enchantment_level=0, output_quantity=1,
        ingredients=[Ingredient("T4_ING_A", "Ing A", 1, 4)]
    )
    recipe_b = PotionRecipe(
        recipe_id="T4_POTION_B", potion_item_id="T4_POTION_B",
        potion_name="Potion B", family="B", tier=4, enchantment_level=0, output_quantity=1,
        ingredients=[Ingredient("T4_ING_B", "Ing B", 1, 4)]
    )
    raw_prices = [
        RawMarketPrice("T4_ING_A", 1, 100, "2026-07-06T12:00:00", 90, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_POTION_A", 1, 250, "2026-07-06T12:00:00", 190, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_ING_B", 1, 100, "2026-07-06T12:00:00", 90, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_POTION_B", 1, 200, "2026-07-06T12:00:00", 190, "2026-07-06T12:00:00")
    ]
    params = CalculationParameters(Decimal("0.0"), Decimal("0.0"), Decimal("0.0"))
    repo = MockRecipeRepository([recipe_a, recipe_b])
    client = MockDataClient(raw_prices)
    price_service = PriceService()
    calculator = CraftCalculator()
    scanner = PotionScanner(repo, client, price_service, calculator)
    result = scanner.scan(params)

    assert result.has_profitable_opportunities is True
    assert result.best_calculation_id == next(c.calculation_id for c in result.calculations if c.recipe.recipe_id == "T4_POTION_A")


def test_scan_all_recipes_negative():
    """Verify scanner state when all calculations have negative profit."""
    recipe_a = PotionRecipe(
        recipe_id="T4_POTION_A", potion_item_id="T4_POTION_A",
        potion_name="Potion A", family="A", tier=4, enchantment_level=0, output_quantity=1,
        ingredients=[Ingredient("T4_ING_A", "Ing A", 1, 4)]
    )
    recipe_b = PotionRecipe(
        recipe_id="T4_POTION_B", potion_item_id="T4_POTION_B",
        potion_name="Potion B", family="B", tier=4, enchantment_level=0, output_quantity=1,
        ingredients=[Ingredient("T4_ING_B", "Ing B", 1, 4)]
    )
    raw_prices = [
        RawMarketPrice("T4_ING_A", 1, 150, "2026-07-06T12:00:00", 90, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_POTION_A", 1, 100, "2026-07-06T12:00:00", 190, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_ING_B", 1, 150, "2026-07-06T12:00:00", 90, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_POTION_B", 1, 140, "2026-07-06T12:00:00", 190, "2026-07-06T12:00:00")
    ]
    params = CalculationParameters(Decimal("0.0"), Decimal("0.0"), Decimal("0.0"))
    repo = MockRecipeRepository([recipe_a, recipe_b])
    client = MockDataClient(raw_prices)
    price_service = PriceService()
    calculator = CraftCalculator()
    scanner = PotionScanner(repo, client, price_service, calculator)
    result = scanner.scan(params)

    assert result.has_profitable_opportunities is False
    assert result.best_calculation_id is None
    assert len(result.calculations) == 2
    sorted_calcs = sorted(result.calculations, key=lambda c: c.profit, reverse=True)
    assert sorted_calcs[0].recipe.recipe_id == "T4_POTION_B"
    assert sorted_calcs[1].recipe.recipe_id == "T4_POTION_A"


def test_scan_all_recipes_exactly_zero():
    """Verify scanner state when all calculations have exactly zero profit."""
    recipe_a = PotionRecipe(
        recipe_id="T4_POTION_A", potion_item_id="T4_POTION_A",
        potion_name="Potion A", family="A", tier=4, enchantment_level=0, output_quantity=1,
        ingredients=[Ingredient("T4_ING_A", "Ing A", 1, 4)]
    )
    raw_prices = [
        RawMarketPrice("T4_ING_A", 1, 100, "2026-07-06T12:00:00", 90, "2026-07-06T12:00:00"),
        RawMarketPrice("T4_POTION_A", 1, 100, "2026-07-06T12:00:00", 190, "2026-07-06T12:00:00")
    ]
    params = CalculationParameters(Decimal("0.0"), Decimal("0.0"), Decimal("0.0"))
    repo = MockRecipeRepository([recipe_a])
    client = MockDataClient(raw_prices)
    price_service = PriceService()
    calculator = CraftCalculator()
    scanner = PotionScanner(repo, client, price_service, calculator)
    result = scanner.scan(params)

    assert result.has_profitable_opportunities is False
    assert result.best_calculation_id is None
    assert len(result.calculations) == 1
    assert result.calculations[0].profit == Decimal("0")
