# Formulas

This document defines accounting formulas for future implementation. It does
not define Albion-specific constants, tax rates, station fee rules, material
return rounding, or recipe quantities. Those inputs must come from verified
sources before implementation.

## Required Inputs

- `sell_price`: selected market sell price for the crafted potion
- `ingredient_unit_price`: selected market price for each ingredient
- `ingredient_quantity`: verified recipe quantity for each ingredient
- `returned_material_value`: silver value of materials returned by confirmed
  Material Return Rate rules
- `crafting_station_fee`: confirmed station fee for the craft
- `marketplace_tax`: confirmed tax amount for the sale

For V1, all market prices and crafting assumptions use Brecilien. The formulas
must not compare cities, include transportation cost, optimize Focus usage, or
derive Return Rate automatically from city bonuses.

## Ingredient Cost

```text
gross_ingredient_cost =
  sum(ingredient_unit_price * ingredient_quantity for each ingredient)
```

This formula is arithmetic only. The ingredient list and quantities are unknown
until recipe data is verified.

## Material Return Rate

```text
effective_ingredient_cost =
  gross_ingredient_cost - returned_material_value
```

`returned_material_value` must be calculated from confirmed game rules. Do not
assume rounding behavior, eligible materials, focus effects, or city bonuses
until those rules are documented.

## Crafting Cost

```text
crafting_cost =
  effective_ingredient_cost + crafting_station_fee
```

The station fee formula itself is not confirmed in this document.

## Marketplace Tax

```text
net_revenue =
  sell_price - marketplace_tax
```

The tax rate and tax base must be confirmed before implementation.

## Final Profit

```text
profit =
  net_revenue - crafting_cost
```

Equivalent expanded form:

```text
profit =
  sell_price
  - marketplace_tax
  - effective_ingredient_cost
  - crafting_station_fee
```

## ROI

```text
roi =
  profit / crafting_cost
```

Percentage form:

```text
roi_percent =
  (profit / crafting_cost) * 100
```

If `crafting_cost` is zero or unavailable, ROI is undefined and must not be
reported as zero.

## Validation Requirements

Before these formulas are implemented, the project must confirm:

- Recipe ingredients and quantities
- Material Return Rate eligibility and rounding behavior
- Crafting station fee calculation
- Marketplace tax rate and tax base
- Which market price field is used as `sell_price`
- Brecilien-specific station fee inputs, without adding city selection to V1
