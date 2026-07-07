import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Optional
from src.domain.models import PotionRecipe, MarketPrice, CalculationParameters, ProfitCalculation

class CraftCalculator:
    """Service responsible for performing deterministic potion crafting profitability calculations."""

    def calculate_profitability(
        self,
        recipe: PotionRecipe,
        ingredient_prices: List[MarketPrice],
        potion_sell_price: MarketPrice,
        parameters: CalculationParameters
    ) -> ProfitCalculation:
        """
        Calculates the profitability of crafting a potion based on raw materials and market data.

        All calculations are performed using the Decimal type to maintain precision.

        Args:
            recipe: The recipe being evaluated.
            ingredient_prices: List of domain MarketPrice objects for the ingredients.
            potion_sell_price: Domain MarketPrice object for the output potion.
            parameters: Calculation parameters (tax rate, station fee, return rate).

        Returns:
            A validated ProfitCalculation object.
        """
        # Map ingredient prices by item_id for faster lookup and matching checks
        prices_by_item: Dict[str, MarketPrice] = {p.item_id: p for p in ingredient_prices}

        # Validate that we have prices for all recipe ingredients
        for ing in recipe.ingredients:
            if ing.item_id not in prices_by_item:
                raise ValueError(f"Missing price entry for recipe ingredient: '{ing.item_id}'")

        # 1. Gross ingredient cost
        gross_ingredient_cost = Decimal("0")
        for ing in recipe.ingredients:
            price = prices_by_item[ing.item_id]
            gross_ingredient_cost += Decimal(str(price.unit_price)) * Decimal(str(ing.quantity))

        # 2. Material Return Rate value
        returned_material_value = gross_ingredient_cost * parameters.material_return_rate

        # 3. Effective ingredient cost
        effective_ingredient_cost = gross_ingredient_cost - returned_material_value

        # 4. Total cost (effective ingredient cost + crafting station fee)
        total_cost = effective_ingredient_cost + parameters.crafting_station_fee

        # 5. Gross revenue
        gross_revenue = Decimal(str(potion_sell_price.unit_price)) * Decimal(str(recipe.output_quantity))

        # 6. Marketplace tax
        marketplace_tax = gross_revenue * parameters.marketplace_tax_rate

        # 7. Net revenue
        net_revenue = gross_revenue - marketplace_tax

        # 8. Profit
        profit = net_revenue - total_cost

        # 9. ROI (None if total_cost is 0)
        roi: Optional[Decimal] = None
        if total_cost > Decimal("0"):
            roi = profit / total_cost

        # 10. Profitability flag
        is_profitable = profit > Decimal("0")

        # 11. Generate warnings for missing/placeholder timestamps
        warnings: List[str] = []
        
        # Check ingredient prices
        for price in ingredient_prices:
            self._check_price_timestamp(price, warnings)
        # Check potion sell price
        self._check_price_timestamp(potion_sell_price, warnings)

        # Create unique ID and calculated timestamp
        calculation_id = f"calc-{uuid.uuid4().hex[:12]}"
        calculated_at = datetime.now(timezone.utc).isoformat()

        calc = ProfitCalculation(
            calculation_id=calculation_id,
            recipe=recipe,
            ingredient_prices=ingredient_prices,
            potion_sell_price=potion_sell_price,
            parameters=parameters,
            gross_ingredient_cost=gross_ingredient_cost,
            returned_material_value=returned_material_value,
            effective_ingredient_cost=effective_ingredient_cost,
            crafting_station_fee=parameters.crafting_station_fee,
            total_cost=total_cost,
            gross_revenue=gross_revenue,
            marketplace_tax=marketplace_tax,
            net_revenue=net_revenue,
            profit=profit,
            roi=roi,
            is_profitable=is_profitable,
            calculated_at=calculated_at,
            warnings=warnings
        )
        
        # Perform domain self-validation to guarantee correctness of internal fields
        calc.validate()
        return calc

    def _check_price_timestamp(self, price: MarketPrice, warnings: List[str]) -> None:
        if not price.observed_at:
            warnings.append(f"Price data for item '{price.item_id}' has no observed timestamp.")
        elif price.observed_at == "0001-01-01T00:00:00":
            warnings.append(f"Price data for item '{price.item_id}' has a placeholder timestamp and might be stale.")
