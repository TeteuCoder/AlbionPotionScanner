import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Set, Dict
from src.domain.models import (
    PotionRecipe,
    MarketPrice as DomainMarketPrice,
    CalculationParameters,
    ProfitCalculation,
    ScanResult
)
from src.repositories.recipe_repository import JsonRecipeRepository
from src.clients.albion_data_client import AlbionDataClient
from src.services.price_service import PriceService, PotionSaleStrategy, PriceServiceError
from src.services.craft_calculator import CraftCalculator

class PotionScanner:
    """Orchestrates loading potion recipes, fetching live market prices, selecting prices, and calculating profitabilities."""

    def __init__(
        self,
        recipe_repository: JsonRecipeRepository,
        data_client: AlbionDataClient,
        price_service: PriceService,
        calculator: CraftCalculator
    ):
        self.recipe_repository = recipe_repository
        self.data_client = data_client
        self.price_service = price_service
        self.calculator = calculator

    def scan(
        self,
        parameters: CalculationParameters,
        qualities: Optional[List[int]] = None,
        sale_strategy: PotionSaleStrategy = PotionSaleStrategy.SELL_ORDER
    ) -> ScanResult:
        """
        Runs the profitability scan across all registered recipes.

        Queries the Albion Online Data Project API in a single batch request to avoid
        repeated identical queries and network overhead.

        Args:
            parameters: Non-price calculation parameters (tax, fee, MRR).
            qualities: Optional list of item qualities to fetch. Defaults to Normal (1).
            sale_strategy: The pricing strategy for selling potions. Defaults to SELL_ORDER.

        Returns:
            A validated ScanResult.
        """
        recipes = self.recipe_repository.get_all()
        scanned_recipe_count = len(recipes)
        scan_warnings: List[str] = []

        if scanned_recipe_count == 0:
            scan_id = f"scan-{uuid.uuid4().hex[:12]}"
            generated_at = datetime.now(timezone.utc).isoformat()
            result = ScanResult(
                scan_id=scan_id,
                generated_at=generated_at,
                calculations=[],
                scanned_recipe_count=0,
                valid_calculation_count=0,
                skipped_recipe_count=0,
                best_calculation_id=None,
                has_profitable_opportunities=False,
                warnings=["Nenhuma receita disponivel para analise."]
            )
            result.validate()
            return result

        # Collect unique item IDs to batch query
        unique_item_ids: Set[str] = set()
        for recipe in recipes:
            unique_item_ids.add(recipe.potion_item_id)
            for ing in recipe.ingredients:
                unique_item_ids.add(ing.item_id)

        # Query all prices in one single batch HTTP request
        raw_prices = self.data_client.fetch_prices(list(unique_item_ids), qualities)

        calculations: List[ProfitCalculation] = []

        for recipe in recipes:
            try:
                # 1. Select potion sell price
                potion_price = self.price_service.select_price(
                    raw_prices=raw_prices,
                    item_id=recipe.potion_item_id,
                    role="potion sale",
                    quality=1,  # V1 assumes quality 1 for standard crafting output
                    sale_strategy=sale_strategy
                )

                # 2. Select ingredient prices
                ingredient_prices: List[DomainMarketPrice] = []
                for ing in recipe.ingredients:
                    ing_price = self.price_service.select_price(
                        raw_prices=raw_prices,
                        item_id=ing.item_id,
                        role="ingredient purchase",
                        quality=1  # V1 assumes quality 1 for standard ingredient purchase
                    )
                    ingredient_prices.append(ing_price)

                # 3. Calculate profitability
                calculation = self.calculator.calculate_profitability(
                    recipe=recipe,
                    ingredient_prices=ingredient_prices,
                    potion_sell_price=potion_price,
                    parameters=parameters
                )
                calculations.append(calculation)

            except PriceServiceError as e:
                # Price selection failed (e.g. missing price, 0 value)
                scan_warnings.append(
                    f"Receita '{recipe.recipe_id}' ignorada: {e}"
                )
            except ValueError as e:
                # Validation error occurred on recipe or output
                scan_warnings.append(
                    f"Receita '{recipe.recipe_id}' ignorada devido a erro de validação: {e}"
                )

        valid_calculation_count = len(calculations)
        skipped_recipe_count = scanned_recipe_count - valid_calculation_count

        # Determine the best calculation using the deterministic tie-break rules:
        # 1. Highest profit
        # 2. Highest ROI (ROI present > ROI None)
        # 3. Alphabetically first potion_item_id
        best_calculation_id: Optional[str] = None
        has_profitable_opportunities = False
        if calculations:
            has_profitable_opportunities = any(c.profit > Decimal("0") for c in calculations)
            if has_profitable_opportunities:
                def sort_key(c):
                    profit_val = c.profit
                    roi_val = c.roi if c.roi is not None else Decimal("-inf")
                    return (-profit_val, -roi_val, c.recipe.potion_item_id)

                sorted_calcs = sorted(calculations, key=sort_key)
                best_calculation_id = sorted_calcs[0].calculation_id

        scan_id = f"scan-{uuid.uuid4().hex[:12]}"
        generated_at = datetime.now(timezone.utc).isoformat()

        result = ScanResult(
            scan_id=scan_id,
            generated_at=generated_at,
            calculations=calculations,
            scanned_recipe_count=scanned_recipe_count,
            valid_calculation_count=valid_calculation_count,
            skipped_recipe_count=skipped_recipe_count,
            best_calculation_id=best_calculation_id,
            has_profitable_opportunities=has_profitable_opportunities,
            warnings=scan_warnings
        )
        
        result.validate()
        return result
