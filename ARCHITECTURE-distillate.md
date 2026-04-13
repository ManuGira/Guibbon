---
type: bmad-distillate
sources:
  - ARCHITECTURE.md
  - project-knowledge.md
downstream_consumer: general
created: 2026-04-13
token_estimate: 3500
parts: 1
---

# Guibbon2 — Distilled Architecture & Implementation Reference

## What Is Guibbon

- Python GUI package wrapping Tkinter for interactive scientific image parameter exploration
- Users define parameters via descriptors; framework generates widgets (sliders, radio buttons, overlays) automatically
- Three usage patterns: (1) simple set_image/wait blocking display, (2) interactive controller (parameters only), (3) interactive image viewer (parameters + image canvas with overlays)

## Five Locked Design Principles (Non-Negotiable)

- **GetPath + Tracked Values:** Field values wrapped in tracked subclasses inheriting from base types (TrackedInt, TrackedStr, etc.); carry `_parent` and `_field_name` for path reconstruction; `GetPath(params.field)` → `"field.path"` (refactor-safe); descriptor metadata on CLASS (`__guibbon_descriptors__`), current values on INSTANCES
- **Modified Descriptors Pattern:** Callback signature `def on_change(self, params: Params, modified_descriptors: list[str])` where modified_descriptors is list of `"field_name.callback_type"` strings (e.g., `["size.on_drag", "point1.on_release"]`); each descriptor has `triggered_callbacks: list[str]`; app collects all, builds list, clears for next cycle
- **Params-Centric:** Single `@guibbon.params` dataclass instance is single source of truth; all widgets read/write to it; user callbacks have full access via `self.params`
- **Component Independence:** ImageViewer, Controller, App orchestrator are decoupled; communicate only via params + need_update flag; can be used standalone or composed
- **Package Structure & Import:** Package named `guibbon`; `@guibbon.params` works via Python's package namespace; src layout `src/guibbon/`; tests at root `tests/`; build backend hatchling

## Rejected Approaches (Don't Revisit)

- **Property-based params** (params.size → descriptor.get_value()): Broke IDE autocompletion for nested fields
- **Trigger IDs** (magic numbers 1001, 1002): Unclear semantics, didn't scale to multiple callbacks per descriptor
- **_Guibbon class** as fake namespace: Replaced by proper Python package import

## @guibbon.params Decorator Mechanics

**What decorator generates:**
- Applies `@dataclass` to class with tracked values replacing descriptor defaults
- Extracts descriptor metadata before `@dataclass` processes; stores on class via `__guibbon_descriptors__`
- Wraps `__init__` to wrap all field values in tracked subclasses; recursively wires nested `@guibbon.params` instances
- Each tracked value carries `_parent` and `_field_name` attributes for `GetPath()` reconstruction

**Example structure:**
```python
@guibbon.params
class Params:
    sigma: float = SliderDescriptor(values=[0.1, 0.5, 1.0], default=1.0)
    resolution: Resolution = Resolution()  # Nested @guibbon.params

# Results in:
# - Instance attrs: sigma=TrackedFloat(1.0), resolution=Resolution(...) with nested tracked values
# - Class attr: __guibbon_descriptors__ = {'sigma': SliderDescriptor(...), 'resolution': {...}}
# - IDE sees: real types (float, Resolution); autocompletion works for params.resolution.width
# - Runtime: TrackedFloat IS a float; params.sigma + 5 works
```

**Key insight:** Tracked values inherit from base types; they ARE their types, not wrappers.

## Core Components & Their Contracts

### ImageViewer
- Displays images with pan, zoom, interactive overlays
- Public methods: `set_image(img: np.ndarray)`, `add_descriptor(descriptor)`, `build(parent: tk.Frame)`
- Property: `need_update` (cascades from overlays)
- Supports: `InteractivePointDescriptor`, `InteractivePolygonDescriptor`, `InteractiveRectangleDescriptor`
- Ignores: Control descriptors (sliders, radio buttons)

### Controller
- Displays parameter controls (sliders, buttons, options)
- Public methods: `add_descriptor(descriptor)`, `build(parent: tk.Frame)`
- Property: `need_update`
- Supports: `SliderDescriptor`, `RadioDescriptor`, `ButtonDescriptor`, any `BuildableDescriptor` with `widget_class` set
- Ignores: Interactive overlays

### App Orchestrator
- Maintains params dataclass instance; tracks `need_update` state (cascading property)
- Public methods: `add_component(component)`, `is_running()`, `wait(timeout_ms)`, property `need_update`
- Coordinates component widget creation; detects when params change → sets need_update

### BuildableWidget Protocol
- Any widget must implement: `build(self, parent: tk.Frame) → None` (populates parent frame)
- Zero framework coupling; user writes plain Tkinter
- User creates `MyWidget(BuildableWidget)` with `build()` method; framework calls it at startup
- Widget manages its own Tkinter objects; modifies parent params via callback references

## Descriptor System

### Base Descriptor (Metadata Storage)
- Stores: name, default value, visibility (isVisible bool), triggered_callbacks list
- Generates trigger IDs; creates widget instances via factory method
- Validates descriptor/callback coherence with callback signature

