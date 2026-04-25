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

This module defines only the **framework contracts** (abstract bases).
Concrete descriptors (SliderDescriptor, RadioDescriptor, …) live in their
respective component packages (e.g. guibbon.controller) and are unknown here.
Users may create their own descriptors by subclassing BuildableDescriptor.

Class hierarchy:
    Descriptor (ABC) — base contract
    └── BuildableDescriptor — adds optional widget_class for custom widgets
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


# ---------------------------------------------------------------------------
# Abstract base descriptor
# ---------------------------------------------------------------------------

class Descriptor(ABC):
    """Abstract base class for all Guibbon parameter descriptors.

    Descriptors carry parameter metadata (default value, visibility) and track
    which GUI callbacks fired in the current event cycle.

    Attributes:
        default: The default value for this parameter.
        is_visible: Whether this parameter's widget should be visible in the UI.
        triggered_callbacks: Callback names that fired this cycle (e.g., ["on_drag"]).
                             Cleared by the app at the start of each cycle.
    """

    def __init__(self, default: Any) -> None:
        self.default = default
        self.is_visible: bool = True
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

    This is the standard base for all built-in and user-defined descriptors.

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
