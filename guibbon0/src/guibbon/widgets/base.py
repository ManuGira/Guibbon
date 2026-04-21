"""Common widget interfaces and base classes for Guibbon widgets."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable
import tkinter as tk


@runtime_checkable
class BuildableWidget(Protocol):
    """Protocol describing widgets that can populate a Tk frame."""

    def build(self, parent: tk.Frame) -> None:
        """Populate *parent* with this widget's controls."""
        ...


class BaseWidget(ABC):
    """Optional convenience base class for widgets that render into Tk frames."""

    def __init__(self, *, widget_color: Any | None = None) -> None:
        self.widget_color = widget_color

    @abstractmethod
    def build(self, parent: tk.Frame) -> None:
        """Populate *parent* with concrete widget content."""
        raise NotImplementedError

