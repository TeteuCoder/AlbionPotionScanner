# Tasks: Player Mastery Experience

**Input**: Design documents from `specs/001-player-mastery/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project layout: `src/` and `tests/` are at the repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initial verification of project state and directory layout

- [x] T001 Verify project structure and .gitignore settings per implementation plan

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model class that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Implement PlayerMastery frozen data class in src/domain/models.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Viewing Mastery Levels (Priority: P1) 🎯 MVP

**Goal**: Display a horizontal mastery bar near the top of the dashboard containing every supported potion.

**Independent Test**: Delete `data/player-mastery.json` if it exists. Load the dashboard and verify that every supported potion appears in the mastery bar, displaying its official icon, level `0`, and a progress bar at `0%`.

### Tests for User Story 1
- [x] T003 [P] [US1] Create unit tests for PlayerMastery model validation in tests/test_mastery_service.py

### Implementation for User Story 1
- [x] T004 [US1] Load default level-0 mastery configuration for all potions in src/app.py
- [x] T005 [US1] Render horizontal mastery card grid using dynamic render URLs and browser-side fallback placeholders in src/app.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Editing Potion Mastery (Priority: P2)

**Goal**: Allow players to select a potion and adjust its mastery level.

**Independent Test**: Open the management expander panel, select "Healing Potion", drag the slider to 80, and verify the mastery card immediately updates to show level 80/100 and 80% progress.

### Implementation for User Story 2
- [x] T006 [US2] Implement the mastery management expander dropdown and slider controls in src/app.py
- [x] T007 [US2] Add constraint validation and clamping logic to clamp user input to 0-100 in src/app.py

**Checkpoint**: At this point, User Stories 1 and 2 should work together.

---

## Phase 5: User Story 3 - Persistence of Mastery Levels (Priority: P3)

**Goal**: Persist player mastery levels locally so they survive application restarts.

**Independent Test**: Change a potion's mastery level to 80, restart the application, and verify that the level loads back as 80.

### Tests for User Story 3
- [x] T008 [P] [US3] Write unit tests for MasteryService JSON loading and saving logic in tests/test_mastery_service.py

### Implementation for User Story 3
- [x] T009 [P] [US3] Create MasteryService for loading and saving JSON data in src/services/mastery_service.py
- [x] T010 [US3] Integrate MasteryService into app.py startup and update callbacks in src/app.py

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T011 [P] Optimize visual CSS layout of the horizontal card grid in src/app.py
- [x] T012 Run quickstart.md validation scenarios to verify end-to-end functionality
- [x] T013 Run pytest to verify all unit tests pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - User stories can then proceed sequentially in priority order (P1 → P2 → P3).
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories.
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 but should be independently testable.
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1/US2 but should be independently testable.

### Within Each User Story

- Models/Services before UI integration.
- Story complete before moving to next priority.

### Parallel Opportunities

- T003 and T008 can be written in parallel.
- Service implementation in T009 can be done in parallel with UI setup.

---

## Parallel Example: User Story 3

```bash
# Launch test creation and service implementation together
Task: "Write unit tests for MasteryService JSON loading and saving logic in tests/test_mastery_service.py"
Task: "Create MasteryService for loading and saving JSON data in src/services/mastery_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (T002 - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently in browser (level 0 state)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Interactive!)
4. Add User Story 3 → Test independently → Deploy/Demo (Persistent!)
5. Each story adds value without breaking previous stories.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
