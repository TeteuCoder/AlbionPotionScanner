# Quickstart Validation Guide: Player Mastery Experience

This guide details how to verify the Player Mastery Experience feature end-to-end.

## Prerequisites
* Python 3.13 virtual environment activated.
* Streamlit and other dependencies installed.
* Streamlit server running locally.

---

## Setup & Launch
1. Ensure the recipe repository exists at `data/potion-recipes.json`.
2. Start the Streamlit application:
   ```bash
   .venv\Scripts\python -m streamlit run src/app.py
   ```
3. Open the application in your browser at [http://localhost:8501](http://localhost:8501).

---

## Validation Scenarios

### Scenario 1: Initial Launch (Empty State)
1. Delete or rename `data/player-mastery.json` if it exists.
2. Load the dashboard in the browser.
3. **Verify**:
   * A horizontal Mastery Bar is visible near the top of the dashboard.
   * Every supported potion in the database is listed.
   * Potion icons load correctly from the Albion Online Render Service (or show the fallback placeholder symbol `🧪` if offline).
   * All potions display a mastery level of `0` and progress at `0%`.
   * Check `data/player-mastery.json` was automatically created with all potions set to `0`.

### Scenario 2: Modifying Mastery Levels
1. Locate the **"Gerenciar Especializações"** expander panel below the mastery bar.
2. Select **"Healing Potion (T4_POTION_HEAL)"** from the selectbox.
3. Drag the slider to set its mastery level to `80`.
4. Click outside or wait for it to apply.
5. **Verify**:
   * The entry for **Healing Potion** in the mastery bar immediately updates to display level `80` and the progress bar/ring is filled to `80%`.
   * All other potion levels remain unchanged.
   * Verify that existing profitability calculations in the KPI cards and results table remain 100% identical.

### Scenario 3: Persistence Validation
1. After setting the level to `80` in Scenario 2, refresh the browser window or restart the Streamlit server.
2. **Verify**:
   * The dashboard loads.
   * The **Healing Potion** entry still displays level `80` and progress at `80%`.
   * Open `data/player-mastery.json` and verify it contains `"T4_POTION_HEAL": 80`.

### Scenario 4: Automated Verification
1. Run the test suite:
   ```bash
   .venv\Scripts\pytest
   ```
2. **Verify**:
   * All 47 existing tests (and any new domain validation tests) pass successfully.
