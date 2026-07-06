# Domain Model

This document defines the recipe-domain model for AlbionPotionScanner. It is
documentation only: no business logic, API access, or profit calculation is
defined here.

Source document:

```text
docs/research/ingredients-for-each-potion.md
```

## Modeling Goals

- Preserve recipe data exactly as researched.
- Represent unresolved recipe fields without guessing values.
- Keep item references reusable across potions, ingredients, and future item
  categories.
- Support Python dataclasses or Pydantic models later.
- Keep the JSON recipe database deterministic and versioned.

## Entity: ItemReference

Purpose: Identifies an Albion item without embedding market prices or recipe
logic.

Attributes:

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `item_id` | `str | null` | Yes | Albion unique item ID, such as `T4_POTION_HEAL`; `null` only when unresolved. |
| `name` | `str` | Yes | Human-readable item name from the source document. |
| `tier` | `int | null` | Yes | Numeric tier when known. |
| `resolution_status` | `str` | Yes | `resolved` or `unresolved`. |
| `notes` | `list[str]` | No | Source notes or warnings about the item reference. |

Relationships:

- Used by `PotionRecipe.output.item`.
- Used by `Ingredient.item`.

Validation rules:

- `resolution_status` must be `resolved` when `item_id` is present.
- `resolution_status` must be `unresolved` when `item_id` is `null`.
- `tier` must be between `1` and `8` when present.
- `name` must not be blank.

## Entity: Ingredient

Purpose: Represents one required input item in a potion recipe.

Attributes:

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `item` | `ItemReference` | Yes | Ingredient item reference. |
| `quantity` | `int | null` | Yes | Required quantity per craft action; `null` only when unresolved. |
| `quantity_status` | `str` | Yes | `resolved` or `unresolved`. |
| `notes` | `list[str]` | No | Ingredient-specific notes from validation. |

Relationships:

- Belongs to exactly one `PotionRecipe`.
- References exactly one `ItemReference`.

Validation rules:

- `quantity` must be a positive integer when `quantity_status` is `resolved`.
- `quantity` must be `null` when `quantity_status` is `unresolved`.
- If `item.resolution_status` is `unresolved`, the ingredient must carry a note
  explaining why.

## Entity: CraftOutput

Purpose: Describes what a craft action produces.

Attributes:

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `item` | `ItemReference` | Yes | Potion item produced by the recipe. |
| `quantity` | `int` | Yes | Number of potion units produced per craft action. |

Relationships:

- Belongs to exactly one `PotionRecipe`.

Validation rules:

- `quantity` must be a positive integer.
- `item.resolution_status` must be `resolved`.
- `item.item_id` must start with `T` and contain `_POTION_` for current scope.

## Entity: CraftCategory

Purpose: Groups recipes by crafting behavior from the source document.

Attributes:

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `category_id` | `str` | Yes | Stable identifier, such as `classic_potions` or `tracking_potions`. |
| `display_name` | `str` | Yes | Human-readable category label. |
| `base_output_quantity` | `int` | Yes | Expected craft output quantity for recipes in this category. |
| `notes` | `list[str]` | No | Category-level source notes. |

Relationships:

- Referenced by `PotionRecipe.category_id`.

Validation rules:

- `category_id` must be unique in the recipe database.
- `base_output_quantity` must be a positive integer.
- Each recipe referencing a category should use an output quantity matching the
  category base output unless a source note explains the exception.

## Entity: PotionRecipe

Purpose: Represents a single craftable potion recipe.

Attributes:

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `recipe_id` | `str` | Yes | Stable recipe ID; use the potion item ID for one-recipe-per-output. |
| `family` | `str` | Yes | Potion family, such as `Healing Potion`. |
| `category_id` | `str` | Yes | Reference to `CraftCategory.category_id`. |
| `tier` | `int` | Yes | Potion tier extracted from the source document. |
| `output` | `CraftOutput` | Yes | Produced potion and craft yield. |
| `ingredients` | `list[Ingredient]` | Yes | Ingredient list for one craft action. |
| `data_status` | `str` | Yes | `complete`, `incomplete`, or `deprecated`. |
| `source_notes` | `list[str]` | No | Notes preserving source warnings or naming inconsistencies. |

Relationships:

- References one `CraftCategory`.
- Owns one `CraftOutput`.
- Owns one or more `Ingredient` entries.

Validation rules:

- `recipe_id` must be unique and equal to `output.item.item_id` for current
  potion recipes.
- `tier` must match the leading tier in `output.item.item_id`.
- `ingredients` must not be empty.
- `data_status` must be `incomplete` if any ingredient item or quantity is
  unresolved.
- `data_status` must be `complete` only when all ingredients and quantities are
  resolved.

## Entity: RecipeDatabase

Purpose: Top-level container for the canonical structured recipe dataset.

Attributes:

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | `str` | Yes | Semantic version of this JSON structure. |
| `source_document` | `str` | Yes | Relative path to the source research document. |
| `scope` | `str` | Yes | Current scope, expected to be `potion_recipes`. |
| `categories` | `list[CraftCategory]` | Yes | Category definitions. |
| `recipes` | `list[PotionRecipe]` | Yes | Potion recipe records. |
| `validation_issues` | `list[RecipeValidationIssue]` | No | Dataset-level unresolved issues. |

Relationships:

- Owns all categories and recipes.
- `recipes[].category_id` must resolve to a category in `categories`.

Validation rules:

- `schema_version` must follow semantic versioning.
- Category IDs must be unique.
- Recipe IDs must be unique.
- All cross-references must resolve inside the database.

## Entity: RecipeValidationIssue

Purpose: Records unresolved or inconsistent source data without changing the
recipe itself.

