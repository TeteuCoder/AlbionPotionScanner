import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

# Match valid Albion potion item ID for T4-T8 potions: e.g. T4_POTION_HEAL or T8_POTION_COOLDOWN@1
POTION_ITEM_ID_PATTERN = re.compile(r"^T[4-8]_POTION_[A-Z0-9_]+(@[1-3])?$")

@dataclass(frozen=True)
class Ingredient:
    item_id: str
    item_name: str
    quantity: int
    tier: Optional[int] = None

    def validate(self) -> None:
        if not self.item_id:
            raise ValueError("Ingredient item_id cannot be empty")
        if not self.item_name:
            raise ValueError("Ingredient item_name cannot be empty")
        if self.tier is not None and not (1 <= self.tier <= 8):
            raise ValueError("Ingredient tier must be between 1 and 8")
        if self.quantity <= 0:
            raise ValueError("Ingredient quantity must be greater than zero")


@dataclass(frozen=True)
class PotionRecipe:
    recipe_id: str
    potion_item_id: str
    potion_name: str
    family: str
    tier: int
    enchantment_level: int
    output_quantity: int
    ingredients: List[Ingredient] = field(default_factory=list)
    source_reference: Optional[str] = None

    def validate(self) -> None:
        if not self.recipe_id:
            raise ValueError("recipe_id cannot be empty")
        if not self.potion_item_id:
            raise ValueError("potion_item_id cannot be empty")
        if not POTION_ITEM_ID_PATTERN.match(self.potion_item_id):
            raise ValueError(f"potion_item_id '{self.potion_item_id}' must identify a valid T4-T8 potion item")
        if self.recipe_id != self.potion_item_id:
            raise ValueError(f"recipe_id '{self.recipe_id}' must match potion_item_id '{self.potion_item_id}'")
        if not self.potion_name:
            raise ValueError("potion_name cannot be empty")
        if not self.family:
            raise ValueError("family cannot be empty")
        if not (4 <= self.tier <= 8):
            raise ValueError("tier must be between 4 and 8")
        if self.enchantment_level < 0:
            raise ValueError("enchantment_level must be zero or greater")
        if self.output_quantity <= 0:
            raise ValueError("output_quantity must be greater than zero")
        if not self.ingredients:
            raise ValueError("ingredients must contain at least one ingredient")

        seen_ingredients = set()
        for ing in self.ingredients:
            ing.validate()
            if ing.item_id == self.potion_item_id:
                raise ValueError(f"Ingredient item_id '{ing.item_id}' cannot be the same as the potion item ID")
            if ing.item_id in seen_ingredients:
                raise ValueError(f"Duplicate ingredient item_id '{ing.item_id}' in recipe")
            seen_ingredients.add(ing.item_id)

        if self.source_reference is not None and not self.source_reference:
            raise ValueError("source_reference, when provided, cannot be empty")


@dataclass(frozen=True)
class MarketPrice:
    """Selected Brecilien market price for one item, mapped to the domain entity in docs/domain-model.md."""
    item_id: str
    quality: int
    price_role: str
    price_field: str
    unit_price: int
    source: str = "Albion Online Data Project"
    observed_at: Optional[str] = None

    def validate(self) -> None:
        if not self.item_id:
            raise ValueError("MarketPrice item_id cannot be empty")
        if self.quality <= 0:
            raise ValueError("MarketPrice quality must be greater than zero")
        if self.price_role not in ("ingredient purchase", "potion sale"):
            raise ValueError("MarketPrice price_role must be 'ingredient purchase' or 'potion sale'")
        if not self.price_field:
            raise ValueError("MarketPrice price_field cannot be empty")
        if self.unit_price <= 0:
            raise ValueError("MarketPrice unit_price must be greater than zero (0 is not a usable price)")
        if self.source != "Albion Online Data Project":
            raise ValueError("MarketPrice source must be 'Albion Online Data Project' in Version 1")
        if self.observed_at is not None and not self.observed_at:
            raise ValueError("MarketPrice observed_at, when provided, cannot be empty")


