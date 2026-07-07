# Potion Item IDs

This document structures potion-related item IDs from:

```text
C:\Users\mathe\Downloads\Geral\items.txt
```

Only potion-related items are included. Food, bags, weapons, armor, and other
non-potion categories remain out of scope.

## Profit Scope

- T4+ potions are the target set for profit calculations.
- T2 and T3 potions are included for catalog awareness only.
- T2 and T3 entries must not drive potion crafter specs unless a later
  specification explicitly changes scope.
- Recipe ingredients and quantities are not documented here.

## Market Variant Rule

The source catalog contains base potion IDs and enchantment variants using
suffixes:

```json
["", "@1", "@2", "@3"]
```

Example:

```json
[
  "T4_POTION_HEAL",
  "T4_POTION_HEAL@1",
  "T4_POTION_HEAL@2",
  "T4_POTION_HEAL@3"
]
```

## Awareness-Only Low-Tier Potions

These items exist in the catalog, but they are outside the initial profitability
scanner scope.

```json
[
  {
    "family": "Healing Potion",
    "tier": "T2",
    "base_item_id": "T2_POTION_HEAL",
    "display_name": "Minor Healing Potion",
    "scope": "awareness_only"
  },
  {
    "family": "Energy Potion",
    "tier": "T2",
    "base_item_id": "T2_POTION_ENERGY",
    "display_name": "Minor Energy Potion",
    "scope": "awareness_only"
  },
  {
    "family": "Gigantify Potion",
    "tier": "T3",
    "base_item_id": "T3_POTION_REVIVE",
    "display_name": "Minor Gigantify Potion",
    "scope": "awareness_only"
  },
  {
    "family": "Resistance Potion",
    "tier": "T3",
    "base_item_id": "T3_POTION_STONESKIN",
    "display_name": "Minor Resistance Potion",
    "scope": "awareness_only"
  },
  {
    "family": "Sticky Potion",
    "tier": "T3",
    "base_item_id": "T3_POTION_SLOWFIELD",
    "display_name": "Minor Sticky Potion",
    "scope": "awareness_only"
  },
  {
    "family": "Calming Potion",
    "tier": "T3",
    "base_item_id": "T3_POTION_MOB_RESET",
    "display_name": "Minor Calming Potion",
    "scope": "awareness_only"
  },
  {
    "family": "Cleansing Potion",
    "tier": "T3",
    "base_item_id": "T3_POTION_CLEANSE2",
    "display_name": "Minor Cleansing Potion",
    "scope": "awareness_only"
  },
  {
    "family": "Acid Potion",
    "tier": "T3",
    "base_item_id": "T3_POTION_ACID",
    "display_name": "Minor Acid Potion",
    "scope": "awareness_only"
  }
]
```

## T4+ Profit Candidate Potions

These are the potion item IDs future profitability specs should target first.

```json
[
  {
    "family": "Healing Potion",
    "base_item_ids": ["T4_POTION_HEAL", "T6_POTION_HEAL"]
  },
  {
    "family": "Energy Potion",
    "base_item_ids": ["T4_POTION_ENERGY", "T6_POTION_ENERGY"]
  },
  {
    "family": "Gigantify Potion",
    "base_item_ids": ["T5_POTION_REVIVE", "T7_POTION_REVIVE"]
  },
  {
    "family": "Resistance Potion",
    "base_item_ids": ["T5_POTION_STONESKIN", "T7_POTION_STONESKIN"]
  },
  {
    "family": "Sticky Potion",
    "base_item_ids": ["T5_POTION_SLOWFIELD", "T7_POTION_SLOWFIELD"]
  },
  {
    "family": "Poison Potion",
    "base_item_ids": ["T4_POTION_COOLDOWN", "T6_POTION_COOLDOWN", "T8_POTION_COOLDOWN"]
  },
  {
    "family": "Invisibility Potion",
    "base_item_ids": ["T8_POTION_CLEANSE"]
  },
  {
    "family": "Calming Potion",
    "base_item_ids": ["T5_POTION_MOB_RESET", "T7_POTION_MOB_RESET"]
  },
  {
    "family": "Cleansing Potion",
    "base_item_ids": ["T5_POTION_CLEANSE2", "T7_POTION_CLEANSE2"]
  },
  {
    "family": "Acid Potion",
    "base_item_ids": ["T5_POTION_ACID", "T7_POTION_ACID"]
  },
  {
    "family": "Berserk Potion",
    "base_item_ids": ["T4_POTION_BERSERK", "T6_POTION_BERSERK", "T8_POTION_BERSERK"]
  },
  {
    "family": "Hellfire Potion",
    "base_item_ids": ["T4_POTION_LAVA", "T6_POTION_LAVA", "T8_POTION_LAVA"]
  },
  {
    "family": "Gathering Potion",
    "base_item_ids": ["T4_POTION_GATHER", "T6_POTION_GATHER", "T8_POTION_GATHER"]
  },
  {
    "family": "Tornado in a Bottle",
    "base_item_ids": ["T4_POTION_TORNADO", "T6_POTION_TORNADO", "T8_POTION_TORNADO"]
  }
]
```

## Non-Tradable Potion-Labeled Items

These are cataloged for awareness but should not be scanned for market
profitability unless a future spec confirms they are relevant.

```json
[
  "T3_FOCUSPOTION_NONTRADABLE",
  "T4_FOCUSPOTION_NONTRADABLE",
  "T5_FOCUSPOTION_NONTRADABLE",
  "T6_FOCUSPOTION_NONTRADABLE",
  "T8_FOCUSPOTION_NONTRADABLE",
  "UNIQUE_FOCUSPOTION_ADC_NONTRADABLE_01"
]
```

## Herb Item IDs From The Same Source

These are included because potion recipes may depend on herbs, but this file
does not assert any recipe relationship.

```json
[
  { "item_id": "T2_AGARIC", "name": "Arcane Agaric" },
  { "item_id": "T3_COMFREY", "name": "Brightleaf Comfrey" },
  { "item_id": "T4_BURDOCK", "name": "Crenellated Burdock" },
  { "item_id": "T5_TEASEL", "name": "Dragon Teasel" },
  { "item_id": "T6_FOXGLOVE", "name": "Elusive Foxglove" },
  { "item_id": "T7_MULLEIN", "name": "Firetouched Mullein" },
  { "item_id": "T8_YARROW", "name": "Ghoul Yarrow" }
]
```

## Pending Verified Data

Potion ingredients and quantities must come from a verified ingredient source,
expected as `ingredients-for-each-potion.md`.
