"""Pattern 2: ControllerAppBase — parameter-only interactive apps.

Subclass, define a Params inner class (decorated with ``@guibbon.params``),
and implement :meth:`on_change`.
"""

from __future__ import annotations

import abc
from typing import Any

from guibbon.controller import Controller
from guibbon.core.app import App


class ControllerAppBase(abc.ABC):
    """Base class for parameter-only interactive apps (Pattern 2).

    Subclasses must:

    1. Define an inner ``Params`` class decorated with ``@guibbon.params``.
    2. Implement :meth:`on_change`.

    Example::

        import guibbon
        from guibbon import SliderDescriptor
        from guibbon.apps import ControllerAppBase

        class MyApp(ControllerAppBase):
            @guibbon.params
            class Params:
                sigma: float = SliderDescriptor(values=[0.1, 1.0, 5.0], default=1.0)

            def on_change(self, params, modified_descriptors):
                print(f"sigma={params.sigma}")

        MyApp(refresh_rate=30).run()

    Args:
        refresh_rate: Target UI refresh rate in Hz (default 30).
        title:        Window title string.
    """

    def __init__(self, refresh_rate: int = 30, title: str = "Guibbon") -> None:
        params_cls = getattr(type(self), "Params")  # AttributeError if not defined by subclass
        self.params = params_cls()
        self._app = App(self.params)
        self._controller = Controller(self.params)
        self._app.add_component(self._controller)
        self._refresh_ms = max(1, 1000 // refresh_rate)
        self._title = title

    @abc.abstractmethod
    def on_change(self, params: Any, modified_descriptors: list[str]) -> None:
        """Called once on startup and again whenever any widget changes.

        Args:
            params:               The live ``@guibbon.params`` instance.
            modified_descriptors: List of ``"field.callback_type"`` strings
                                  (empty on the initial call).
        """

    def run(self) -> None:
        """Build the Tk window and enter the event loop.

        Blocks until the window is closed.
        """
        import tkinter as tk

        root = tk.Tk()
        root.title(self._title)
        self._controller.build(root, expand=True)
        self.on_change(self.params, [])

        def _refresh() -> None:
            if self._app.need_update:
                modified = self._app.collect_modified_descriptors()
                self._app.clear_modified_descriptors()
                self._app.need_update = False
                self.on_change(self.params, modified)
            root.after(self._refresh_ms, _refresh)

        root.after(self._refresh_ms, _refresh)
        root.mainloop()
