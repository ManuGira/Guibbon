"""Pattern 3: InteractiveImageAppBase — parameters + image viewer.

Subclass, define a Params inner class (decorated with ``@guibbon.params``),
and implement :meth:`on_change` returning the image to display.
"""

from __future__ import annotations

import abc
from typing import Any

import numpy as np

from guibbon.controller import Controller
from guibbon.core.app import App
from guibbon.image_viewer import ImageViewer


class InteractiveImageAppBase(abc.ABC):
    """Base class for interactive image apps — parameters + image viewer (Pattern 3).

    Subclasses must:

    1. Define an inner ``Params`` class decorated with ``@guibbon.params``.
    2. Implement :meth:`on_change`, returning the BGR image to display.

    Example::

        import guibbon
        from guibbon import SliderDescriptor
        from guibbon.apps import InteractiveImageAppBase

        class MyFilterApp(InteractiveImageAppBase):
            @guibbon.params
            class Params:
                k: int = SliderDescriptor(values=list(range(1, 12, 2)), default=5)

            def on_change(self, params, modified_descriptors):
                return apply_filter(image, params.k)

        MyFilterApp(refresh_rate=30).run()

    Args:
        refresh_rate: Target UI refresh rate in Hz (default 30).
        title:        Window title string.
        viewer_height: ImageViewer canvas height in pixels (default 720).
        viewer_width:  ImageViewer canvas width in pixels (default 720).
        viewer_mode:   Initial zoom mode — ``"fit"``, ``"fill"``, or ``"100"``
                       (default ``"fit"``).
    """

    def __init__(
        self,
        refresh_rate: int = 30,
        title: str = "Guibbon",
        viewer_height: int = 720,
        viewer_width: int = 720,
        viewer_mode: str = "fit",
    ) -> None:
        params_cls = getattr(type(self), "Params")  # AttributeError if not defined by subclass
        self.params = params_cls()
        self._app = App(self.params)
        self._controller = Controller(self.params)
        self._viewer = ImageViewer(height=viewer_height, width=viewer_width, mode=viewer_mode)
        self._app.add_component(self._controller)
        self._app.add_component(self._viewer)
        self._refresh_ms = max(1, 1000 // refresh_rate)
        self._title = title

    @abc.abstractmethod
    def on_change(
        self, params: Any, modified_descriptors: list[str]
    ) -> np.ndarray | None:
        """Called once on startup and again whenever any widget changes.

        Args:
            params:               The live ``@guibbon.params`` instance.
            modified_descriptors: List of ``"field.callback_type"`` strings
                                  (empty on the initial call).

        Returns:
            BGR ``uint8`` numpy array to display, or ``None`` to keep the
            current image unchanged.
        """

    def run(self) -> None:
        """Build the Tk window (controller panel + image canvas) and run.

        Blocks until the window is closed.
        """
        import tkinter as tk

        root = tk.Tk()
        root.title(self._title)
        root.resizable(False, False)

        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._controller.build(root)
        self._viewer.build(right_frame)

        initial_img = self.on_change(self.params, [])
        if initial_img is not None:
            self._viewer.set_image(initial_img)

        def _refresh() -> None:
            if self._app.need_update:
                modified = self._app.collect_modified_descriptors()
                self._app.clear_modified_descriptors()
                self._app.need_update = False
                result = self.on_change(self.params, modified)
                if result is not None:
                    self._viewer.set_image(result)
            root.after(self._refresh_ms, _refresh)

        root.after(self._refresh_ms, _refresh)
        root.mainloop()
