"""
@guibbon.params decorator with GetPath support.

Design: GetPath + Tracked Values
=================================
The @guibbon.params decorator generates standard @dataclass classes with
tracked field values. IDE sees real types for full autocompletion on nested
fields (e.g. params.resolution.width).

At runtime, field values are replaced with *tracked* subclasses of their
original types. Tracked values carry hidden _parent and _field_name attributes.
GetPath(field) walks the parent chain to reconstruct the dotted path string.

Benefits:
  - IDE autocompletion on all fields and sub-fields
  - Refactor-safe path identifiers (use GetPath instead of hand-written strings)
  - Descriptor metadata stored on CLASS, current values on INSTANCES
  - Nested @guibbon.params classes work seamlessly

Example:
    @guibbon.params
    class Params:
        size: int = SliderDescriptor(values=range(1, 11), default=5)
        sigma: float = SliderDescriptor(values=[0.1, 1.0, 5.0], default=1.0)

    params = Params()
    params.size                  # -> 5 (real int, IDE knows this)
    GetPath(params.size)         # -> "size"
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Iterable


# ---------------------------------------------------------------------------
# Tracked value wrappers (subclass the real type, carry parent info)
# ---------------------------------------------------------------------------

_TRACKED_CACHE: dict[type, type] = {}


def _make_tracked_type(base: type) -> type:
    """Create a subclass of *base* that carries _parent and _field_name.

    For immutable types (int, str, float, bool, tuple), override __new__.
    For mutable types (list, dict), override __init__.

    Args:
        base: The type to subclass (e.g., int, str, float)

    Returns:
        A new type that carries _parent and _field_name metadata
    """
    if base in _TRACKED_CACHE:
        return _TRACKED_CACHE[base]

    if base.__hash__ is None:
        # Unhashable mutable types (list, dict, …) — inject via __init__
        class Tracked(base):
            def __init__(self, *args, _parent=None, _field_name="", **kwargs):
                super().__init__(*args, **kwargs)
                object.__setattr__(self, '_parent', _parent)
                object.__setattr__(self, '_field_name', _field_name)
    else:
        # Immutable types (int, str, float, bool, tuple, …) — need __new__
        class Tracked(base):
            def __new__(cls, *args, _parent=None, _field_name="", **kwargs):
                obj = base.__new__(cls, *args, **kwargs)
                object.__setattr__(obj, '_parent', _parent)
                object.__setattr__(obj, '_field_name', _field_name)
                return obj

    Tracked.__name__ = f"Tracked{base.__name__}"
    Tracked.__qualname__ = Tracked.__name__
    _TRACKED_CACHE[base] = Tracked
    return Tracked


def _wrap_value(value: Any, parent: Any, field_name: str) -> Any:
    """Wrap *value* so it knows its parent and field name.

    For dataclass instances, tag directly and recurse into fields.
    For primitives, wrap in tracked subclass.

    Args:
        value: The value to wrap
        parent: The parent object (usually a dataclass instance)
        field_name: The field name (for path reconstruction)

    Returns:
        The wrapped value (carrying _parent and _field_name metadata)
    """
    if is_dataclass(value) and not isinstance(value, type):
        # Dataclass instance — tag it directly, then recurse into its fields
        object.__setattr__(value, '_parent', parent)
        object.__setattr__(value, '_field_name', field_name)
        _track_fields(value)
        return value
    # Primitive type — wrap in tracked subclass
    TrackedType = _make_tracked_type(type(value))
    return TrackedType(value, _parent=parent, _field_name=field_name)


def _track_fields(instance: Any) -> None:
    """Replace each field of a dataclass *instance* with a tracked copy.

    Walks all @dataclass fields and wraps them with parent/field_name info.
    This enables GetPath() to reconstruct dotted paths.

    Args:
        instance: The dataclass instance to track
    """
    for f in fields(instance):
        val = getattr(instance, f.name)
        wrapped = _wrap_value(val, parent=instance, field_name=f.name)
        object.__setattr__(instance, f.name, wrapped)


# ---------------------------------------------------------------------------
# GetPath — walk up the parent chain to reconstruct dotted paths
# ---------------------------------------------------------------------------

def GetPath(obj: Any) -> str:
    """Reconstruct the dotted path from root to *obj*.

    Walks up the _parent chain to build the full field path. This enables
    refactor-safe path identification without hand-written strings.

    Args:
        obj: An object with _parent and _field_name attributes (usually
             a tracked value)

    Returns:
        The dotted path string (e.g., "resolution.width", "sigma")

    Example:
        params = Params()  # Has resolution.width field
        GetPath(params.resolution.width)  # -> "resolution.width"
    """
    parts: list[str] = []
    current = obj
    while hasattr(current, '_field_name') and current._field_name:
        parts.append(current._field_name)
        current = current._parent
    return ".".join(reversed(parts))


# ---------------------------------------------------------------------------
# Base descriptor class
# ---------------------------------------------------------------------------

class _BaseDescriptor:
    """Base class for all Guibbon parameter descriptors.

    Descriptors hold metadata (default value, options, etc.) about a parameter.
    They are stored on the CLASS and never modified; only referenced for
    metadata. Current parameter VALUES are stored on INSTANCES, wrapped in
    tracked subclasses.

    Attributes:
        default: The default value for this parameter
        triggered_callbacks: List of callback types that fired (e.g., ["on_drag"])
        isVisible: Whether this parameter widget should be visible in the UI
    """

    def __init__(self, default: Any) -> None:
        self.default = default
        self.triggered_callbacks: list[str] = []
        self.isVisible: bool = True


# ---------------------------------------------------------------------------
# Concrete descriptor classes
# ---------------------------------------------------------------------------

class SliderDescriptor(_BaseDescriptor):
    """Descriptor backed by a slider widget.

    Args:
        values: Iterable of valid slider values
        default: Initial slider value (must be in values)
        on_drag: If True, append "on_drag" to triggered_callbacks while dragging
        on_release: If True, append "on_release" when user releases the slider
    """

    def __init__(
        self,
        values: Iterable,
        default: Any,
        on_drag: bool = True,
        on_release: bool = False,
    ) -> None:
        self.values = list(values)
        if default not in self.values:
            raise ValueError(f"default {default!r} is not in values {self.values}")
        self.on_drag = on_drag
        self.on_release = on_release
        super().__init__(default)


class RadioDescriptor(_BaseDescriptor):
    """Descriptor backed by radio buttons or dropdown.

    Args:
        options: List of valid options (strings or other values)
        default: Initial selected option (must be in options)
        on_change: If True, append "on_change" to triggered_callbacks when option changes
    """

    def __init__(
        self,
        options: list[str],
        default: str,
        on_change: bool = True,
    ) -> None:
        self.options = options
        if default not in self.options:
            raise ValueError(f"default {default!r} is not in options {self.options}")
        self.on_change = on_change
        super().__init__(default)


# ---------------------------------------------------------------------------
# @guibbon.params decorator
# ---------------------------------------------------------------------------

def _params_decorator(cls: type) -> type:
    """Transform a class into a @dataclass with tracked field values.

    Steps:
    1. Collect descriptor defaults before @dataclass processes them
    2. Apply @dataclass to generate __init__, __repr__, __eq__, etc.
    3. Store descriptors on __guibbon_descriptors__ for the GUI builder
    4. Replace descriptor attribute defaults with their .default values
    5. Wire up __init__ to track all fields for GetPath support

    Args:
        cls: A class with Field and Descriptor attributes

    Returns:
        The transformed class (now a @dataclass with tracked values)
    """
    # --- Collect descriptors before @dataclass consumes them ----------------
    annotations = getattr(cls, '__annotations__', {})
    descriptors: dict[str, _BaseDescriptor] = {}
    for name in annotations:
        value = getattr(cls, name, dataclasses.MISSING)
        if isinstance(value, _BaseDescriptor):
            descriptors[name] = value
            # Replace the descriptor with its plain default so @dataclass
            # sees a normal default value (not a descriptor object).
            setattr(cls, name, value.default)

    # --- Apply @dataclass ---------------------------------------------------
    cls = dataclass(cls)

    # --- Store descriptors on the class for the GUI builder -----------------
    cls.__guibbon_descriptors__ = descriptors

    # --- Wrap __init__ to add parent tracking after construction ------------
    original_init = cls.__init__

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        # Mark this instance as a root (no parent)
        object.__setattr__(self, '_parent', None)
        object.__setattr__(self, '_field_name', "")
        # Track all fields so GetPath works
        _track_fields(self)

    cls.__init__ = __init__
    return cls


# Public alias — exposed at package level so `@guibbon.params` works
# via `import guibbon; @guibbon.params`.
params = _params_decorator