Attributes:

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `issue_id` | `str` | Yes | Stable issue identifier. |
| `severity` | `str` | Yes | `info`, `warning`, or `blocking`. |
| `recipe_id` | `str | null` | Yes | Related recipe, if any. |
| `field` | `str | null` | Yes | Related field path, if any. |
| `description` | `str` | Yes | Human-readable issue description. |

Validation rules:

- `severity` must be `blocking` when missing data prevents a complete recipe.
- `recipe_id` must resolve to a recipe when present.

## Proposed JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/TeteuCoder/AlbionPotionScanner/schemas/recipe-database.schema.json",
  "title": "AlbionPotionScanner Recipe Database",
  "type": "object",
  "required": ["schema_version", "source_document", "scope", "categories", "recipes"],
  "additionalProperties": false,
  "properties": {
    "schema_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "source_document": {
      "type": "string",
      "minLength": 1
    },
    "scope": {
      "const": "potion_recipes"
    },
    "categories": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/$defs/CraftCategory" }
    },
    "recipes": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/$defs/PotionRecipe" }
    },
    "validation_issues": {
      "type": "array",
      "items": { "$ref": "#/$defs/RecipeValidationIssue" },
      "default": []
    }
  },
  "$defs": {
    "CraftCategory": {
      "type": "object",
      "required": ["category_id", "display_name", "base_output_quantity"],
      "additionalProperties": false,
      "properties": {
        "category_id": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_]*$"
        },
        "display_name": {
          "type": "string",
          "minLength": 1
        },
        "base_output_quantity": {
          "type": "integer",
          "minimum": 1
        },
        "notes": {
          "type": "array",
          "items": { "type": "string" },
          "default": []
        }
      }
    },
    "ItemReference": {
      "type": "object",
      "required": ["item_id", "name", "tier", "resolution_status"],
      "additionalProperties": false,
      "properties": {
        "item_id": {
          "type": ["string", "null"],
          "pattern": "^(T[0-9]_[A-Z0-9_]+(@[1-3])?|UNIQUE_[A-Z0-9_]+)$"
        },
        "name": {
          "type": "string",
          "minLength": 1
        },
        "tier": {
          "type": ["integer", "null"],
          "minimum": 1,
          "maximum": 8
        },
        "resolution_status": {
          "enum": ["resolved", "unresolved"]
        },
        "notes": {
          "type": "array",
          "items": { "type": "string" },
          "default": []
        }
      }
    },
    "Ingredient": {
      "type": "object",
      "required": ["item", "quantity", "quantity_status"],
      "additionalProperties": false,
      "properties": {
        "item": { "$ref": "#/$defs/ItemReference" },
        "quantity": {
          "type": ["integer", "null"],
          "minimum": 1
        },
        "quantity_status": {
          "enum": ["resolved", "unresolved"]
        },
        "notes": {
          "type": "array",
          "items": { "type": "string" },
          "default": []
        }
      }
    },
    "CraftOutput": {
      "type": "object",
      "required": ["item", "quantity"],
      "additionalProperties": false,
      "properties": {
        "item": { "$ref": "#/$defs/ItemReference" },
        "quantity": {
          "type": "integer",
          "minimum": 1
        }
      }
    },
    "PotionRecipe": {
      "type": "object",
      "required": [
        "recipe_id",
        "family",
        "category_id",
        "tier",
        "output",
        "ingredients",
        "data_status"
      ],
      "additionalProperties": false,
      "properties": {
        "recipe_id": {
          "type": "string",
          "pattern": "^T[0-9]_POTION_[A-Z0-9_]+$"
        },
        "family": {
          "type": "string",
          "minLength": 1
        },
        "category_id": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_]*$"
        },
        "tier": {
          "type": "integer",
          "minimum": 4,
          "maximum": 8
        },
        "output": { "$ref": "#/$defs/CraftOutput" },
        "ingredients": {
          "type": "array",
          "minItems": 1,
          "items": { "$ref": "#/$defs/Ingredient" }
        },
        "data_status": {
          "enum": ["complete", "incomplete", "deprecated"]
        },
        "source_notes": {
          "type": "array",
          "items": { "type": "string" },
          "default": []
        }
      }
    },
    "RecipeValidationIssue": {
      "type": "object",
      "required": ["issue_id", "severity", "recipe_id", "field", "description"],
      "additionalProperties": false,
      "properties": {
        "issue_id": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_]*$"
        },
        "severity": {
          "enum": ["info", "warning", "blocking"]
        },
        "recipe_id": {
          "type": ["string", "null"]
        },
        "field": {
          "type": ["string", "null"]
        },
        "description": {
          "type": "string",
          "minLength": 1
        }
      }
    }
  }
}
```

## Deterministic Database Shape

A future recipe database should use this layout:

```json
{
  "schema_version": "1.0.0",
  "source_document": "docs/research/ingredients-for-each-potion.md",
  "scope": "potion_recipes",
  "categories": [
    {
      "category_id": "classic_potions",
      "display_name": "Classic Potions",
      "base_output_quantity": 5,
      "notes": []
    },
    {
      "category_id": "tracking_potions",
      "display_name": "Tracking Potions",
      "base_output_quantity": 10,
      "notes": ["Introduced in Wild Blood according to source document."]
    }
  ],
  "recipes": [],
  "validation_issues": []
}
```

## Scope Boundary

This model intentionally excludes:

- Market prices
- City selection
- API response objects
- Profit calculations
- ROI calculations
- Station fee calculations
- Marketplace tax rules

Those concepts belong in later pricing and calculation models after their specs
are written. For V1, any later pricing or calculation model must use Brecilien
as the fixed operating city.
