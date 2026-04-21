# Guibbon2 Architecture Design Document

**Version:** 0.1 (Draft)  
**Date:** April 6, 2026  
**Status:** Design Complete - Ready for Implementation Planning  

---

## Table of Contents

1. [Overview](#overview)
2. [Core Design Principles](#core-design-principles)
3. [Architecture Components](#architecture-components)
4. [Parameter & Descriptor System](#parameter--descriptor-system)
5. [Data Flow & State Management](#data-flow--state-management)
6. [Extension Points & Customization](#extension-points--customization)
7. [Module Organization](#module-organization)
8. [Testability Strategy](#testability-strategy)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Overview

**Guibbon2** is a Tkinter-based GUI framework for interactive image processing parameter exploration. It enables users to:

1. **Tweak parameters visually** using sliders, buttons, overlays
2. **See results instantly** via reactive parameter binding
3. **Extend freely** by injecting custom widgets without framework knowledge
4. **Test rigorously** with 100% coverage of non-GUI code

The architecture supports three usage patterns:
- Simple set_image/wait (like OpenCV's `imshow`)
- Interactive controller (parameter panel only)
- Interactive image viewer (full parameter panel + image with overlays)

---

## Core Design Principles

### 1. **Params-Centric Architecture**
- Single source of truth: a `@guibbon.params`-decorated params instance
- All widgets read/write to this instance
- User callbacks have full access to the params object (stored in `self.params`)
- No duplicate state between widgets and app logic

### 2. **Component Independence**
- `ImageViewer`, `Controller`, and `App` are decoupled
- Each component manages its own widgets
- Components communicate only via params + need_update flag
- Can be used standalone or composed

### 3. **Descriptor-Driven UI Generation**
- Declarative: users specify parameter controls via descriptors
- Framework generates widgets automatically
- Type-safe: descriptor system enforces type coherence via properties
- Extensible: users add custom descriptors

### 4. **Framework Agnosticism**
- Widget system abstracted via `BuildableWidget` protocol
- Current: Tkinter implementation
- Future: PySide6 implementation possible without app code changes
- Plugin mechanism allows swappable UI backends

### 5. **User Responsibility Model**
- Users write business logic (`on_change()`, `on_change_preview()`)
- Framework handles boring parts (event loops, param binding, redraw)
- Users control when computations happen (via trigger flags)
- Advanced users can override `run()` for total control

---

## Architecture Components

### **1. Descriptor System**

**Purpose:** Declarative specification of parameter controls.

```
Descriptor (Base)
├── BuildableDescriptor (for interactive controls)
│   ├── SliderDescriptor
│   ├── RadioDescriptor
│   ├── ButtonDescriptor
│   ├── InteractivePointDescriptor
│   ├── InteractivePolygonDescriptor
│   └── CustomDescriptor (user-defined)
└── Metadata (name, default, ranges, triggers)
```

**Descriptor Responsibilities:**
- Store metadata (ranges, options, defaults)
- Manage visibility state (isVisible bool)
- Generate trigger IDs
- Create widget instances via factory method
- Validate descriptor coherence with callback signature

**Example:**
```python
SliderDescriptor(
    name="size",
    values=range(3, 11, 2),
    default=5,
    on_drag=True,      # Callback triggers during drag
    on_release=False   # Not on release
)
```

---

### **2. BuildableWidget Protocol**

**Purpose:** Interface for all GUI elements (built-in and user-custom).

```python
class BuildableWidget(Protocol):
    """Any widget must implement this."""
    def build(self, parent: tk.Frame) -> None:
        """Populate parent frame with widget content."""
        ...
```

**Implementation Pattern:**
- User creates `MyWidget(BuildableWidget)` with `build()` method
- Framework calls `build()` with a `tk.Frame` at startup
- Widget manages its own Tkinter objects
- Widget modifies parent params via callback references

**Benefit:** Zero framework coupling; users write plain Tkinter code.

---

### **3. ImageViewer Component**

**Responsibility:** Display images with pan, zoom, interactive overlays.

**Public Interface:**
```python
class ImageViewer:
    def set_image(self, img: np.ndarray) -> None: ...
    def add_descriptor(self, descriptor: BuildableDescriptor) -> None: ...
    def build(self, parent: tk.Frame) -> None: ...
    @property
    def need_update(self) -> bool: ...  # Cascades from overlays
```

**Supported Descriptors:**
- `InteractivePointDescriptor`
- `InteractivePolygonDescriptor`
- `InteractiveRectangleDescriptor`

**Ignored Descriptors:**
- Controls that aren't image-based (sliders, radio buttons)

---

### **4. Controller Component**

**Responsibility:** Display parameter controls (sliders, buttons, options).

**Public Interface:**
```python
class Controller:
    def add_descriptor(self, descriptor: BuildableDescriptor) -> None: ...
    def build(self, parent: tk.Frame) -> None: ...
    @property
    def need_update(self) -> bool: ...
```

**Supported Descriptors:**
- `SliderDescriptor`
- `RadioDescriptor`
- `ButtonDescriptor`
- Any `BuildableDescriptor` with `widget_class` set

**Ignored Descriptors:**
- Interactive overlays (image viewer's job)

---

### **5. App Orchestrator**

**Responsibility:** Manage components, event loop, state updates.

**Public Interface:**
```python
class App:
    def add_component(self, component) -> None: ...
    def is_running(self) -> bool: ...
    def wait(self, timeout_ms: float) -> None: ...
    @property
    def need_update(self) -> bool: ...  # Aggregates all components
```

**Responsibilities:**
- Maintain params dataclass instance
- Track `need_update` state (cascading property)
- Coordinate component widget creation
- Detect when params change → set need_update

---

### **6. @guibbon.params Decorator**

**Purpose:** Generate a standard `@dataclass` with tracked field values for IDE autocompletion + path reconstruction.

**Design: GetPath + Tracked Values**

```python
# User writes:
@guibbon.params
class Resolution:
    width:  int = SliderDescriptor(values=range(1, 1025), default=512)
    height: int = SliderDescriptor(values=range(1, 1025), default=512)

@guibbon.params
class Params:
    sigma: float = SliderDescriptor(values=[0.1, 0.5, 1.0, 2.0], default=1.0)
    mode:  str   = RadioDescriptor(options=["blur", "sharpen"], default="blur")
    resolution: Resolution = Resolution()

params = Params()
```

**What the decorator generates:**

```python
# Under the hood: real @dataclass with tracked values
@dataclass
class Params:
    sigma: float              # Type hint for IDE
    mode: str
    resolution: Resolution
    
    __guibbon_descriptors__ = {  # Class attribute: descriptor metadata
        'sigma': SliderDescriptor(...),
        'mode': RadioDescriptor(...),
        # Nested descriptors accessible via nested class
        'resolution': Resolution.__guibbon_descriptors__
    }
    
    def __init__(self, ...):
        self.sigma = TrackedFloat(1.0, _parent=self, _field_name="sigma")
        self.mode = TrackedStr("blur", _parent=self, _field_name="mode")
        self.resolution = Resolution()  # Nested gets parent chain
        # Recursively wire nested instances
        _track_fields(self.resolution, parent=self, field_name="resolution")
```

**Key Design Insights:**

1. **IDE sees real types:**
   ```python
   params.resolution.width  # IDE knows this is int
   ```

2. **Tracked values are real primitives:**
   ```python
   width_value = params.resolution.width  # Actually an int (TrackedInt inherits from int)
   print(width_value + 5)  # Works! Tracked values ARE their base types
   ```

3. **Path reconstruction via GetPath():**
   ```python
   GetPath(params.resolution.width)  # → "resolution.width"
   GetPath(params.sigma)              # → "sigma"
   ```

4. **Descriptor metadata on class:**
   ```python
   Params.__guibbon_descriptors__["sigma"]            # SliderDescriptor(...)
   Params.__guibbon_descriptors__["resolution"]       # Nested descriptors dict
   Params.__guibbon_descriptors__["resolution"]["width"]  # SliderDescriptor(...)
   ```

5. **Current values on instances:**
   ```python
   params.sigma                       # Current value (TrackedFloat)
   params.resolution.width            # Current value (TrackedInt)
   ```

**Implementation Details:**

- Decorator extracts descriptors before `@dataclass` processes them
- Replaces descriptor defaults with their `.default` values so dataclass sees primitives
- Wraps `__init__` to track all field values with parent/field_name info
- Recursively wires nested `@guibbon.params` instances
- `GetPath()` walks up `_parent` chain to reconstruct dotted paths
- Nested fields automatically support IDE autocompletion

**Benefits:**
- ✅ **IDE support:** Full autocompletion on nested fields (real types)
- ✅ **Refactor-safe:** Use `GetPath(params.field)` instead of hand-written strings
- ✅ **Natural nesting:** Nested `@guibbon.params` classes work seamlessly
- ✅ **Real primitives:** No wrapping/unwrapping; tracked values ARE their types
- ✅ **Validation:** Descriptor/callback coherence checked at app init

---

## Parameter & Descriptor System

### **Descriptor Lifecycle**

```
1. USER DEFINES
   @guibbon.params
   class Params:
       size: int = SliderDescriptor(values=range(1,11), default=5)
       resolution: Resolution = Resolution()  # Nested

2. DECORATOR PROCESSES
   - Extracts descriptor metadata from class attributes
   - Applies @dataclass to generate __init__, __repr__, etc.
   - Wraps field values in tracked subclasses (TrackedInt, TrackedStr, etc.)
   - Wires parent chain: each tracked value knows _parent and _field_name
   - Stores descriptor metadata on class via __guibbon_descriptors__

3. APP INITIALIZES
   - Validates descriptor/callback coherence
   - Creates component instances
   - Initializes descriptor triggered_callbacks tracking
   - User callbacks can use GetPath(params.field) for refactoring

4. ON PARAMS CHANGE (User interacts with widget)
   - Widget detects change (slider drag, radio button click, etc.)
   - Calls descriptor.on_widget_change(trigger_type="drag"|"release"|"click")
   - Descriptor appends to triggered_callbacks: ["on_drag"] or ["on_release"]
   - App.need_update = True

5. MAIN LOOP (checks need_update)
   - App collects all triggered_callbacks from descriptors
   - Builds modified_descriptors list: ["size.on_drag", "resolution.width.on_release"]
   - Clears all triggered_callbacks for next cycle
   - Calls on_change(params, modified_descriptors)

6. DYNAMIC VISIBILITY (inside on_change)
   - Check modified_descriptors: if "filter_type.on_change" in modified_descriptors
   - Update descriptor.isVisible based on current params state
   - Component detects visibility change on next render
```

---

### **Modified Descriptors Tracking System**

**Problem:** Multiple overlays + multiple callbacks per descriptor; how to know what triggered?

**Solution:** Track which descriptor callbacks fired, return as `descriptor_name.callback_type` strings.

**User Callback Signature:**

```python
def on_change(self, params: Params, modified_descriptors: list[str]) -> np.ndarray:
    """
    Args:
        params: Current params instance with tracked field values
        modified_descriptors: List of "field.callback" strings that triggered
                             e.g., ["size.on_drag", "resolution.width.on_release"]
    Returns:
        Result to display (image, data, etc.)
    """
```

**Example 1: Refactor-safe field checking via GetPath**

```python
def on_change(self, params: Params, modified_descriptors: list[str]) -> np.ndarray:
    # GetPath makes field references refactor-safe
    if "size.on_release" in modified_descriptors:
        # Size slider finalized; full compute
        return self.compute_full(params)
    
    # Preview mode while user drags
    if any("on_drag" in md for md in modified_descriptors):
        return self.compute_preview(params)
    
    return self.compute_full(params)
```

**Example 2: Nested field access with IDE support**

```python
def on_change(self, params: Params, modified_descriptors: list[str]) -> np.ndarray:
    # IDE knows params.resolution is a Resolution instance
    # IDE knows params.resolution.width is an int
    # So autocompletion works perfectly
    
    if "resolution.width.on_release" in modified_descriptors:
        print(f"Width set to: {params.resolution.width}")  # int, IDE has hints
    
    if "resolution.height.on_release" in modified_descriptors:
        print(f"Height set to: {params.resolution.height}")  # int
    
    return self.apply_filter(params)
```

**Example 3: Dynamic visibility based on params**

```python
def on_change(self, params: Params, modified_descriptors: list[str]) -> np.ndarray:
    # Tracked values are real primitives; comparison works naturally
    if "filter_type.on_change" in modified_descriptors:
        # Type selector changed; update visibility
        if params.filter_type == "Gaussian":
            self.params.__guibbon_descriptors__["sigma"].isVisible = True
        else:
            self.params.__guibbon_descriptors__["sigma"].isVisible = False
    
    return self.apply_filter(params)
```

**Example 4: Multi-overlay tracking**

```python
def on_change(self, params: Params, modified_descriptors: list[str]) -> np.ndarray:
    # Track which overlays were modified
    overlay_changes = [md for md in modified_descriptors if "point" in md]
    
    if overlay_changes:
        for change in overlay_changes:
            # change is like "points.0.on_drag" or "points.1.on_release"
            if "on_release" in change:
                print(f"  {change} - finalized")
            else:
                print(f"  {change} - still dragging")
    
    return self.compute_roi_based_filter(params)
```

**Why this design:**
- ✅ **Clear semantics:** Exactly which descriptor + which callback
- ✅ **Scalable:** Multiple callbacks per descriptor handled naturally
- ✅ **User-friendly:** Pattern matching on strings vs magic IDs
- ✅ **Debuggable:** Print the list and see what fired
- ✅ **Refactor-safe:** GetPath() reconstructs paths automatically
- ✅ **IDE support:** Params instance has real types; autocompletion works

---

### **Custom Widget Pattern (Hybrid)**

**User writes a Widget class:**
```python
class MyKaleidoscopeWidget(BuildableWidget):
    def __init__(self, symmetry: int, on_change_callback):
        self.symmetry = symmetry
        self.callback = on_change_callback
    
    def build(self, parent: tk.Frame) -> None:
        # Plain Tkinter code
        tk.Label(parent, text=f"Symmetry: {self.symmetry}").pack()
        scale = tk.Scale(parent, from_=1, to=8, orient=tk.HORIZONTAL)
        scale.set(self.symmetry)
        scale.config(command=lambda v: self.callback(int(v)))
        scale.pack()
```

**User creates a Descriptor:**
```python
class MyKaleidoscopeDescriptor(BuildableDescriptor):
    widget_class = MyKaleidoscopeWidget
    
    def __init__(self, name: str, default=3):
        self.name = name
        self.current_value = default
```

**User uses it:**
```python
@guibbon.params
class Params:
    symmetry: int = MyKaleidoscopeDescriptor(name="symmetry", default=4)
```

**Benefit:** User's widget code has zero Guibbon imports; pure Tkinter.

---

## Data Flow & State Management

### **Single Source of Truth**

**Params Instance Structure:**

```
┌──────────────────────────────────────────────────────────────┐
│  Params Dataclass Instance (Single Source of Truth)          │
│                                                              │
│  INSTANCE ATTRIBUTES (Current Values):                       │
│  ├─ size: TrackedInt(5)          [inherits from int]        │
│  ├─ type: TrackedStr("Gaussian") [inherits from str]        │
│  ├─ sigma: TrackedFloat(1.0)     [inherits from float]      │
│  └─ resolution: Resolution                                   │
│     ├─ width: TrackedInt(512)   [inherits from int]         │
│     └─ height: TrackedInt(512)  [inherits from int]         │
│                                                              │
│  CLASS ATTRIBUTES (Metadata):                                │
│  ├─ __guibbon_descriptors__ = {                             │
│  │   'size': SliderDescriptor(...),                         │
│  │   'type': RadioDescriptor(...),                          │
│  │   'sigma': SliderDescriptor(...),                        │
│  │   'resolution': {  # Nested                              │
│  │     'width': SliderDescriptor(...),                      │
│  │     'height': SliderDescriptor(...),                     │
│  │   }                                                       │
│  ├─ __annotations__ = {...}  # Standard dataclass           │
│  └─ __dataclass_fields__ = {...}  # Standard dataclass      │
└──────────────────────────────────────────────────────────────┘
         ▲                           ▲
         │                           │
    [reads current values]       [stores metadata]
         │                           │
         └───────────────┬───────────┘
                         │
                 [GUI Widgets Update]
                         │
              [Sliders, Buttons, Points]
```

**Key Design Points:**

1. **Tracked values are real primitives:**
   ```python
   params.size  # Returns TrackedInt(5), which IS-A int
   params.size + 10  # Works! Type check: isinstance(params.size, int) → True
   ```

2. **Nested structures work seamlessly:**
   ```python
   params.resolution  # Returns Resolution instance
   params.resolution.width  # Returns TrackedInt(512)
   GetPath(params.resolution.width)  # → "resolution.width"
   ```

3. **Descriptors hold metadata (on class):**
   ```python
   Params.__guibbon_descriptors__["size"]  # SliderDescriptor(...)
   Params.__guibbon_descriptors__["size"].values  # range(1, 11)
   Params.__guibbon_descriptors__["size"].triggered_callbacks  # ["on_drag"]
   ```

4. **Callback receives entire params instance:**
   ```python
   def on_change(self, params: Params, modified_descriptors: list[str]):
       # Full access to all current values
       print(params.size)  # Current TrackedInt
       print(params.resolution.width)  # Current TrackedInt
       # No need to pass individual fields; everything available
   ```

5. **All mutations go through params instance:**
   ```python
   # GUI widget: slider.set(7)
   params.size = TrackedInt(7, _parent=params, _field_name="size")
   
   # Descriptor detects change and appends to triggered_callbacks
   # App collects and builds modified_descriptors list
   # App calls on_change(params, ["size.on_drag"])
   ```

---

### **Event Flow with Modified Descriptors**

```
1. USER INTERACTS WITH WIDGET
   └─> slider.on_drag_callback(value)
   └─> descriptor.triggered_callbacks.append("on_drag")
   └─> app.need_update = True

2. MAIN LOOP DETECTS need_update
   └─> Collect all triggered_callbacks from each descriptor
   └─> modified_descriptors = ["size.on_drag", "type.on_change", ...]
   └─> Clear all triggered_callbacks for next cycle

3. DETERMINE COMPUTATION MODE
   └─> is_interacting()? 
       ├─> YES: result = on_change_preview(modified_descriptors)
       └─> NO: result = on_change(modified_descriptors)

4. UPDATE GUI
   └─> app.image_viewer.set_image(result)
   └─> app.wait(timeout)

5. DYNAMIC VISIBILITY (inside on_change)
   └─> if "type.on_change" in modified_descriptors:
       └─> if params.type == "Gaussian":
           └─> descriptors.sigma.isVisible = True
```

---

### **need_update Propagation (Cascading Property)**

```
App.need_update
├─> ImageViewer.need_update
│   └─> PointOverlay1.need_update
│   └─> PointOverlay2.need_update
│   └─> PolygonOverlay.need_update
│
└─> Controller.need_update
    └─> SliderWidget.need_update
    └─> RadioWidget.need_update

On query: need_update = OR(all children's need_update)
On any change: child sets own flag; parent computes aggregate

Benefit: No manual state propagation; automatic!
```

---

## Extension Points & Customization

### **Level 1: Use Provided Descriptors (Easiest)**
```python
@guibbon.params
class Params:
    size: int = SliderDescriptor(...)
    type: str = RadioDescriptor(...)

class MyApp(InteractiveImageAppBase):
    def on_change(self):
        return filter(self.image, self.params)
```

### **Level 2: Custom Descriptors + Widgets**
```python
class MyDescriptor(BuildableDescriptor):
    widget_class = MyWidget

@guibbon.params
class Params:
    my_param: int = MyDescriptor(...)
```

### **Level 3: Custom Base Class**
```python
class MyCustomApp(InteractiveImageAppBase):
    def run(self):
        # Custom event loop logic
        # Custom timing controls
        # Custom preview vs full compute logic
        while self.app.is_running():
            ...
```

### **Level 4: No Base Class (Full Control)**
```python
class MyManualApp:
    def __init__(self):
        self.params = Params()
        self.image_viewer = gbn.ImageViewer(self.params)
        self.controller = gbn.Controller(self.params)
        # Custom wiring...
```

---

## Module Organization

```
guibbon2/
├── core/
│   ├── __init__.py
│   ├── params.py           # @guibbon.params decorator
│   ├── descriptor.py       # Base descriptor classes
│   ├── buildable.py        # BuildableWidget protocol
│   └── app.py              # App orchestrator
│
├── controller/
│   ├── __init__.py
│   ├── controller.py       # Controller component
│   ├── slider.py           # SliderDescriptor + widget
│   ├── radio.py            # RadioDescriptor + widget
│   ├── button.py           # ButtonDescriptor + widget
│   └── __init__.py         # Re-exports for user imports
│
├── image_viewer/
│   ├── __init__.py
│   ├── image_viewer.py     # ImageViewer component
│   ├── point.py            # InteractivePointDescriptor
│   ├── polygon.py          # InteractivePolygonDescriptor
│   ├── rectangle.py        # InteractiveRectangleDescriptor
│   └── __init__.py         # Re-exports
│
├── apps/
│   ├── __init__.py
│   ├── simple_image_viewer.py   # Use case 1: show/wait
│   ├── controller_app.py        # Use case 2: ControllerAppBase
│   └── image_app.py             # Use case 3: InteractiveImageAppBase
│
└── tests/
    ├── test_params.py
    ├── test_descriptors.py
    ├── test_controller.py
    ├── test_image_viewer.py
    └── test_apps.py
```

**Import Patterns for Users:**

```python
# Built-in descriptors are location-aware
from guibbon.controller import SliderDescriptor, RadioDescriptor
from guibbon.image_viewer import InteractivePointDescriptor

# App base classes
from guibbon import ControllerAppBase, InteractiveImageAppBase

# Core utilities
from guibbon import params as guibbon_params
```

---

## Testability Strategy

### **What's Tested (100% Coverage)**

1. **Tracked Type Generation**
   - `_make_tracked_type()` creates subclasses of base types (int, str, float, etc.)
   - Tracked subclasses inherit from their base types
   - `isinstance(TrackedInt(5), int)` returns True
   - Tracked instances carry `_parent` and `_field_name` attributes

2. **GetPath Function**
   - `GetPath(obj)` walks up `_parent` chain correctly
   - Nested structures reconstructed as dotted paths
   - `GetPath(params.resolution.width)` → `"resolution.width"`

3. **@guibbon.params Decorator**
   - Decorator extracts descriptor metadata from class
   - Applies `@dataclass` correctly
   - Wraps field values in tracked subclasses
   - Wires parent/field_name for entire object graph
   - Stores descriptors on class via `__guibbon_descriptors__`
   - Nested `@guibbon.params` classes work correctly

4. **Descriptor Logic**
   - `descriptor.triggered_callbacks` tracks ("on_drag", "on_release", etc.)
   - Multiple callbacks per descriptor supported
   - Visibility toggle (`isVisible`) works
   - Descriptor metadata accessible via `Params.__guibbon_descriptors__`

5. **Modified Descriptors Collection**
   - App collects all `triggered_callbacks` from descriptors
   - Builds `modified_descriptors` list as `["field.callback_type", ...]`
   - Callback receives correct list of what triggered
   - triggered_callbacks cleared after collection

6. **App Orchestration** (non-GUI)
   - `need_update` cascading logic
   - Component registration
   - Params mutation detection

7. **User Callback Injection**
   - User callback receives `params` (dataclass instance)
   - User callback receives `modified_descriptors` (list of strings)
   - Return value used correctly
   - Dynamic visibility works inside callback

**Example Tests:**

```python
def test_tracked_type_is_real_primitive():
    \"\"\"Tracked values inherit from their base types.\"\"\"
    tracked_int = TrackedInt(5, _parent=None, _field_name="test")
    assert isinstance(tracked_int, int)
    assert tracked_int + 10 == 15
    assert tracked_int * 2 == 10

def test_getpath_reconstruction():
    \"\"\"GetPath walks parent chain to reconstruct dotted paths.\"\"\"
    params = Params()  # Has resolution.width
    width_value = params.resolution.width
    assert GetPath(width_value) == "resolution.width"
    
    sigma_value = params.sigma
    assert GetPath(sigma_value) == "sigma"

def test_guibbon_params_decorator():
    \"\"\"Decorator creates dataclass with tracked values.\"\"\"
    @guibbon.params
    class TestParams:
        size: int = SliderDescriptor(values=range(1, 11), default=5)
        name: str = RadioDescriptor(options=["A", "B"], default="A")
    
    params = TestParams()
    assert params.size == 5
    assert isinstance(params.size, int)  # TrackedInt IS-A int
    assert params.name == "A"
    assert isinstance(params.name, str)  # TrackedStr IS-A str
    assert hasattr(TestParams, '__guibbon_descriptors__')
    assert 'size' in TestParams.__guibbon_descriptors__

def test_modified_descriptors_collection():
    \"\"\"App collects triggered_callbacks and builds modified_descriptors list.\"\"\"
    params = Params()
    descriptor = params.__guibbon_descriptors__['size']
    
    # Simulate user dragging slider
    descriptor.triggered_callbacks.append('on_drag')
    
    # App collects
    modified = [f'size.{cb}' for cb in descriptor.triggered_callbacks]
    assert 'size.on_drag' in modified
    
    # Clear for next cycle
    descriptor.triggered_callbacks.clear()

def test_user_callback_receives_params_and_modified_descriptors():
    \"\"\"User callback gets full params and list of what changed.\"\"\"
    callback_received_params = None
    callback_received_modified = None
    
    def mock_callback(params: Params, modified_descriptors: list[str]):
        nonlocal callback_received_params, callback_received_modified
        callback_received_params = params
        callback_received_modified = modified_descriptors
        return np.zeros((10, 10))
    
    params = Params()
    modified = [\"size.on_release\", \"type.on_change\"]
    
    # App would call it like:
    result = mock_callback(params, modified)
    
    assert callback_received_params is params
    assert callback_received_modified == modified

def test_dynamic_visibility_in_callback():
    \"\"\"Callback can check modified_descriptors and update visibility.\"\"\"
    @guibbon.params
    class Params:
        filter_type: str = RadioDescriptor(options=["Gaussian\", \"Bilateral\"], default=\"Gaussian\")
        sigma: float = SliderDescriptor(values=[0.1, 1.0, 5.0], default=1.0)
    
    params = Params()
    
    # Simulate type change
    params.__guibbon_descriptors__['filter_type'].triggered_callbacks.append('on_change')
    modified_descriptors = ['filter_type.on_change']
    
    # Inside callback: update visibility based on current params
    if \"filter_type.on_change\" in modified_descriptors:
        if params.filter_type == \"Gaussian\":
            params.__guibbon_descriptors__['sigma'].isVisible = True
        else:
            params.__guibbon_descriptors__['sigma'].isVisible = False
    
    assert params.__guibbon_descriptors__['sigma'].isVisible == True
```

### **What's NOT Tested (Acceptable Flakiness)**

1. **Tkinter widget rendering** (flaky, not worth testing)
2. **Mouse events on canvas** (flaky, user's responsibility)
3. **Image display pixel-perfect rendering** (flaky)

**Acceptance:** These areas are tested via manual integration tests and user examples; automated test flakiness not worth the overhead.

---

---

## Usage Patterns — Detailed Examples

This section shows concrete implementations of the three usage patterns introduced in the Overview.

### **Pattern 1: Simple set_image/wait (Blocking Display)**

Similar to OpenCV's `imshow`/`waitKey` or matplotlib's `show`. The app blocks until the user closes the window.

```python
import cv2
import guibbon

def process_image(img, offset):
    return img + offset

img = cv2.imread("path/to/image.png")
result = process_image(img, 10)

# Minimal: just display the image and wait for user to close window
app = guibbon.ImageViewer()
app.set_image(result)
app.wait(0)  # 0 = wait indefinitely until closed
```

**Use cases:** Quick visualization, debugging, one-off image display.

---

### **Pattern 2: Interactive Controller (Parameters Only, No Image)**

A reactive loop where changing parameters triggers computation. The result can be any data structure (not necessarily an image) — users are responsible for displaying it.

```python
import guibbon
from guibbon import SliderDescriptor
from dataclasses import field
import abc

# Base class provided by Guibbon (Phase 3)
class ControllerAppBase(abc.ABC):
    def __init__(self, refresh_rate=10):
        if not hasattr(self, "params"):
            raise ValueError("Subclasses must define `params` as a @guibbon.params instance")
        self.refresh_rate = refresh_rate
        self.controller = guibbon.Controller(self.params)
        self.app = guibbon.App([self.controller], self.params)

    def run(self):
        while self.app.is_running():
            if self.app.need_update:
                self.on_change()
                self.app.need_update = False
            self.app.wait(timeout=1/self.refresh_rate)

    @abc.abstractmethod
    def on_change(self) -> None:
        """Implement computation logic here."""
        raise NotImplementedError()

# User's application
def process_data(data, offset: int):
    return data + offset

class MyDataApp(ControllerAppBase):
    @guibbon.params
    class Params:
        offset: int = SliderDescriptor(values=range(3, 11, 2), default=3)

    def __init__(self, refresh_rate=10):
        self.params = MyDataApp.Params()
        super().__init__(refresh_rate=refresh_rate)
        self.data = [1, 2, 3, 4, 5]  # Load user's data

    def on_change(self):
        result = process_data(self.data, self.params.offset)
        # User is responsible for displaying result
        # (e.g., print it, save it, send to matplotlib, etc.)
        print(f"Result: {result}")

# Run the app
app = MyDataApp(refresh_rate=10)
app.run()
```

**Use cases:** Data processing, interactive analysis, parameter tuning without image display.

---

### **Pattern 3: Interactive Image Viewer (Parameters + Image with Overlays)**

Full interactive application: parameter controls + image canvas + interactive overlays. This combines controller + image viewer components.

```python
import numpy as np
import guibbon
from guibbon import SliderDescriptor, InteractivePointDescriptor
from typing import Tuple
import abc

# Base class provided by Guibbon (Phase 3)
class InteractiveImageAppBase(abc.ABC):
    def __init__(self, refresh_rate=10):
        if not hasattr(self, "params"):
            raise ValueError("Subclasses must define `params` as a @guibbon.params instance")
        
        self.refresh_rate = refresh_rate
        
        # Create components: each looks at params and builds only widgets it supports
        image_viewer = guibbon.ImageViewer(self.params)
        controller = guibbon.Controller(self.params)
        
        # App orchestrator manages both
        self.app = guibbon.App([image_viewer, controller], self.params)

    def run(self):
        while self.app.is_running():
            if self.app.need_update:
                result = self.on_change()
                self.app.image_viewer.set_image(result)
                self.app.need_update = False
            self.app.wait(timeout=1/self.refresh_rate)

    @abc.abstractmethod
    def on_change(self) -> np.ndarray:
        """Implement computation logic returning an image."""
        raise NotImplementedError()

# User's application
def process_image(image, size: int, pos_xy: Tuple[int, int]) -> np.ndarray:
    """Apply filter based on parameters."""
    result = image.copy()
    x, y = pos_xy
    # Example: draw a colored rectangle at the interactive point
    result[max(0, y):min(result.shape[0], y+size), 
           max(0, x):min(result.shape[1], x+size)] = [255, 0, 0]
    return result

class MyFilterApp(InteractiveImageAppBase):
    @guibbon.params
    class Params:
        # Slider: handled by Controller component
        size: int = SliderDescriptor(values=range(3, 11, 2), default=3)
        
        # Interactive point: handled by ImageViewer component
        pos_xy: Tuple[int, int] = InteractivePointDescriptor(
            default=(0, 0), 
            on_drag=True  # Trigger while dragging
        )

    def __init__(self, refresh_rate=10):
        self.params = MyFilterApp.Params()
        super().__init__(refresh_rate=refresh_rate)
        self.image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    def on_change(self) -> np.ndarray:
        """Called whenever parameters change."""
        result = process_image(
            self.image,
            self.params.size,
            self.params.pos_xy
        )
        return result

# Run the app
app = MyFilterApp(refresh_rate=10)
app.run()
```

**Use cases:** Interactive image filtering, scientific image exploration, parameter-driven visualization.

---

### **Key Patterns in Use**

1. **Descriptor placement is automatic:**
   - `SliderDescriptor` → Controller component creates the slider widget
   - `InteractivePointDescriptor` → ImageViewer component creates the overlay
   - No manual widget routing — components know what they support

2. **Nested params work naturally:**
   ```python
   @guibbon.params
   class Resolution:
       width: int = SliderDescriptor(values=range(1, 1025), default=512)
       height: int = SliderDescriptor(values=range(1, 1025), default=768)

   @guibbon.params
   class Params:
       resolution: Resolution = field(default_factory=Resolution)
   
   # In callback:
   print(self.params.resolution.width)  # IDE autocomplete works
   print(GetPath(self.params.resolution.width))  # → "resolution.width"
   ```

3. **Modified descriptors pattern in callbacks:**
   ```python
   def on_change(self, params, modified_descriptors):
       if "pos_xy.on_drag" in modified_descriptors:
           # Preview mode while user drags
           return self.compute_preview(params)
       
       if "size.on_release" in modified_descriptors:
           # Full compute when user releases slider
           return self.compute_full(params)
   ```

---

## Implementation Roadmap

### **Phase 1: Core Infrastructure (Week 1-2)**

**Deliverables:**

1. **`params.py`: GetPath + Tracked Values System**
   - `_make_tracked_type(base: type) → type`: Create subclasses of int, str, float, bool, tuple, list, dict
   - `_wrap_value(value, parent, field_name) → Any`: Wrap field values in tracked subclasses
   - `_track_fields(instance) → None`: Recursively wrap all dataclass fields
   - `GetPath(obj: Any) → str`: Walk parent chain to reconstruct dotted paths
   - `_params_decorator(cls) → type`: Main decorator applying @dataclass + tracking
   - Usage: `@guibbon.params` decorator on user classes

2. **`descriptor.py`: Base Descriptor Classes**
   - `Descriptor`: Abstract base with metadata (name, default, isVisible, triggered_callbacks)
   - `BuildableDescriptor`: For custom widgets (widget_class attribute)
   - `SliderDescriptor`: int/float with values range, callback modes (on_drag, on_release)
   - `RadioDescriptor`: str/int with options, on_change callback
   - Callback tracking: `triggered_callbacks` list appends callback types

3. **`buildable.py`: BuildableWidget Protocol**
   - `BuildableWidget` protocol: `build(parent) → None` method
   - No framework dependencies; pure Tkinter expected

4. **`app.py`: App Orchestrator (non-GUI)**
   - `App` class: component registration, params validation
   - `need_update` cascading property
   - Modified descriptors collection: scan all descriptors for triggered_callbacks
   - Main loop skeleton (no GUI)

**Tests:** 100% coverage of non-GUI code
- test_tracked_types.py: Type generation, inheritance, isinstance checks
- test_getpath.py: Path reconstruction for nested structures
- test_params_decorator.py: Decorator extraction, @dataclass application, parent wiring
- test_descriptors.py: Metadata storage, triggered_callbacks, visibility
- test_app_orchestration.py: need_update cascading, descriptor collection

**Key Code from draft.py:**
All core logic already exists in draft.py (200+ lines). Phase 1 is extracting, refining, and creating tests.

### **Phase 2: Components (Week 3-4)**
- [ ] Controller component (assembles slider/radio widgets)
- [ ] ImageViewer component (canvas + overlays from Guibbon1)
- [ ] App + GUI integration (event loop, main window)
- [ ] need_update cascading across components

**Tests:** Component composition, event routing, state updates

### **Phase 3: Base Classes (Week 5)**
- [ ] ControllerAppBase (parameters only, no image)
- [ ] InteractiveImageAppBase (parameters + image + callbacks)
- [ ] Simple show/wait utility

**Tests:** App lifecycle, on_change integration, refresh rates

### **Phase 4: Documentation & Examples (Week 6)**
- [ ] Example 1: Simple show/wait
- [ ] Example 2: Interactive controller (data processing)
- [ ] Example 3: Interactive image viewer (filter exploration)
- [ ] Custom widget example
- [ ] API reference

---

## Key Decision Summary

| Question | Decision | Rationale |
|----------|----------|-----------|
| **Params field access?** | GetPath + Tracked Values | IDE autocompletion + refactor-safe paths |
| **Single source of truth?** | Params dataclass instance | Type-safe, prevents state duplication |
| **How to bind params?** | Descriptors + callbacks | Declarative, auto-validated |
| **Callback tracking?** | Modified descriptors (["field.callback"]) | Clear semantics, scalable, refactor-safe |
| **Custom widgets?** | Protocol + optional widget class | User writes plain Tkinter |
| **Framework?** | Tkinter + pluggable design | Simplicity + future flexibility |
| **Preview mode?** | on_change + on_change_preview | User chooses granularity |

---

## Open Questions for Implementation

1. **Error handling:** What happens if user's on_change() raises an exception?
2. **Visibility toggle:** When descriptor.isVisible changes, how quickly does widget hide?
3. **Image input pattern:** Should ImageViewer support multiple images or single?
4. **Type hints:** How strictly to enforce type coherence between descriptor and field?
5. **State persistence:** Should app support save/load of params state?

---

**Next Step:** Begin implementation of Phase 1 (Core Infrastructure) from draft.py prototype.
