# Data Model: Player Mastery Experience

This document defines the data structures and domain entities introduced for tracking player progression.

## 1. Domain Entities

### `PlayerMastery` (Value Object / Entity)
Represents the specialization progress of the player for a specific potion.

#### Attributes
* `potion_item_id`: `str` (Primary identifier, e.g. `"T4_POTION_HEAL"`)
* `mastery_level`: `int` (Progression level, must satisfy `0 <= level <= 100`)

#### Validation Invariants
* `potion_item_id` cannot be empty.
* `mastery_level` must be an integer between `0` and `100` inclusive.

#### Python Class Definition (Conceptual)
```python
@dataclass(frozen=True)
class PlayerMastery:
    potion_item_id: str
    mastery_level: int

    def validate(self) -> None:
        if not self.potion_item_id:
            raise ValueError("potion_item_id cannot be empty")
        if not (0 <= self.mastery_level <= 100):
            raise ValueError("mastery_level must be between 0 and 100 inclusive")
```

---

## 2. Serialization & Persistence Schema

### JSON Persistence Format
The state is persisted to a local file (`data/player-mastery.json`) as a flat key-value dictionary to minimize storage footprint and maximize read/write performance.

```json
{
  "T4_POTION_HEAL": 15,
  "T6_POTION_HEAL": 0,
  "T4_POTION_ENERGY": 80,
  "T6_POTION_ENERGY": 40
}
```

### State Initialization & Lifecycle
1. On start:
   * Read `data/player-mastery.json`.
   * Parse keys as `potion_item_id` and values as `mastery_level`.
   * Create `PlayerMastery` instances and validate.
   * If the file is missing or invalid, default all potions from `JsonRecipeRepository` to level `0` and write a new file.
2. On update:
   * Re-validate modified level.
   * Update internal memory mapping and overwrite `data/player-mastery.json`.
