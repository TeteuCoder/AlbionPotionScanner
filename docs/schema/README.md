# Recipe Schema

## Purpose

`potion-recipe.schema.json` validates `data/potion-recipes.json`, the Version 1
potion recipe database for AlbionPotionScanner.

The recipe file is expected to be an array of `PotionRecipe` entries. Each
recipe contains its produced potion, output quantity, and the ingredients
required for one craft action before Material Return Rate is applied.

The schema validates only recipe structure. It does not validate market prices,
profit calculations, scan results, API responses, persistence, Focus,
transportation, or city selection.

## Schema Version

The schema uses JSON Schema Draft 2020-12:

`https://json-schema.org/draft/2020-12/schema`

## Relationship With The Domain Model

This schema is derived from `docs/domain-model.md`.

It covers the `PotionRecipe` and `Ingredient` entities only:

- `PotionRecipe.recipe_id`
- `PotionRecipe.potion_item_id`
- `PotionRecipe.potion_name`
- `PotionRecipe.family`
- `PotionRecipe.tier`
- `PotionRecipe.enchantment_level`
- `PotionRecipe.output_quantity`
- `PotionRecipe.ingredients`
- `PotionRecipe.source_reference`
- `Ingredient.item_id`
- `Ingredient.item_name`
- `Ingredient.tier`
- `Ingredient.quantity`

Fields marked optional in the Domain Model remain optional in the schema.
Therefore `source_reference` and `Ingredient.tier` are defined but not required.

## Validation Coverage

The schema enforces rules that JSON Schema can represent directly:

- Required properties.
- String types and non-empty strings.
- Integer types.
- Potion tier range from 4 through 8.
- Ingredient tier range from 1 through 8.
- Minimum values for quantities, output quantity, and enchantment level.
- Minimum ingredient array length.
- Potion item ID shape for T4 through T8 potion IDs.
- General Albion item ID shape for ingredients.

Some Domain Model rules require cross-field or collection-aware business logic
and are intentionally not encoded here:

- `recipe_id` must equal `potion_item_id`.
- A recipe must not contain duplicate ingredient item IDs.
- An ingredient item ID must not match the produced potion item ID.
- `tier` must match the tier embedded in `potion_item_id`.
- `enchantment_level` must match the enchantment suffix embedded in
  `potion_item_id`.

Those checks belong in application validation, not in this schema.

## How To Validate

Use any JSON Schema validator that supports Draft 2020-12.

Validate this file:

`data/potion-recipes.json`

Against this schema:

`docs/schema/potion-recipe.schema.json`

The schema validates the recipe database shape only. A valid recipe file is not
proof that market prices exist or that a potion can produce a profitable scan
result.

## Extension Strategy

Version 1 defines only the fields approved in the Domain Model. The schema does
not define Version 2 fields.

The schema is designed to be extended later by adding new definitions or
properties while preserving the Version 1 required fields. Future additions such
as potion categories, richer metadata, or expanded recipe annotations should be
introduced through an updated Domain Model and a schema version change.

Consumers should depend only on the documented Version 1 fields until a future
schema explicitly adds more fields.
