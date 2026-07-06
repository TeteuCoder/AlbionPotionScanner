# AlbionPotionScanner Constitution

This document mirrors the active project constitution for easier discovery from
the documentation tree. The canonical source remains
`.specify/memory/constitution.md`.

## Purpose

AlbionPotionScanner is a market analysis tool for Albion Online that identifies
the most profitable potions to craft in Brecilien using live market data from
the Albion Online Data Project.

## Core Rules

- The project scope is potion profitability scanning only.
- All market prices must come from the Albion Online Data Project.
- Version 1 must use Brecilien as the fixed city for ingredient purchases,
  crafting, and potion sales.
- The application must not allow city selection during Version 1.
- External integrations must be isolated behind dedicated services.
- Business logic must not depend on the user interface.
- Calculation logic must be deterministic and testable.
- External API calls must be mockable.
- Future item categories must not require changes to the calculation engine.
- Duplicated API requests should be avoided through batching or caching.
- Python code must use type hints and follow PEP 8.
- Every result must expose the values used to calculate it.

## MVP Scope

The initial version includes:

- Potion profitability scanner
- Fixed Brecilien marketplace, crafting city, and sales city
- Profit calculation
- ROI calculation
- Material Return Rate
- Crafting station fee
- Marketplace tax

Any feature outside this scope requires a new specification.

Explicitly excluded from Version 1: multiple cities, different buying and
selling cities, route optimization, arbitrage, transportation cost, best-city
recommendation, Focus optimization, Profit per Focus, and automatic Return Rate
calculation based on city bonuses.

## Governance

The full governance policy, version, ratification date, and amendment rules are
defined in `.specify/memory/constitution.md`.
