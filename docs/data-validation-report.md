# Potion Recipe Data Validation Report

## Result

Validation succeeded.

`data/potion-recipes.json` was generated from the corrected canonical recipe
documentation and validated against the Version 1 recipe schema constraints and
required cross-field rules.

## Inputs

- `docs/research/ingredients-for-each-potion.md`
- `docs/domain-model.md`
- `docs/schema/potion-recipe.schema.json`

## Output

- `data/potion-recipes.json`

## Summary

| Check | Result |
| --- | --- |
| Total documented recipes | 32 |
| Total generated recipe objects | 32 |
| Validation success | Yes |
| Recipes with missing data | 0 |
| Duplicate recipe IDs | 0 |
| Duplicate ingredient IDs inside the same recipe | 0 |
| Schema validation summary | Passed |

## Corrected Source Data

The previously unresolved `T4_POTION_BERSERK` ingredient data has been resolved
in the canonical recipe documentation.

Resolved ingredients for `T4_POTION_BERSERK`:

| Item ID | Name | Quantity |
| --- | --- | --- |
| `T3_ALCHEMY_RARE_WEREWOLF` | Rugged Werewolf Fangs | 1 |
| `T4_BURDOCK` | Crenellated Burdock | 16 |

## Schema Validation Summary

Every generated recipe object includes the schema-defined fields:

- `recipe_id`
- `potion_item_id`
- `potion_name`
- `family`
- `tier`
- `enchantment_level`
- `output_quantity`
- `ingredients`
- `source_reference`

Every generated ingredient object includes:

- `item_id`
- `item_name`
- `tier`
- `quantity`

Validated schema constraints:

- Recipe database is a non-empty array.
- Every recipe contains all required fields.
- Every ingredient contains all required fields.
- Recipe and ingredient string fields are non-empty.
- Potion item IDs match the Version 1 T4-T8 potion item ID pattern.
- Ingredient item IDs match the Albion item ID pattern.
- Potion tiers are between 4 and 8.
- Ingredient tiers are between 1 and 8.
- Enchantment levels are zero or greater.
- Output quantities are positive integers.
- Ingredient quantities are positive integers.
- Every recipe contains at least one ingredient.

## Cross-Field Validation Summary

Validated project rules:

- `recipe_id == potion_item_id` for every recipe.
- Recipe `tier` matches the tier encoded in `potion_item_id`.
- `enchantment_level` matches the enchantment suffix encoded in
  `potion_item_id`; all Version 1 generated recipes are base items with
  `enchantment_level` set to `0`.
- No ingredient quantity is zero or negative.
- No output quantity is zero or negative.
- Every recipe contains at least one ingredient.
- No duplicate recipe IDs were found.
- No duplicate ingredient IDs were found inside any single recipe.
- No ingredient item ID matches its produced potion item ID.

## Duplicate Recipe IDs

No duplicate recipe IDs were detected.

Observed recipe heading count: 32.

Unique recipe ID count: 32.

## Duplicate Ingredient IDs Inside Recipes

No duplicate ingredient IDs were detected inside any recipe.

## Missing Data

No missing recipe data remains in the generated Version 1 recipe database.
