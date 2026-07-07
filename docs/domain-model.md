# AlbionPotionScanner Domain Model

## Purpose

This document defines the Version 1 business domain model for
AlbionPotionScanner. It is the contract future specifications, plans, tasks,
and implementations must follow when representing potion recipes, market
prices, profitability calculations, and scanner results.

Version 1 answers one question:

"Considering that every step (buying ingredients, crafting and selling) happens
in Brecilien, which potion is the most profitable to craft right now?"

## Version 1 Scope

Version 1 has a fixed operating city:

- Ingredients are purchased in Brecilien.
- Potions are crafted in Brecilien.
- Finished potions are sold in Brecilien.

City selection is not part of the model. Brecilien is a project-wide
configuration value used by market access and calculations, not a user input
and not a domain entity.

## Modeling Principles

- Each entity has one business responsibility.
- Recipe data, market data, calculation inputs, calculation outputs, and scan
  aggregation remain separate.
- Calculations are deterministic from their explicit inputs.
- Derived values are stored only where they are calculation results.
- Recipe definitions do not contain market prices.
- Market prices do not contain recipe rules.
- Scan results do not recompute business rules in the UI.
- The model includes only entities required for Version 1.

## Entity Overview

Version 1 contains these business entities:

- `PotionRecipe`
- `Ingredient`
- `MarketPrice`
- `CalculationParameters`
- `ProfitCalculation`
- `ScanResult`

Supporting values such as item IDs, item names, tiers, price fields, and
timestamps are attributes of these entities. They are not separate entities in
Version 1 unless a future specification proves that separation is necessary.

## Fixed Operating City Constraint

Brecilien is a project-wide configuration value for Version 1. It is applied by
market access and calculation services before domain entities are created. The
domain model does not include a City entity, city selector, route, source city,
destination city, or city comparison.

## Entity: PotionRecipe

### Purpose

Represents one craftable potion recipe that can be evaluated for profitability.
A recipe defines the potion produced, the quantity produced per craft action,
and the ingredients required. It does not contain live prices, taxes, crafting
fees, or calculated profit.

### Attributes

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `recipe_id` | `string` | Required | Stable unique identifier for the recipe. For Version 1, this must match the produced potion item ID. |
| `potion_item_id` | `string` | Required | Albion item ID of the crafted potion. |
| `potion_name` | `string` | Required | Human-readable potion name. |
| `family` | `string` | Required | Potion family, such as Healing Potion or Poison Potion. |
| `tier` | `integer` | Required | Potion tier included in the Version 1 profitability scan. |
| `enchantment_level` | `integer` | Required | Enchantment level for the produced potion. Use `0` for the base item and positive values for enchanted variants. |
| `output_quantity` | `integer` | Required | Number of potion units produced by one craft action. |
| `ingredients` | `list<Ingredient>` | Required | Ingredients consumed by one craft action before Material Return Rate is applied. |
| `source_reference` | `string` | Optional | Reference to the research source used to define the recipe. |

### Relationships

`PotionRecipe`
contains many
`Ingredient`

`ProfitCalculation`
references one
`PotionRecipe`

### Validation Rules

- `recipe_id` cannot be empty.
- `potion_item_id` cannot be empty.
- `potion_item_id` must identify a potion item.
- `potion_name` cannot be empty.
- `family` cannot be empty.
- `tier` must be between 4 and 8.
- `enchantment_level` must be zero or greater.
- `output_quantity` must be greater than zero.
- `ingredients` must contain at least one ingredient.
- A recipe must not contain the same ingredient item more than once for the
  same enchantment level.
- `source_reference`, when provided, cannot be empty.

## Entity: Ingredient

### Purpose

Represents one item required to craft a potion. An ingredient belongs to a
recipe and defines the item and quantity consumed by one craft action before
Material Return Rate is applied. It does not contain market price data.

### Attributes

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `item_id` | `string` | Required | Albion item ID of the required ingredient. |
| `item_name` | `string` | Required | Human-readable ingredient name. |
| `tier` | `integer` | Optional | Ingredient tier when known and relevant to validation or display. |
| `quantity` | `integer` | Required | Quantity required for one craft action before Material Return Rate is applied. |

### Relationships

`Ingredient`
belongs to one
`PotionRecipe`

`MarketPrice`
may price the item identified by
`Ingredient.item_id`

### Validation Rules

- `item_id` cannot be empty.
- `item_name` cannot be empty.
- `tier`, when present, must be between 1 and 8.
- `quantity` must be greater than zero.
- An ingredient must not reference the same item ID as the potion produced by
  its recipe.

## Entity: MarketPrice

### Purpose

Represents the selected current Brecilien market price for one item. Market
prices are inputs to profitability calculations. They are sourced from the
Albion Online Data Project and are isolated from recipe definitions.

