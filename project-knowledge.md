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

### COMPLETED — Phase 1, Module 4: `app.py`
- `App` class: Params orchestrator, component registration, need_update cascading, modified_descriptors collection
- `HasNeedUpdate` protocol: Component contract for need_update property
- Methods: `add_component()`, `is_running()`, `wait()`, `collect_modified_descriptors()`, `clear_modified_descriptors()`, `stop()`
- Property: `need_update` cascades from all registered components (OR logic)
- **27 tests passing** in `test_app.py` covering initialization, component lifecycle, need_update cascading, callback collection
- **Phase 1 COMPLETE: 140 total tests passing** (30 + 59 + 24 + 27)

### COMPLETED — Phase 2a: `controller/controller.py`
- `Controller` component: discovers buildable descriptors from params, including nested params trees
- Routes supported control descriptors (`SliderDescriptor`, `RadioDescriptor`, custom `BuildableDescriptor.widget_class`) to control-side widgets
- Tracks local `need_update` state; widget events update params and append descriptor callbacks
- Default Tk widget adapters for slider and radio descriptors; custom widget classes receive controller context
- `App.collect_modified_descriptors()` and `clear_modified_descriptors()` now recurse into nested params for consistency with controller routing
- **25 tests passing** in `test_controller.py`; repo total now **167 passing tests**

### COMPLETED — Phase 2b: `image_viewer/image_viewer.py` + demo app
- `ImageViewer` component: pan/zoom canvas (720×720 default), cv2.warpPerspective for transform, Pillow only as numpy→Tk bridge
- `_MousePan` state machine for drag; pure transform helpers `_identity()`, `_translation()`, `_scale()`, `_apply()`, `_inv()`
- Toolbar: fit/fill/100%/home buttons, zoom entry, pan/zoom checkbox
- `ImageViewer.wait(timeout_ms=0)` for Pattern 1 standalone blocking display
- **71 tests passing** in `test_image_viewer.py`; repo total now **238 passing tests**
- `examples/demo_app.py` wires params → Controller → ImageViewer with refresh loop

### COMPLETED — Controller UI polish
- Dark card design replaced by **light theme** (configurable via `controller/_theme.py`)
- Theme constants: `BG_PANEL`, `BG_CARD`, `BG_TROUGH`, `FG` — single file to change the whole panel look
- `_TkSliderWidget` and `_TkRadioWidget` each extracted to their own files (`tk_slider_widget.py`, `tk_radio_widget.py`)
- Circular imports avoided via `TYPE_CHECKING` guard for `Controller` import in widget files
- Controller panel default width: **360px** (was 200px)
- Radio button GC bug fixed: `tk.StringVar` stored as instance attribute
- `Controller.build(parent, width=360, expand=False)`: `expand=True` skips `pack_propagate(False)` and lets card children determine height (required for Pattern 2 standalone window); a zero-height spacer Frame enforces the minimum width instead
- Bottom 4px spacer added after last card for symmetric border

### COMPLETED — Phase 3: `apps/` package
- `ControllerAppBase` (Pattern 2): subclass + define `Params` + implement `on_change()` + call `.run()`
- `InteractiveImageAppBase` (Pattern 3): same but `on_change()` returns BGR image
- `ImageViewer.wait(timeout_ms=0)` is Pattern 1 (already in Phase 2b)
- Both base classes exported from `guibbon` root + `guibbon.apps`
- `__all__` added to `guibbon/__init__.py`
- **37 new tests** in `test_apps.py` + **2 Tk geometry regression tests** in `test_controller.py`
- **277 total tests passing**
- Demo scripts: `examples/demo_pattern1_wait.py`, `examples/demo_pattern2_controller.py`, `examples/demo_pattern3_image_app.py`

### NOT YET STARTED — Phase 4
- Documentation, examples, API reference

## Key Reference Files

- `ARCHITECTURE.md` — comprehensive design blueprint (all sections updated to reflect current decisions)
- `.github/instructions/core-implementation.instructions.md` — Phase 1 core implementation patterns and rules
- `src/guibbon/core/params.py` — `@guibbon.params` decorator (Module 1, COMPLETED)
- `src/guibbon/core/descriptor.py` — Descriptor base classes (Module 2, COMPLETED)
- `src/guibbon/controller/slider.py` — SliderDescriptor implementation (Module 2, COMPLETED)
- `src/guibbon/controller/radio.py` — RadioDescriptor implementation (Module 2, COMPLETED)
- `src/guibbon/controller/controller.py` — Controller component assembly (Phase 2a, COMPLETED)
- `src/guibbon/controller/_theme.py` — Light-theme colour constants (`BG_PANEL`, `BG_CARD`, `BG_TROUGH`, `FG`)
- `src/guibbon/controller/tk_slider_widget.py` — Tkinter slider widget adapter
- `src/guibbon/controller/tk_radio_widget.py` — Tkinter radio widget adapter
- `src/guibbon/core/buildable.py` — BuildableWidget protocol (Module 3, COMPLETED)
- `src/guibbon/core/app.py` — App orchestrator (Module 4, COMPLETED)
- `src/guibbon/image_viewer/image_viewer.py` — ImageViewer component incl. `wait()` (Phase 2b, COMPLETED)
- `src/guibbon/apps/__init__.py` — apps package exports
- `src/guibbon/apps/controller_app.py` — ControllerAppBase (Phase 3, COMPLETED)
- `src/guibbon/apps/image_app.py` — InteractiveImageAppBase (Phase 3, COMPLETED)
- `tests/test_params.py` — 30 tests for params.py (Module 1)
- `tests/test_descriptor.py` — 59 tests for descriptor.py + controller (Module 2)
- `tests/test_buildable.py` — 24 tests for buildable.py (Module 3)
- `tests/test_app.py` — 27 tests for app.py (Module 4)
- `tests/test_controller.py` — 27 tests for controller.py (Phase 2a + geometry regression)
- `tests/test_image_viewer.py` — 71 tests for image_viewer.py (Phase 2b)
- `tests/test_apps.py` — 37 tests for ControllerAppBase, InteractiveImageAppBase (Phase 3)
- `examples/demo_params.py` — params decorator demo
- `examples/demo_descriptors.py` — descriptor system demo
- `examples/demo_app.py` — low-level demo wiring params → Controller → ImageViewer
- `examples/demo_pattern1_wait.py` — Pattern 1: standalone blocking display
- `examples/demo_pattern2_controller.py` — Pattern 2: ControllerAppBase calculator
- `examples/demo_pattern3_image_app.py` — Pattern 3: InteractiveImageAppBase image filter

## Development Commands

```bash
uv sync                                 # Install dependencies
uv run pytest                           # Run all tests (277 passing)
./ci.ps1                                # Full CI: tests + ruff + ty
uv run python examples/demo_pattern2_controller.py  # Pattern 2 demo
uv run python examples/demo_pattern3_image_app.py   # Pattern 3 demo
```
