"""RadioDescriptor — parameter descriptor backed by radio buttons / dropdown."""

from __future__ import annotations

from guibbon.core.descriptor import BuildableDescriptor


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
