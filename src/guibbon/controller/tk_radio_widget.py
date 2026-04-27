"""Tkinter widget adapter for ``RadioDescriptor``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._theme import BG_CARD, BG_TROUGH, FG
from .radio import RadioDescriptor

if TYPE_CHECKING:
    from .controller import Controller


class _TkRadioWidget:
    """Default Tkinter widget for ``RadioDescriptor``."""

    def __init__(
        self,
        controller: Controller,
        field_path: str,
        descriptor: RadioDescriptor,
    ) -> None:
        self.controller = controller
        self.field_path = field_path
        self.descriptor = descriptor

    def build(self, parent: Any) -> None:
        import tkinter as tk

        frame = tk.Frame(parent, bg=BG_CARD)
        label = tk.Label(frame, text=self.field_path, bg=BG_CARD, fg=FG, anchor=tk.W)
        # Store as instance attribute — a local StringVar is GC'd after build() returns,
        # which causes all radio buttons to appear deselected.
        self._selected = tk.StringVar(value=self.controller._get_param_value(self.field_path))
        label.pack(anchor=tk.W, fill=tk.X)
        for option in self.descriptor.options:
            button = tk.Radiobutton(
                frame,
                text=option,
                value=option,
                variable=self._selected,
                command=lambda chosen=option: self._on_change(chosen),
                bg=BG_CARD,
                fg=FG,
                selectcolor=BG_TROUGH,
                activebackground=BG_CARD,
                activeforeground=FG,
            )
            button.pack(anchor=tk.W)
        frame.pack(fill=tk.X)

    def _on_change(self, value: str) -> None:
        self.controller._handle_widget_change(
            self.field_path,
            self.descriptor,
            value,
            "change",
        )
