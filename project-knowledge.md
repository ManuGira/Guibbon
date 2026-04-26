# Guibbon — Project Knowledge

## What Is Guibbon

Guibbon is a Python GUI package wrapping Tkinter for interactive scientific image parameter exploration. Users define parameters via descriptors, and the framework generates widgets (sliders, radio buttons, interactive overlays) automatically.

**Three usage patterns:**
1. **Simple show/wait** — blocking image display (like OpenCV `imshow`/`waitKey`)
2. **Interactive controller** — parameter panel only, no image viewer
3. **Interactive image viewer** — parameter panel + image canvas with drag/click overlays

## Locked-In Design Decisions

These decisions are final. Do not revisit or propose alternatives.

### 1. GetPath + Tracked Values (`params.py` — IMPLEMENTED)
- `@guibbon.params` applies `@dataclass` under the hood
- Field values are wrapped in tracked subclasses (TrackedInt, TrackedStr, etc.) that inherit from their base types
- Tracked values carry `_parent` and `_field_name` for path reconstruction
- `GetPath(params.field)` walks the parent chain → `"field.path"` (refactor-safe)
- Descriptor metadata lives on CLASS (`__guibbon_descriptors__`), current values on INSTANCES
- IDE autocompletion works because tracked values ARE their base types

### 2. Modified Descriptors Pattern (callbacks)
- User callback signature: `def on_change(self, params: Params, modified_descriptors: list[str])`
- `modified_descriptors` is a list of `"field_name.callback_type"` strings (e.g., `["size.on_drag", "point1.on_release"]`)
- Each descriptor has `triggered_callbacks: list[str]` that tracks what fired
- App orchestrator collects all triggered callbacks, builds the list, clears for next cycle
- Pattern matching: `if "size.on_release" in modified_descriptors:` or `if any("on_drag" in md for md in modified_descriptors):`

### 3. Package structure: `import guibbon`
- The package is named `guibbon` — `@guibbon.params` works via Python's package namespace (no fake class needed)
- Src layout: `src/guibbon/` with tests at root `tests/`
- Build backend: hatchling

### 4. Architecture principles
- Params-centric: single `@guibbon.params` dataclass instance is the single source of truth
- Component independence: ImageViewer, Controller, App orchestrator are decoupled
- `BuildableWidget` protocol for zero-framework-coupling widget injection (framework-agnostic: ANY framework supported)
- Cascading `need_update` property aggregates children's flags
- Tkinter now, pluggable for nicegui/PySide6/other frameworks later (same protocol works for all)
- 100% test coverage of non-GUI code; accept framework rendering flakiness

### 5. Callback access pattern
- User has full access to params via `self.params` (not passed as parameter)
- Type safety depends on the descriptor system, not name matching

## Rejected Approaches (Don't Revisit)

- **Property-based params** (params.size → descriptor.get_value()): Broke IDE autocompletion for nested fields
- **Trigger IDs** (magic numbers like 1001, 1002): Unclear semantics, didn't scale to multiple callbacks per descriptor
- **_Guibbon class** as fake namespace: Replaced by proper Python package import

## Implementation Status

### COMPLETED — Phase 1, Module 1: `params.py`
- `_make_tracked_type(base)`: Creates tracked subclasses of int, str, float, bool, list, dict
- `_wrap_value(value, parent, field_name)`: Wraps values with parent tracking
- `_track_fields(instance)`: Recursively wraps all dataclass fields
- `GetPath(obj)`: Walks parent chain to reconstruct dotted paths
- `_params_decorator(cls)`: Extracts descriptors → applies @dataclass → wraps __init__ with tracking
- **30 tests passing** covering tracked types, GetPath, decorator patterns

### COMPLETED — Phase 1, Module 2: `descriptor.py` + `controller/`
- `Descriptor` (ABC): Base with default, triggered_callbacks, is_visible, `on_widget_change()`, `get_triggered_descriptors()`
- `BuildableDescriptor`: Descriptor with optional widget_class for custom widgets
- `SliderDescriptor` (in `controller/`): values range, on_drag/on_release flags
- `RadioDescriptor` (in `controller/`): options list, on_change flag
- **59 tests passing** in `test_descriptor.py` covering descriptor system, modified_descriptors patterns
- New example: `examples/demo_descriptors.py` demonstrating descriptor API and usage

### COMPLETED — Phase 1, Module 3: `buildable.py`
- `BuildableWidget` protocol: `@runtime_checkable` structural Protocol, framework-agnostic, zero imports
- Single `build(self, parent: Any)` method; supports Tkinter, nicegui, PySide6
- **24 tests passing** in `test_buildable.py` covering protocol structure, framework-agnosticism, structural satisfaction
- **Total Phase 1 tests: 113 passing** (30 + 59 + 24)

### NOT YET STARTED — Remaining Phase 1
- `app.py`: App orchestrator (need_update cascading, modified_descriptors collection, main loop skeleton)

### NOT YET STARTED — Phases 2-4
- Phase 2: Controller component, ImageViewer component (port from Guibbon1), App GUI integration
- Phase 3: Base classes (ControllerAppBase, InteractiveImageAppBase, simple show/wait)
- Phase 4: Documentation, examples, API reference

## Key Reference Files

- `ARCHITECTURE.md` — comprehensive design blueprint (all sections updated to reflect current decisions)
- `.github/instructions/core-implementation.instructions.md` — Phase 1 core implementation patterns and rules
- `src/guibbon/core/params.py` — `@guibbon.params` decorator (Module 1, COMPLETED)
- `src/guibbon/core/descriptor.py` — Descriptor base classes (Module 2, COMPLETED)
- `src/guibbon/controller/slider.py` — SliderDescriptor implementation (Module 2, COMPLETED)
- `src/guibbon/controller/radio.py` — RadioDescriptor implementation (Module 2, COMPLETED)
- `src/guibbon/core/buildable.py` — BuildableWidget protocol (Module 3, COMPLETED)
- `tests/test_params.py` — 30 tests for params.py (Module 1)
- `tests/test_descriptor.py` — 59 tests for descriptor.py + controller (Module 2)
- `tests/test_buildable.py` — 24 tests for buildable.py (Module 3)
- `examples/demo_params.py` — params decorator demo (`uv run python -m guibbon.examples.demo_params`)
- `examples/demo_descriptors.py` — descriptor system demo (`uv run python -m guibbon.examples.demo_descriptors`)

## Development Commands

```bash
uv sync                                    # Install dependencies
uv run python -m pytest tests/ -v          # Run all tests
uv run python -m guibbon.examples.demo_params  # Run demo
```
