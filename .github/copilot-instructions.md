# GitHub Copilot Instructions

## Initial Context Loading

When starting a new session with GitHub Copilot in this repository:

1. **First, read** `project-knowledge.md` in the repository root
   - This file contains the high-level summary of:
     - What Guibbon is and its three usage patterns
     - All locked design decisions (do not revisit)
     - Rejected approaches (avoid going down these paths)
     - Current implementation status
     - Key reference files

2. **Then, deep dive into** `ARCHITECTURE.md` for:
   - Comprehensive design specification
   - All components and their interactions
   - Detailed usage patterns with concrete code examples (see "Usage Patterns" section)
   - Event flow and data flow diagrams
   - Implementation roadmap with exact module specs

## Purpose

Guibbon is a Python GUI package wrapping Tkinter for interactive scientific image parameter exploration. The architecture is locked in; implementation is ongoing (currently completing Phase 1).

## Key Design Principles

- **Params-centric**: Single `@guibbon.params` dataclass is the source of truth
- **GetPath + Tracked Values**: Reconstruction of dotted paths via parent chain walking
- **Modified Descriptors Pattern**: Callbacks receive list of `"field.callback_type"` strings
- **Component decoupling**: ImageViewer, Controller, App are independent
- **IDE autocompletion**: Tracked values ARE their base types (not wrappers)

## Current Development Phase

- ✅ Phase 1, Module 1 complete: `params.py` (30 tests passing)
- ⏳ Phase 1, Modules 2-4 in progress: `descriptor.py`, `buildable.py`, `app.py`
- ❌ Phase 2-4: Not started

## Commands

```powershell
uv run pytest                                  # Run all tests
uv run python -m guibbon.examples.demo_params  # Run demo
./ci.ps1                                       # Run all CI checks (tests, ruff, ty)
```

## Quality Gate: CI Validation Workflow

**Before committing or creating a PR**, follow this workflow:

### Step 1: Run CI Validator
Invoke **[CI Validator](\.github\agents\ci-validator.agent.md)** agent to verify all checks pass locally:

```powershell
./ci.ps1
```

This sequentially runs:
1. **Tests** — `uv run pytest` with coverage
2. **Linting** — `uv run ruff check --fix src tests examples` (auto-fixes most issues)
3. **Type checking** — `uv run ty check`

### Step 2: If CI Validator Fails
Invoke **[Github Actions fixer](\.github\agents\ci-fixer.agent.md)** agent to solve specific issues:
- Test failures → test debugging guidance
- Ruff failures → formatting/import fixes
- Type check failures → annotation fixes

**Benefits of this workflow**:
- ✅ Catch issues **before** committing
- ✅ All checks pass **before** PR creation
- ✅ Consistent with GitHub Actions CI environment
- ✅ Two agents handle different phases (verify vs. fix)

## Questions?

- Decisions are **locked** — read project-knowledge.md first to understand why
- Implementation details are in **ARCHITECTURE.md** — read before coding
- Code archaeology: Check `src/guibbon/core/params.py` for reference implementations
