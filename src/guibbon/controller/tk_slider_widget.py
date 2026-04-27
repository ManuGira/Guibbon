"""Tkinter widget adapter for ``SliderDescriptor``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._theme import BG_CARD, BG_TROUGH, FG
from .slider import SliderDescriptor

if TYPE_CHECKING:
    from .controller import Controller


class _TkSliderWidget:
    """Default Tkinter widget for ``SliderDescriptor``."""

    def __init__(
        self,
        controller: Controller,
        field_path: str,
        descriptor: SliderDescriptor,
    ) -> None:
        self.controller = controller
        self.field_path = field_path
        self.descriptor = descriptor

    def build(self, parent: Any) -> None:
        import tkinter as tk

        current_value = self.controller._get_param_value(self.field_path)
        current_index = self.descriptor.values.index(current_value)

        frame = tk.Frame(parent, bg=BG_CARD)
        label = tk.Label(frame, text=self.field_path, bg=BG_CARD, fg=FG, anchor=tk.W)
        scale = tk.Scale(
            frame,
            from_=0,
            to=len(self.descriptor.values) - 1,
            orient=tk.HORIZONTAL,
            command=self._on_drag,
            bg=BG_CARD,
            fg=FG,
            highlightthickness=0,
            troughcolor=BG_TROUGH,
        )
        scale.set(current_index)
        scale.bind("<ButtonRelease-1>", self._on_release)
        label.pack(fill=tk.X)
        scale.pack(fill=tk.X)
        frame.pack(fill=tk.X)

    def _on_drag(self, index: str) -> None:
        value = self.descriptor.values[int(float(index))]
        self.controller._handle_widget_change(
            self.field_path,
            self.descriptor,
            value,
            "drag",
        )

    def _on_release(self, event: Any) -> None:
        scale = event.widget
        value = self.descriptor.values[int(scale.get())]
        self.controller._handle_widget_change(
            self.field_path,
            self.descriptor,
            value,
            "release",
        )
