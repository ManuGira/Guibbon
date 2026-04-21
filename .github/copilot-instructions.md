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

```bash
uv sync                                    # Install dependencies
uv run python -m pytest tests/ -v          # Run all tests
uv run python -m guibbon.examples.demo_params  # Run demo
uv run ci.ps1                              # Run all CI checks (tests, ruff, ty)
```

## Quality Gate: CI Validation

**After coding work completes**, invoke the **CI Validator** agent to verify all checks pass:

```bash
uv run ci.ps1
```

This runs:
1. **Tests** — `pytest` with coverage
2. **Linting** — `ruff check --fix`
3. **Type checking** — `ty check .`

**Benefits**:
- Catch issues **before** committing
- All checks pass **before** PR creation
- Consistent with GitHub Actions CI environment

**When it fails**: Type `@CI Validator` in chat to invoke the agent for analysis and fix guidance. It's auto-discovered from `.github/agents/`.

## Questions?

- Decisions are **locked** — read project-knowledge.md first to understand why
- Implementation details are in **ARCHITECTURE.md** — read before coding
- Code archaeology: Check `src/guibbon/core/params.py` for reference implementations
