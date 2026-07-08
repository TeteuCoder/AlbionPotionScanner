# Implementation Plan: Player Mastery Experience

**Branch**: `001-player-mastery` | **Date**: 2026-07-08 | **Spec**: [specs/001-player-mastery/spec.md](file:///c:/Users/mathe/Dev/AlbionPotionScanner/specs/001-player-mastery/spec.md)

**Input**: Feature specification from `specs/001-player-mastery/spec.md`

## Summary
Introduce player mastery specialization tracking (0-100) to the dashboard. The feature is visual and data-oriented, preserving all existing profitability calculations while laying down the data models and persistence layers for future Focus calculations.

## Technical Context
* **Language/Version**: Python 3.13
* **Primary Dependencies**: Streamlit, pandas, pytest, standard library (`json`, `os`, `dataclasses`)
* **Storage**: Local JSON file at `data/player-mastery.json`
* **Testing**: pytest
* **Target Platform**: Windows / Web browser
* **Project Type**: Web application
* **Performance Goals**: Instant UI rendering (< 100ms) and updates
* **Constraints**: 
  * No modifications to existing profit/ROI formulas.
  * No Focus calculations implemented in V1.
  * No extra Python-level API calls (using HTML `onerror` browser-side fallbacks).

## Constitution Check

- Scope stays limited to potion profitability: **Pass**. The new mastery fields only represent player progression.
- All market pricing comes from the Albion Online Data Project: **Pass**. No prices are changed or hardcoded.
- V1 uses Brecilien as the fixed operating city: **Pass**. No city selection is introduced.
- V1 plans must not introduce city selection, Focus optimization, Profit per Focus, or automatic Return Rate calculation: **Pass**.
- Calculation logic remains deterministic, testable, and independent from the UI: **Pass**. All domain progression models and persistence are isolated in a separate service layer (`MasteryService`).
- Python type hints, PEP 8, and single-responsibility functions remain mandatory: **Pass**.

## Project Structure

### Documentation (this feature)
```text
specs/001-player-mastery/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Research findings
├── data-model.md        # Data models and structures
└── quickstart.md        # Validation/run guide
```

### Source Code
```text
src/
├── domain/
│   └── models.py        # [MODIFY] Add PlayerMastery model
├── services/
│   └── mastery_service.py # [NEW] Handles loading/saving of player mastery progression
└── app.py               # [MODIFY] Render mastery bar, progress, and management controls

tests/
└── test_mastery_service.py # [NEW] Unit tests for loading, saving, and validating masteries
```

**Structure Decision**: Single project layout matching the existing layered architecture.

---

## Proposed Changes

### Domain

#### [MODIFY] [models.py](file:///c:/Users/mathe/Dev/AlbionPotionScanner/src/domain/models.py)
* Add `PlayerMastery` frozen data class:
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

### Services

#### [NEW] [mastery_service.py](file:///c:/Users/mathe/Dev/AlbionPotionScanner/src/services/mastery_service.py)
* Create `MasteryService` class to handle loading/saving of mastery levels to `data/player-mastery.json`.
* Default all loaded masteries to `0` based on the potion list in `JsonRecipeRepository`.

### UI Web App

#### [MODIFY] [app.py](file:///c:/Users/mathe/Dev/AlbionPotionScanner/src/app.py)
* Instantiate `MasteryService` and load player masteries on startup.
* Render a horizontal **"Especialização (Mastery)"** bar as a card grid.
* Potion card layout: Potion Icon (Albion Render Service with browser-side SVG fallback), numerical level representation (`X/100`), and a styled progress bar (`X%`).
* Add a `st.expander` named `"⚙️ Gerenciar Especializações (Mastery)"` underneath the bar to select a potion and adjust its level with a slider.

### Tests

#### [NEW] [test_mastery_service.py](file:///c:/Users/mathe/Dev/AlbionPotionScanner/src/tests/test_mastery_service.py)
* Write tests to verify:
  * Default initialization (0 level when file is absent).
  * Valid validation invariants.
  * Correct loading from existing files.
  * Correct save updates to disk.

---

## Verification Plan

### Automated Tests
* Run pytest to verify all existing and new tests pass:
  ```bash
  .venv\Scripts\pytest
  ```

### Manual Verification
* Follow the validation scenarios described in [quickstart.md](file:///c:/Users/mathe/Dev/AlbionPotionScanner/specs/001-player-mastery/quickstart.md).