A `MarketPrice` represents the chosen usable price for the scanner, not the full
external API response.

### Attributes

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `item_id` | `string` | Required | Albion item ID being priced. |
| `quality` | `integer` | Required | Item quality used for the selected market price. |
| `price_role` | `string` | Required | Business use of the price. Allowed Version 1 roles are ingredient purchase and potion sale. |
| `price_field` | `string` | Required | Source market field used to select the price, such as sell order price or buy order price. |
| `unit_price` | `decimal` | Required | Selected price for one unit of the item in silver. |
| `observed_at` | `datetime` | Optional | Timestamp associated with the selected price, when available from the data source. |
| `source` | `string` | Required | Market data source name. For Version 1 this is Albion Online Data Project. |

### Relationships

`MarketPrice`
prices one item identified by
`item_id`

`ProfitCalculation`
uses many ingredient
`MarketPrice`

`ProfitCalculation`
uses one output potion
`MarketPrice`

### Validation Rules

- `item_id` cannot be empty.
- `quality` must be greater than zero.
- `price_role` must be ingredient purchase or potion sale.
- `price_field` cannot be empty.
- `unit_price` cannot be negative.
- `unit_price` equal to zero means no usable current price and must not be
  treated as a free item.
- `observed_at`, when present, must be a valid timestamp.
- `source` must be Albion Online Data Project for Version 1.
- A Version 1 market price is always for Brecilien, through project
  configuration. No city attribute is allowed on this entity.

## Entity: CalculationParameters

### Purpose

Represents explicit non-price inputs required to calculate profitability for a
single scan. These values are separated from recipes and market prices so the
calculator remains deterministic and testable.

### Attributes

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `material_return_rate` | `decimal` | Required | Material Return Rate applied to eligible ingredient cost. Expressed as a decimal fraction. |
| `crafting_station_fee` | `decimal` | Required | Brecilien crafting station fee applied to one craft action. |
| `marketplace_tax_rate` | `decimal` | Required | Marketplace tax rate applied to potion sale revenue. Expressed as a decimal fraction. |

### Relationships

`ProfitCalculation`
uses one
`CalculationParameters`

`ScanResult`
may reference one
`CalculationParameters`
when all calculations in the scan use the same values

### Validation Rules

- `material_return_rate` must be greater than or equal to zero.
- `material_return_rate` must be less than one.
- `crafting_station_fee` cannot be negative.
- `marketplace_tax_rate` cannot be negative.
- `marketplace_tax_rate` must be less than one.
- Parameters must be supplied explicitly. The domain model does not derive
  Material Return Rate from city bonuses in Version 1.

## Entity: ProfitCalculation

### Purpose

Represents the complete profitability calculation for one potion recipe using
current Brecilien market prices and explicit calculation parameters. This is
the core business result of the application.

The calculation contains both input references and derived values so results
can be displayed transparently without the UI recomputing business rules.

### Attributes

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `calculation_id` | `string` | Required | Stable identifier for this calculation within a scan. |
| `recipe` | `PotionRecipe` | Required | Recipe being evaluated. |
| `ingredient_prices` | `list<MarketPrice>` | Required | Selected Brecilien market prices for each recipe ingredient. |
| `potion_sell_price` | `MarketPrice` | Required | Selected Brecilien market price used as the sale value for the crafted potion. |
| `parameters` | `CalculationParameters` | Required | Non-price inputs used by the calculation. |
| `gross_ingredient_cost` | `decimal` | Required | Sum of ingredient quantities multiplied by their selected unit prices before Material Return Rate. |
| `returned_material_value` | `decimal` | Required | Silver value deducted from ingredient cost due to Material Return Rate. |
| `effective_ingredient_cost` | `decimal` | Required | Ingredient cost after returned material value is deducted. |
| `crafting_station_fee` | `decimal` | Required | Crafting fee used in this calculation. |
| `total_cost` | `decimal` | Required | Effective ingredient cost plus crafting station fee. |
| `gross_revenue` | `decimal` | Required | Potion output quantity multiplied by selected potion unit sale price. |
| `marketplace_tax` | `decimal` | Required | Marketplace tax amount deducted from gross revenue. |
| `net_revenue` | `decimal` | Required | Gross revenue minus marketplace tax. |
| `profit` | `decimal` | Required | Net revenue minus total cost. |
| `roi` | `decimal` | Optional | Profit divided by total cost. Optional only when ROI is undefined because total cost is zero. |
| `is_profitable` | `boolean` | Required | Whether `profit` is greater than zero. |
| `calculated_at` | `datetime` | Required | Time the calculation was produced. |
| `warnings` | `list<string>` | Optional | Non-blocking issues that affect interpretation, such as stale or missing price timestamps. |

### Relationships

`ProfitCalculation`
references one
`PotionRecipe`

`ProfitCalculation`
uses many ingredient
`MarketPrice`

