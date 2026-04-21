"""SliderDescriptor — parameter descriptor backed by a slider widget."""

from __future__ import annotations

from typing import Any, Iterable

from guibbon.core.descriptor import BuildableDescriptor


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
