<!--
Sync Impact Report
- Version change: template -> 1.0.0
- Modified principles: all core principles defined from the template placeholders
- Added sections: MVP Scope; Delivery & Quality Gates
- Removed sections: none
- Templates requiring updates:
  - updated .specify/templates/plan-template.md
  - updated .specify/templates/spec-template.md
  - updated .specify/templates/tasks-template.md
- Deferred items: none
-->
# AlbionPotionScanner Constitution

## Core Principles

### I. Potion-Only Scope
AlbionPotionScanner MUST focus on potion profitability analysis only. Food, bags,
weapons, armor, and other item classes remain out of scope unless a new
specification explicitly expands the product. A narrow scope keeps the MVP
cohesive and prevents unrelated calculation paths from entering the codebase.

### II. Albion Online Data Project as Single Source of Truth
All market prices and price-derived values MUST come from the Albion Online Data
Project. The application MUST NOT hardcode prices or business assumptions about
live market values. External market access MUST be isolated behind dedicated
services so pricing behavior can be mocked, replaced, and tested independently.

### III. Layered Architecture
The codebase MUST separate the API client, price service, recipe service, craft
calculator, scanner, and user interface into independent layers. Business logic
MUST not depend on the UI. Each layer MUST own a single responsibility and
communicate through explicit data structures or service interfaces.

### IV. Testable Business Rules
All calculation rules MUST be deterministic and covered by tests. External API
calls MUST be mockable, and calculation logic MUST be written so it can be
validated without live network access. New pricing or formula changes require
tests that prove the expected behavior before release.

### V. Future Extensibility
The architecture MUST allow future support for food, bags, weapons, and armor
without changing the calculation engine. New item categories MUST be introduced
through isolated adapters or configuration, not by rewriting profit or ROI
logic. This keeps the calculator stable while the catalog grows.

### VI. Efficient Data Access
The application MUST avoid duplicated API requests and MUST prefer batching and
caching when those mechanisms reduce redundant market lookups. Performance
improvements MUST not reduce correctness or transparency. Any cache MUST be
bounded and MUST not alter the underlying business rules.

### VII. Python Quality Standards
Implementation MUST use Python type hints, follow PEP 8, and use descriptive
names. Functions MUST stay focused on a single responsibility. Code that spans
layers or handles domain rules MUST remain small enough to review and test in
isolation.

### VIII. MVP Scope Discipline
The initial release MUST include only the potion profitability scanner and the
calculations required to support it: profit, ROI, Material Return Rate,
crafting station fee, and marketplace tax. Any capability outside this MVP
scope requires a new specification and constitutional review before
implementation begins.

### IX. Transparent Results
Every calculated result MUST expose the input values and derived values used in
the calculation. At minimum, results MUST include item name, sell price,
ingredient cost, crafting fee, marketplace tax, Material Return Rate, total
cost, profit, and ROI. The UI MUST present this structured data without hiding
or reinterpreting the calculation.

## MVP Scope

The first deliverable is a potion profitability scanner powered by live Albion
market data. The product MUST remain focused on a narrow, usable workflow:
fetch prices, calculate crafting economics, and display the result set clearly.
Features outside this scope require explicit approval through a new
specification.

- Supported items: potions only.
- Required outputs: profit, ROI, Material Return Rate, crafting station fee,
  and marketplace tax.
- Required data source: Albion Online Data Project.
- Disallowed in the MVP: food, bags, weapons, armor, and non-market-derived
  price assumptions.

## Delivery & Quality Gates

All feature work MUST preserve the layered architecture and the single source of
truth. Calculators and services MUST have unit tests that cover the expected
inputs, outputs, and error cases. Any work that changes calculation behavior,
market data access, or the result schema MUST include a focused validation plan
before merge.

- Business rules MUST be implemented outside the UI.
- External integrations MUST remain mockable.
- Result payloads MUST remain structured and transparent.
- New item categories MUST be proposed through a new specification.

## Governance

This constitution supersedes all other project guidance when rules conflict.
Amendments require a documented rationale, a semantic version bump, and
synchronized updates to dependent templates or guidance that rely on the changed
rules.

Versioning policy:

- MAJOR: backward-incompatible governance changes, principle removals, or
  principle redefinitions.
- MINOR: new principles or materially expanded guidance.
- PATCH: clarifications, wording fixes, and non-semantic refinements.

Compliance review expectations:

- Every spec, plan, and task set MUST include a constitution check.
- Any explicit violation MUST be called out and justified before implementation.
- Runtime guidance MUST not contradict the constitution.
- The current ratification date is the original adoption date for this
  constitution.

**Version**: 1.0.0 | **Ratified**: 2026-07-02 | **Last Amended**: 2026-07-02
