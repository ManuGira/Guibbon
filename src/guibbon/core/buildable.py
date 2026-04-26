"""
Framework-agnostic BuildableWidget protocol.

Design: Zero Framework Coupling
================================
BuildableWidget is a structural Protocol (PEP 544).  Any class that implements
``build(self, parent: Any) -> None`` satisfies it — no explicit inheritance
needed, though explicit subclassing is fine and improves IDE support.

The ``parent`` argument is purposely typed as ``Any``: each framework passes a
different container type (tk.Frame, a nicegui element, a QWidget, …).  The
protocol never imports any of those frameworks.

Concrete widget classes own all framework-specific code; this module stays
completely dependency-free.

Examples:

    # Tkinter
    class MySlider(BuildableWidget):
        def build(self, parent: Any) -> None:
            import tkinter as tk
            scale = tk.Scale(parent, from_=1, to=10)
            scale.pack()

    # nicegui
    class MySlider(BuildableWidget):
        def build(self, parent: Any) -> None:
            from nicegui import ui
            with parent or ui.row():
                ui.slider(min=1, max=10)

    # PySide6
    class MySlider(BuildableWidget):
        def build(self, parent: Any) -> None:
            from PySide6.QtWidgets import QVBoxLayout, QSlider
            from PySide6.QtCore import Qt
            layout = QVBoxLayout(parent)
            slider = QSlider(Qt.Horizontal)
            layout.addWidget(slider)
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class BuildableWidget(Protocol):
    """Framework-agnostic widget building protocol.

    Works with ANY framework: Tkinter, nicegui, PySide6, etc.

    Any class that exposes ``build(self, parent: Any) -> None`` satisfies this
    protocol structurally, without needing to subclass ``BuildableWidget``.

    Examples:

        # Tkinter
        class MySlider(BuildableWidget):
            def build(self, parent: Any) -> None:
                scale = tk.Scale(parent, from_=1, to=10)
                scale.pack()

        # nicegui
        class MySlider(BuildableWidget):
            def build(self, parent: Any) -> None:
                with parent or ui.row():
                    ui.slider(min=1, max=10)

        # PySide6
        class MySlider(BuildableWidget):
            def build(self, parent: Any) -> None:
                layout = QVBoxLayout(parent)
                slider = QSlider(Qt.Horizontal)
                layout.addWidget(slider)
    """

    def build(self, parent: Any) -> None:
        """Build widget in parent context (framework-specific).

        Args:
            parent: Any framework-specific container (tk.Frame, nicegui
                    container, QWidget, etc.)
        """
        ...