@dataclass(frozen=True)
class CalculationParameters:
    """Explicit parameters required for potion profitability calculations."""
    material_return_rate: Decimal
    crafting_station_fee: Decimal
    marketplace_tax_rate: Decimal

    def validate(self) -> None:
        if self.material_return_rate < Decimal("0") or self.material_return_rate >= Decimal("1"):
            raise ValueError("material_return_rate must be between 0 (inclusive) and 1 (exclusive)")
        if self.crafting_station_fee < Decimal("0"):
            raise ValueError("crafting_station_fee cannot be negative")
        if self.marketplace_tax_rate < Decimal("0") or self.marketplace_tax_rate >= Decimal("1"):
            raise ValueError("marketplace_tax_rate must be between 0 (inclusive) and 1 (exclusive)")


@dataclass(frozen=True)
class ProfitCalculation:
    """Represents the complete profitability calculation for one potion recipe."""
    calculation_id: str
    recipe: PotionRecipe
    ingredient_prices: List[MarketPrice]
    potion_sell_price: MarketPrice
    parameters: CalculationParameters
    gross_ingredient_cost: Decimal
    returned_material_value: Decimal
    effective_ingredient_cost: Decimal
    crafting_station_fee: Decimal
    total_cost: Decimal
    gross_revenue: Decimal
    marketplace_tax: Decimal
    net_revenue: Decimal
    profit: Decimal
    calculated_at: str
    roi: Optional[Decimal] = None
    is_profitable: bool = False
    warnings: List[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.calculation_id:
            raise ValueError("calculation_id cannot be empty")
        if not self.calculated_at:
            raise ValueError("calculated_at cannot be empty")

        self.recipe.validate()
        self.parameters.validate()

        # Validate ingredient prices list structure and match with recipe ingredients
        recipe_ing_ids = {ing.item_id for ing in self.recipe.ingredients}
        provided_ing_ids = set()

        for price in self.ingredient_prices:
            price.validate()
            if price.price_role != "ingredient purchase":
                raise ValueError(f"Ingredient price for '{price.item_id}' must have 'ingredient purchase' role")
            if price.item_id not in recipe_ing_ids:
                raise ValueError(f"Price provided for item '{price.item_id}' which is not in recipe ingredients")
            if price.item_id in provided_ing_ids:
                raise ValueError(f"Duplicate price entry provided for ingredient '{price.item_id}'")
            provided_ing_ids.add(price.item_id)

        if provided_ing_ids != recipe_ing_ids:
            missing_ids = recipe_ing_ids - provided_ing_ids
            raise ValueError(f"Missing price entries for recipe ingredients: {missing_ids}")

        # Validate potion sell price
        self.potion_sell_price.validate()
        if self.potion_sell_price.item_id != self.recipe.potion_item_id:
            raise ValueError(
                f"potion_sell_price item_id '{self.potion_sell_price.item_id}' "
                f"must match recipe potion_item_id '{self.recipe.potion_item_id}'"
            )
        if self.potion_sell_price.price_role != "potion sale":
            raise ValueError("potion_sell_price must have 'potion sale' role")

        # Validate financial invariants
        if self.gross_ingredient_cost < Decimal("0"):
            raise ValueError("gross_ingredient_cost cannot be negative")
        if self.returned_material_value < Decimal("0"):
            raise ValueError("returned_material_value cannot be negative")
        if self.returned_material_value > self.gross_ingredient_cost:
            raise ValueError("returned_material_value cannot exceed gross_ingredient_cost")
        if self.effective_ingredient_cost != self.gross_ingredient_cost - self.returned_material_value:
            raise ValueError("effective_ingredient_cost must equal gross_ingredient_cost minus returned_material_value")
        if self.crafting_station_fee < Decimal("0"):
            raise ValueError("crafting_station_fee cannot be negative")
        if self.total_cost != self.effective_ingredient_cost + self.crafting_station_fee:
            raise ValueError("total_cost must equal effective_ingredient_cost plus crafting_station_fee")
        if self.gross_revenue < Decimal("0"):
            raise ValueError("gross_revenue cannot be negative")
        if self.marketplace_tax < Decimal("0"):
            raise ValueError("marketplace_tax cannot be negative")
        if self.marketplace_tax > self.gross_revenue:
            raise ValueError("marketplace_tax cannot exceed gross_revenue")
        if self.net_revenue != self.gross_revenue - self.marketplace_tax:
            raise ValueError("net_revenue must equal gross_revenue minus marketplace_tax")
        if self.profit != self.net_revenue - self.total_cost:
            raise ValueError("profit must equal net_revenue minus total_cost")

        # ROI check
        if self.total_cost == Decimal("0"):
            if self.roi is not None:
                raise ValueError("roi must be absent (None) when total_cost is zero")
        else:
            if self.roi is None:
                raise ValueError("roi must be present when total_cost is non-zero")
            expected_roi = self.profit / self.total_cost
            if abs(self.roi - expected_roi) > Decimal("0.0001"):
                raise ValueError(f"roi '{self.roi}' does not match expected roi '{expected_roi}'")

        if self.is_profitable != (self.profit > Decimal("0")):
            raise ValueError("is_profitable must be True if and only if profit is greater than zero")

        for warning in self.warnings:
            if not warning:
                raise ValueError("warnings cannot contain empty values")


@dataclass(frozen=True)
class ScanResult:
    """Represents the results of running the profitability scanner across all potion recipes."""
    scan_id: str
    generated_at: str
    calculations: List[ProfitCalculation]
    scanned_recipe_count: int
    valid_calculation_count: int
    skipped_recipe_count: int
    best_calculation_id: Optional[str] = None
    has_profitable_opportunities: bool = False
    warnings: List[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.scan_id:
            raise ValueError("scan_id cannot be empty")
        if not self.generated_at:
            raise ValueError("generated_at cannot be empty")
        if self.scanned_recipe_count < 0:
            raise ValueError("scanned_recipe_count cannot be negative")
        if self.valid_calculation_count < 0:
            raise ValueError("valid_calculation_count cannot be negative")
        if self.skipped_recipe_count < 0:
            raise ValueError("skipped_recipe_count cannot be negative")
        if self.valid_calculation_count != len(self.calculations):
            raise ValueError(
                f"valid_calculation_count '{self.valid_calculation_count}' "
                f"must equal length of calculations '{len(self.calculations)}'"
            )
        if self.skipped_recipe_count != self.scanned_recipe_count - self.valid_calculation_count:
            raise ValueError(
                f"skipped_recipe_count '{self.skipped_recipe_count}' must equal "
                f"scanned_recipe_count '{self.scanned_recipe_count}' minus "
                f"valid_calculation_count '{self.valid_calculation_count}'"
            )

        for calc in self.calculations:
            calc.validate()

        # Validate has_profitable_opportunities matches calculations profit > 0
        has_profit = any(c.profit > Decimal("0") for c in self.calculations)
        if self.has_profitable_opportunities != has_profit:
            raise ValueError(
                f"has_profitable_opportunities must be {has_profit} "
                f"based on calculation profits, but got {self.has_profitable_opportunities}"
            )

        # Validate best_calculation_id using deterministic tie-break rules
        if self.calculations and self.has_profitable_opportunities:
            # Sort calculations by:
            # 1. Profit descending
            # 2. ROI descending (treat None as negative infinity)
            # 3. Potion Item ID alphabetically (ascending)
            def sort_key(c):
                profit_val = c.profit
                roi_val = c.roi if c.roi is not None else Decimal("-inf")
                # We return a tuple representing keys in order. Since sorted() sorts ascending,
                # we negate numeric values to sort them descending.
                return (-profit_val, -roi_val, c.recipe.potion_item_id)

            sorted_calcs = sorted(self.calculations, key=sort_key)
            expected_best = sorted_calcs[0]

            if not self.best_calculation_id:
                raise ValueError("best_calculation_id must be present when profitable calculations are available")

            if self.best_calculation_id != expected_best.calculation_id:
                raise ValueError(
                    f"best_calculation_id '{self.best_calculation_id}' must match the top calculation "
                    f"'{expected_best.calculation_id}' (item_id: '{expected_best.recipe.potion_item_id}', "
                    f"profit: {expected_best.profit}, roi: {expected_best.roi})"
                )
        else:
            if self.best_calculation_id is not None:
                raise ValueError("best_calculation_id must be None when no profitable calculations were produced")

        for warning in self.warnings:
            if not warning:
                raise ValueError("warnings cannot contain empty values")


