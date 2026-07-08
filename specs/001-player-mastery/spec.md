# Feature Specification: Player Mastery Experience

**Feature Branch**: `001-player-mastery`

**Created**: 2026-07-08

**Status**: Draft

**Input**: User description: "Introduce a player mastery component to the dashboard inspired by Albion Online's Destiny Board progression."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Viewing Mastery Levels (Priority: P1)

As a crafter, I want to see a horizontal mastery bar near the top of the dashboard showing my specialization progress for each supported potion, so that I can quickly assess my character's progression.

**Why this priority**: It is the core visual component that introduces player mastery tracking to the dashboard.
**Independent Test**: Can be verified by loading the dashboard and confirming that all supported potions from the recipe database are displayed in the bar with their respective icons, level (0-100), and a visual progress indicator.

**Acceptance Scenarios**:
1. **Given** the application starts for the first time with no saved mastery data, **When** the dashboard loads, **Then** all supported potions are shown in the mastery bar, each displaying a level of `0` and a progress indicator at `0%`.
2. **Given** a potion has a saved mastery level of `75`, **When** the dashboard loads, **Then** its entry displays level `75` and a progress indicator filled to `75%`.

---

### User Story 2 - Editing Potion Mastery (Priority: P2)

As a crafter, I want to select a potion in the mastery bar and edit its level, so that I can align the dashboard with my in-game character's specialization.

**Why this priority**: Enables user interaction, making the mastery bar dynamic and customizable.
**Independent Test**: Select a potion on the mastery bar, open the editing control, input a new level, save, and confirm that the mastery bar immediately updates to show the new value and corresponding progress.

**Acceptance Scenarios**:
1. **Given** a potion in the mastery bar, **When** I select it to edit, **Then** I am presented with an input control (e.g. popover, modal, or number input) allowing me to enter a value between `0` and `100`.
2. **Given** the edit control is active, **When** I enter a value of `105`, **Then** the value is clamped or validated to a maximum of `100`.
3. **Given** the edit control is active, **When** I enter a value of `-5`, **Then** the value is clamped or validated to a minimum of `0`.

---

### User Story 3 - Persistence of Mastery Levels (Priority: P3)

As a crafter, I want my mastery levels to persist between application sessions, so that I do not need to re-enter them every time I open the scanner.

**Why this priority**: Essential usability feature that ensures the tool remains convenient for repeated use.
**Independent Test**: Change the mastery level of one or more potions, refresh the page/restart the application, and verify that the updated levels are correctly loaded and displayed.

**Acceptance Scenarios**:
1. **Given** I edit and save a potion's mastery level, **When** the change is confirmed, **Then** the value is persisted locally.
2. **Given** persisted mastery values exist on disk, **When** the application starts, **Then** those values are loaded and used to populate the mastery bar.

---

### Edge Cases

- **Official Render Service Offline**: If the Albion Render Service is unreachable or returns a `404`/error for a potion icon, the system MUST show a generic fallback placeholder image, keeping the mastery bar entry fully visible and interactive.
- **Corrupted Persistence File**: If the local persistence file is corrupted, empty, or fails to parse, the system MUST log a warning, default all mastery levels to `0` to keep the application running, and write a fresh, valid default persistence file.

## Requirements *(mandatory)*

For AlbionPotionScanner, requirements MUST explicitly state the market data source, fixed V1 operating city, calculation inputs, derived outputs, and any scope exclusions. V1 MUST use Brecilien for ingredient purchases, crafting, and potion sales. Requirements MUST NOT allow city selection or multi-city optimization during V1. Keep the requirements deterministic and traceable to the live Albion Online Data Project.

### Functional Requirements

- **FR-001**: The system MUST display a horizontal mastery bar near the top of the dashboard page.
- **FR-002**: Every supported potion in the recipe repository MUST be represented as an entry in the mastery bar.
- **FR-003**: Each potion entry MUST display its official icon, current mastery level, and a visual progress indicator (e.g. progress bar or ring).
- **FR-004**: Potion icons MUST be loaded dynamically from the official Albion Render Service. Local storage of icons is prohibited.
- **FR-005**: If a potion icon fails to load, the system MUST display a fallback placeholder icon and maintain the entry's functionality.
- **FR-006**: Users MUST be able to select a potion in the mastery bar and update its mastery level using an interactive control.
- **FR-007**: The mastery input MUST accept only integers from `0` to `100` inclusive.
- **FR-008**: Mastery levels MUST be persisted locally using a lightweight persistence mechanism (e.g., a local JSON file `data/player-mastery.json` or local session-backed persistence).
- **FR-009**: If no local persistence file exists, all potions MUST default to a mastery level of `0`.
- **FR-010**: The player mastery component and its underlying data MUST remain completely independent from all profitability, cost, MRR, station fee, and tax calculations.
- **FR-011**: Calculations MUST produce identical results regardless of player mastery values.

### Key Entities *(include if feature involves data)*

- **PlayerMastery**: Represents the progression state of the player's specialization for a specific potion.
  - Attributes:
    - `potion_item_id` (string, unique identifier matching the recipe/item ID)
    - `mastery_level` (integer, range `0` to `100` inclusive)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the supported potions loaded from the repository are rendered in the dashboard's mastery bar.
- **SC-002**: Users can update any potion's mastery level in under 5 seconds with immediate visual update of the progress bar/ring.
- **SC-003**: Modified mastery levels persist across page reloads and application restarts.
- **SC-004**: Existing profitability calculations and values remain 100% unchanged after editing or saving mastery levels.
- **SC-005**: The pytest test suite passes with 100% success.

## Assumptions

- Market prices are sourced from the Albion Online Data Project unless the spec says otherwise.
- V1 uses Brecilien as the fixed marketplace, crafting city, and sales city.
- The operating city is project-wide configuration, not a user-selectable input.
- Multiple cities, route optimization, arbitrage, transportation cost, best-city recommendation, Focus optimization, Profit per Focus, and automatic Return Rate calculation from city bonuses are out of scope for V1.
- Any new item category outside potions requires a separate specification.
- Calculation outputs remain structured so the UI can present them without recomputing business rules.
- Potion icons are fetched from the Albion Online Render Service using standard naming conventions based on the `potion_item_id` (e.g., `https://render.albiononline.com/v1/item/{item_id}.png`).
- Storing mastery data in a simple JSON file in the project's data directory is sufficient for session-to-session persistence.
- Focus and specialization calculations (such as Focus cost reduction or efficiency bonuses) are explicitly out of scope for this feature but will consume this data in future releases.