`ProfitCalculation`
uses one potion sale
`MarketPrice`

`ProfitCalculation`
uses one
`CalculationParameters`

`ScanResult`
contains many
`ProfitCalculation`

### Validation Rules

- `calculation_id` cannot be empty.
- `ingredient_prices` must contain exactly one usable price for each ingredient
  item in the recipe.
- Each ingredient price must use the ingredient purchase role.
- `ingredient_prices` must not contain prices for items that are not recipe
  ingredients.
- `potion_sell_price.item_id` must match `recipe.potion_item_id`.
- `potion_sell_price` must use the potion sale role.
- All market prices used by the calculation must be Brecilien prices through
  the fixed Version 1 configuration.
- `gross_ingredient_cost` cannot be negative.
- `returned_material_value` cannot be negative.
- `returned_material_value` must not exceed `gross_ingredient_cost`.
- `effective_ingredient_cost` must equal `gross_ingredient_cost` minus
  `returned_material_value`.
- `crafting_station_fee` cannot be negative.
- `total_cost` must equal `effective_ingredient_cost` plus
  `crafting_station_fee`.
- `gross_revenue` cannot be negative.
- `marketplace_tax` cannot be negative.
- `marketplace_tax` must not exceed `gross_revenue`.
- `net_revenue` must equal `gross_revenue` minus `marketplace_tax`.
- `profit` must equal `net_revenue` minus `total_cost`.
- `profit` may be negative.
- `roi`, when present, must equal `profit` divided by `total_cost`.
- `roi` may be negative.
- `roi` must be absent when `total_cost` is zero.
- `is_profitable` must be true only when `profit` is greater than zero.
- `calculated_at` must be a valid timestamp.
- `warnings`, when present, must not contain empty values.

## Entity: ScanResult

### Purpose

Represents the result of running the profitability scanner across the Version 1
potion recipe set. It groups individual profit calculations, records scan-level
metadata, and identifies the most profitable potion under the fixed Brecilien
assumption.

### Attributes

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `scan_id` | `string` | Required | Stable identifier for a scanner run. |
| `generated_at` | `datetime` | Required | Time the scan result was produced. |
| `calculations` | `list<ProfitCalculation>` | Required | Profit calculations produced for the scanned potion recipes. |
| `best_calculation_id` | `string` | Optional | Identifier of the calculation with the highest profit. Optional only when there are no valid calculations. |
| `scanned_recipe_count` | `integer` | Required | Number of recipes considered by the scanner. |
| `valid_calculation_count` | `integer` | Required | Number of calculations that produced a usable profitability result. |
| `skipped_recipe_count` | `integer` | Required | Number of recipes skipped because required inputs were unavailable or invalid. |
| `warnings` | `list<string>` | Optional | Scan-level warnings that apply to the result set. |

### Relationships

`ScanResult`
contains many
`ProfitCalculation`

`ScanResult.best_calculation_id`
references one contained
`ProfitCalculation`

### Validation Rules

- `scan_id` cannot be empty.
- `generated_at` must be a valid timestamp.
- `calculations` may be empty only when no recipe can be calculated.
- `best_calculation_id`, when present, must reference a calculation contained
  in `calculations`.
- `best_calculation_id` must identify the calculation with the highest `profit`.
- If two or more calculations have the same highest `profit`, the scanner must
  use a deterministic tie-break rule defined by the implementation plan before
  release.
- `scanned_recipe_count` must be greater than or equal to zero.
- `valid_calculation_count` must equal the number of calculations in
  `calculations`.
- `skipped_recipe_count` must equal `scanned_recipe_count` minus
  `valid_calculation_count`.
- Counts cannot be negative.
- `warnings`, when present, must not contain empty values.

## Cross-Entity Rules

- Every `ProfitCalculation` must be reproducible from its `PotionRecipe`,
  `MarketPrice` entries, and `CalculationParameters`.
- A scan must not mix market data from different operating cities.
- Version 1 must not expose city as a user-selectable value.
- A recipe may exist without market prices, but it cannot produce a valid
  `ProfitCalculation` until all required prices are available.
- A market price may exist without a recipe, but unused prices must not affect
  profitability calculations.
- The UI must consume `ScanResult` and `ProfitCalculation` data without
  recalculating profit, ROI, taxes, or ingredient costs.
- Calculation warnings must be surfaced as result metadata, not hidden inside
  display text.

## Excluded From Version 1

The following concepts are intentionally not part of this domain model:

- Focus.
- Profit per Focus.
- Multiple cities.
- City selection.
- Different buying and selling cities.
- Route optimization.
- Arbitrage.
- Transportation cost.
- Best city recommendation.
- Automatic Return Rate calculation based on city bonuses.
- Historical prices.
- User accounts.
- Persistence models.
- Database tables.
- External API request or response models.
- Python classes or implementation structures.
