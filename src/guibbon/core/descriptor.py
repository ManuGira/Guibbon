"""
Descriptor base classes for Guibbon parameter controls.

Design: Modified Descriptors Pattern
=====================================
Each descriptor stores metadata about a parameter (defaults, ranges, options)
and tracks which callbacks fired during a GUI event cycle.

When a user interacts with a widget (drag slider, click radio button):
  1. Widget calls descriptor.on_widget_change(trigger_type="drag"|"release"|"change"|"click")
  2. Descriptor appends matching callback name to triggered_callbacks
  3. App reads triggered_callbacks; builds ["field.on_drag", "field.on_release"] list
  4. App clears triggered_callbacks for next cycle

Class hierarchy:
    Descriptor (ABC)
    └── BuildableDescriptor (adds optional widget_class)
        ├── SliderDescriptor
        └── RadioDescriptor

Usage:
    @guibbon.params
    class Params:
        size: int = SliderDescriptor(values=range(1, 11), default=5)
        mode: str = RadioDescriptor(options=["fast", "accurate"], default="fast")

    descriptor = Params.__guibbon_descriptors__["size"]
    descriptor.on_widget_change("drag")       # User dragged slider
    descriptor.get_triggered_descriptors("size")  # -> ["size.on_drag"]
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable


# ---------------------------------------------------------------------------
# Abstract base descriptor
# ---------------------------------------------------------------------------

class Descriptor(ABC):
    """Abstract base class for all Guibbon parameter descriptors.

    Descriptors carry parameter metadata (default value, visibility) and track
    which GUI callbacks fired in the current event cycle.

    Attributes:
        default: The default value for this parameter.
        isVisible: Whether this parameter's widget should be visible in the UI.
        triggered_callbacks: Callback names that fired this cycle (e.g., ["on_drag"]).
                             Cleared by the app at the start of each cycle.
    """

    def __init__(self, default: Any) -> None:
        self.default = default
        self.isVisible: bool = True
        self.triggered_callbacks: list[str] = []

    @abstractmethod
    def on_widget_change(self, trigger_type: str) -> None:
        """Called by the widget layer when a user interaction occurs.

        Subclasses must append to ``triggered_callbacks`` for each callback
        type that is both enabled and matches *trigger_type*.

        Args:
            trigger_type: Type of GUI event ("drag", "release", "change", "click").
        """
        ...

    def get_triggered_descriptors(self, field_name: str) -> list[str]:
        """Return triggered descriptors as ``"field_name.callback_type"`` strings.

        The app calls this after an event cycle to build the ``modified_descriptors``
        list passed to the user's ``on_change`` callback.

        Args:
            field_name: Dotted path of this descriptor's field (from GetPath or
                        stored during app initialization).

        Returns:
            List of strings like ``["size.on_drag", "size.on_release"]``.

        Example:
            descriptor.triggered_callbacks = ["on_drag"]
            descriptor.get_triggered_descriptors("size")  # -> ["size.on_drag"]
        """
        return [f"{field_name}.{cb}" for cb in self.triggered_callbacks]


# ---------------------------------------------------------------------------
# BuildableDescriptor — descriptors with an optional custom widget class
# ---------------------------------------------------------------------------

class BuildableDescriptor(Descriptor):
    """Descriptor that can carry a custom ``widget_class``.

    This is the standard base for all built-in descriptors (Slider, Radio, …)
    and for user-defined custom widgets.

    ``widget_class`` may be set at the class level by subclasses:

        class MyDescriptor(BuildableDescriptor):
            widget_class = MyWidget

    When ``widget_class is None``, the framework uses the default widget for
    that descriptor type.  When set, the Controller calls
    ``widget_class(...).build(parent)`` at startup.
    """

    widget_class: type | None = None

    def on_widget_change(self, trigger_type: str) -> None:  # pragma: no cover
        """Default no-op; concrete subclasses override to track events."""
        pass


# ---------------------------------------------------------------------------
# SliderDescriptor
# ---------------------------------------------------------------------------

class SliderDescriptor(BuildableDescriptor):
    """Descriptor backed by a slider widget.

    Supports two callback modes that can be enabled independently:
      - ``on_drag`` — fires continuously while the user moves the slider.
      - ``on_release`` — fires once when the user releases the slider thumb.

    Args:
        values: Ordered iterable of valid slider values.
        default: Initial value; must be present in *values*.
        on_drag: Fire the callback during slider movement.
        on_release: Fire the callback when the slider is released.

    Raises:
        ValueError: If *default* is not in *values*.

    Example:
        size_desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)
        size_desc.on_widget_change("drag")
        size_desc.get_triggered_descriptors("size")  # -> ["size.on_drag"]
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

    def on_widget_change(self, trigger_type: str) -> None:
        """Track drag/release events if the corresponding flag is enabled.

        Args:
            trigger_type: ``"drag"`` or ``"release"``.
        """
        if trigger_type == "drag" and self.on_drag:
            self.triggered_callbacks.append("on_drag")
        elif trigger_type == "release" and self.on_release:
            self.triggered_callbacks.append("on_release")


# ---------------------------------------------------------------------------
# RadioDescriptor
# ---------------------------------------------------------------------------

class RadioDescriptor(BuildableDescriptor):
    """Descriptor backed by radio buttons or a dropdown widget.

    Supports a single callback mode:
      - ``on_change`` — fires when the user selects a new option.

    Args:
        options: Ordered list of valid options.
        default: Initially selected option; must be present in *options*.
        on_change: Fire the callback when the selection changes.

    Raises:
        ValueError: If *default* is not in *options*.

    Example:
        mode_desc = RadioDescriptor(options=["fast", "accurate"], default="fast")
        mode_desc.on_widget_change("change")
        mode_desc.get_triggered_descriptors("mode")  # -> ["mode.on_change"]
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

    def on_widget_change(self, trigger_type: str) -> None:
        """Track change events if ``on_change`` is enabled.

        Args:
            trigger_type: ``"change"`` (other values are silently ignored).
        """
        if trigger_type == "change" and self.on_change:
            self.triggered_callbacks.append("on_change")