### Descriptor Lifecycle
1. User defines params with descriptor defaults
2. Decorator extracts descriptors; applies @dataclass; wraps values in tracked types
3. App initializes: validates coherence; creates components; initializes triggered_callbacks tracking
4. On params change: widget calls `descriptor.on_widget_change(trigger_type="drag"|"release"|"click")`
5. Descriptor appends to triggered_callbacks; sets `app.need_update = True`
6. Main loop collects triggered_callbacks from all descriptors; builds `modified_descriptors` list (["size.on_drag", "resolution.width.on_release"])
7. Clears all triggered_callbacks for next cycle
8. Calls `on_change(params, modified_descriptors)`

### Modified Descriptors Pattern (Callback Tracking)
- Problem: Multiple overlays + multiple callbacks per descriptor; how to know what triggered?
- Solution: Track which descriptor callbacks fired; return as `"descriptor_name.callback_type"` strings
- User checks: `if "size.on_release" in modified_descriptors:` or `if any("on_drag" in md for md in modified_descriptors):`
- Benefits: Clear semantics (exactly which descriptor + callback), scalable, debuggable, refactor-safe via GetPath

## Data Flow & State Management

### Single Source of Truth (Params Instance)
- Instance attributes (current values): sigma=TrackedFloat(1.0), resolution=Resolution(...) with nested tracked values
- Class attributes (metadata): `__guibbon_descriptors__ = {'sigma': SliderDescriptor(...), 'resolution': {...}}`
- Key: Tracked values ARE real primitives (inherit from int, str, float); no unwrapping needed
- Nested structures work seamlessly: params.resolution.width is tracked int with IDE support

### need_update Cascading Property
- Aggregates: `App.need_update = OR(ImageViewer.need_update, Controller.need_update)`
- ImageViewer.need_update cascades from overlays: `OR(PointOverlay1, PointOverlay2, PolygonOverlay)`
- Cascades automatically; no manual state propagation needed

### Event Flow with Modified Descriptors
1. User interacts with widget → slider.on_drag_callback(value)
2. Descriptor appends to triggered_callbacks; sets app.need_update = True
3. Main loop detects need_update
4. Collects all triggered_callbacks from each descriptor across app
5. Builds modified_descriptors list: ["size.on_drag", "resolution.width.on_release"]
6. Clears all triggered_callbacks for next cycle
7. Calls on_change(params, modified_descriptors)
8. Dynamic visibility inside callback: check modified_descriptors to update descriptor.isVisible

## Usage Patterns & Examples

### Pattern 1: Simple set_image/wait (Blocking Display)
- Like OpenCV's `imshow`/`waitKey` or matplotlib's `show`
- App blocks until user closes window
- Use case: quick visualization, debugging, one-off display
```python
import cv2, guibbon
img = cv2.imread("path/to/image.png")
result = process_image(img, 10)
app = guibbon.ImageViewer()
app.set_image(result)
app.wait(0)  # 0 = indefinite
```

### Pattern 2: Interactive Controller (Parameters Only)
- Reactive loop; changing parameters triggers computation
- Result is any data structure (not necessarily image); user displays
- Use case: data processing, interactive analysis, parameter tuning
```python
class MyDataApp(ControllerAppBase):
    @guibbon.params
    class Params:
        offset: int = SliderDescriptor(range(0, 100), default=0)
        # ...
    
    def on_change(self, params, modified_descriptors):
        return process_data(data, params.offset)

app = MyDataApp(refresh_rate=10)
app.run()
```

### Pattern 3: Interactive Image Viewer (Full App)
- Parameter controls + image canvas + interactive overlays
- Combines controller + image viewer components
- Use case: interactive image filtering, scientific exploration
```python
class MyFilterApp(InteractiveImageAppBase):
    @guibbon.params
    class Params:
        size: int = SliderDescriptor(range(1, 11), default=5)
        pos: tuple = InteractivePointDescriptor(name="point1", default=(256, 256))
    
    def on_change(self, params, modified_descriptors):
        if any("on_drag" in md for md in modified_descriptors):
            # Preview mode during drag
            return compute_preview(params)
        return compute_full(params)

app = MyFilterApp(refresh_rate=10)
app.run()
```

**Pattern mechanics:**
- Descriptors placed in params automatically route to correct component (Controller handles SliderDescriptor; ImageViewer handles InteractivePointDescriptor)
- Nested params work: slider in parent → creates field in nested class
- Modified descriptors pattern enables efficient on_drag vs on_release handling

## Extension Points (4 Customization Levels)

- **Level 1:** Use provided descriptors (SliderDescriptor, RadioDescriptor, etc.)
- **Level 2:** Write custom descriptor + widget: `class MyDescriptor(BuildableDescriptor): widget_class = MyWidget`
- **Level 3:** Override base class: `class MyCustomApp(InteractiveImageAppBase): def run(): ...`
- **Level 4:** No base class: full control of App lifecycle and components

## Module Organization

