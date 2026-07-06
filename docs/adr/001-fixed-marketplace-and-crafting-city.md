# ADR-001: Fixed Marketplace and Crafting City for V1

## Status

Accepted

## Date

2026-07-06

## Context

The long-term vision of AlbionPotionScanner includes supporting multiple cities
for ingredient purchasing, crafting, and selling. Supporting multiple cities
introduces optimization problems and significantly increases the complexity of
the first release.

The goal of V1 is to validate the calculation engine, not the logistics engine.

## Decision

Version 1 assumes that every operation occurs exclusively in Brecilien.

This includes:

- Ingredient prices are fetched from the Brecilien marketplace.
- Crafting is assumed to occur in Brecilien.
- The crafted potion is assumed to be sold in Brecilien.

The application MUST NOT allow selecting another city during V1. The city MUST
be treated as project-wide configuration rather than user input.

## Scope

V1 answers only the following question:

"Considering that every step (buying ingredients, crafting and selling) happens
in Brecilien, which potion is the most profitable to craft right now?"

## Out of Scope

The following features are explicitly excluded from Version 1:

- Multiple crafting cities.
- Different buying/selling cities.
- Route optimization.
- Arbitrage between cities.
- Transportation cost.
- Best city recommendation.
- Focus optimization.
- Profit per Focus.
- Automatic Return Rate calculation based on city bonuses.

## Consequences

- Future specifications, plans, tasks, and implementations MUST assume
  Brecilien for all V1 market and crafting calculations.
- Price queries for V1 MUST request Brecilien data only.
- UI work for V1 MUST NOT include city selectors or city recommendation flows.
- Multi-city support requires a future ADR or specification amendment.