```
guibbon2/
├── core/
│   ├── params.py           # @guibbon.params decorator (IMPLEMENTED)
│   ├── descriptor.py       # Base descriptor classes (PHASE 1)
│   ├── buildable.py        # BuildableWidget protocol (PHASE 1)
│   └── app.py              # App orchestrator non-GUI (PHASE 1)
├── controller/
│   ├── controller.py       # Component
│   ├── slider.py, radio.py, button.py    # Descriptors + widgets
├── image_viewer/
│   ├── image_viewer.py     # Component
│   ├── point.py, polygon.py, rectangle.py  # Descriptors
├── apps/
│   ├── simple_image_viewer.py   # Pattern 1: show/wait
│   ├── controller_app.py        # Pattern 2: ControllerAppBase
│   └── image_app.py             # Pattern 3: InteractiveImageAppBase
└── tests/  (100% coverage non-GUI)
```

## Implementation Status & Roadmap

### COMPLETED — Phase 1, Module 1: params.py
- `_make_tracked_type(base)`: Creates tracked subclasses of int, str, float, bool, list, dict
- `_wrap_value(value, parent, field_name)`: Wraps values with parent tracking
- `_track_fields(instance)`: Recursively wraps all dataclass fields
- `GetPath(obj)`: Walks parent chain to reconstruct dotted paths
- `_BaseDescriptor` base class: default, triggered_callbacks, isVisible
- `SliderDescriptor`: values range, on_drag/on_release flags
- `RadioDescriptor`: options list, on_change flag
- `_params_decorator(cls)`: Complete decorator logic
- **30 tests passing** covering tracked types, GetPath, decorator, descriptors, modified_descriptors patterns

### NOT YET STARTED — Remaining Phase 1 (modules 2-4)
- `descriptor.py`: Descriptor base with `on_widget_change()`, `get_triggered_descriptors()`, `BuildableDescriptor` with widget_class
- `buildable.py`: BuildableWidget protocol definition
- `app.py`: App orchestrator (need_update cascading, modified_descriptors collection, main loop skeleton)

### NOT YET STARTED — Phase 2 (Week 3-4)
- Controller component assembly
- ImageViewer component (port from Guibbon1)
- App GUI integration + event loop
- need_update cascading across components

### NOT YET STARTED — Phase 3 (Week 5)
- ControllerAppBase (parameters only, no image)
- InteractiveImageAppBase (parameters + image + callbacks)
- Simple show/wait utility

### NOT YET STARTED — Phase 4 (Week 6)
- Documentation + examples
- API reference

## Testability Strategy

### What's Tested (100% Coverage Non-GUI)
- **Tracked type generation:** `_make_tracked_type()` creates subclasses; inheritance semantics; isinstance/arithmetic works
- **GetPath reconstruction:** Walks parent chain correctly for flat and nested structures
- **@guibbon.params decorator:** Extracts metadata; applies @dataclass; wraps __init__ with tracking; recursive nesting
- **Descriptor logic:** `triggered_callbacks` tracking; metadata storage; visibility
- **Modified descriptors collection:** App collects triggered_callbacks; builds list; clears for next cycle
- **Callback injection:** Receives params + modified_descriptors; type coherence
- **Dynamic visibility:** Callback can check modified_descriptors and update descriptor.isVisible

### Test Files
- `test_params.py`: 30 passing tests
- `test_descriptors.py` (planned): Metadata, triggered_callbacks, visibility
- `test_app_orchestration.py` (planned): need_update cascading, descriptor collection

### What's NOT Tested (Acceptable)
- Tkinter widget rendering (flaky)
- Mouse events on canvas (flaky)
- Image display pixel-perfect rendering (flaky)
- These validated via manual integration tests + examples

## Key Decisions Table

| Question | Decision | Rationale |
|----------|----------|-----------|
| Params field access? | GetPath + Tracked Values | IDE autocompletion + refactor-safe paths |
| Single source of truth? | Params dataclass instance | Type-safe, prevents state duplication |
| Callback tracking? | Modified descriptors (["field.callback"]) | Clear semantics, scalable, refactor-safe |
| Custom widgets? | Protocol + optional widget class | User writes plain Tkinter; zero coupling |
| Framework? | Tkinter + pluggable design | Simplicity + future PySide6 flexibility |
| Preview mode? | on_change + on_change_preview | User chooses granularity |

## Development Commands

```bash
uv sync                                    # Install dependencies
uv run python -m pytest tests/ -v          # Run all tests
uv run python -m guibbon.examples.demo_params  # Run demo
```

## Reference Files

- `ARCHITECTURE.md` — comprehensive design blueprint
- `project-knowledge.md` — status tracking + locked decisions
- `src/guibbon/core/params.py` — production params.py
- `tests/test_params.py` — 30 passing tests
- `examples/demo_params.py` — working demo

## Open Questions for Implementation

- Error handling: What if user's on_change() raises exception?
- Visibility toggle speed: How quickly does widget hide when descriptor.isVisible changes?
- Image input pattern: Multiple images or single?
- Type enforcement: How strict should type coherence be between descriptor and field?
- State persistence: Should app support save/load of params state?
