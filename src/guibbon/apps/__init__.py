"""Guibbon high-level app base classes.

Three usage patterns are provided:

* **Pattern 1** — Simple blocking image display::

      viewer = guibbon.ImageViewer()
      viewer.set_image(bgr_array)
      viewer.wait(0)  # blocks until window is closed

* **Pattern 2** — Parameter-only interactive app (:class:`ControllerAppBase`)::

      class MyApp(ControllerAppBase):
          @guibbon.params
          class Params:
              sigma: float = SliderDescriptor(values=[0.1, 1.0, 5.0], default=1.0)

          def on_change(self, params, modified_descriptors):
              print(params.sigma)

      MyApp(refresh_rate=30).run()

* **Pattern 3** — Parameters + image viewer (:class:`InteractiveImageAppBase`)::

      class MyFilterApp(InteractiveImageAppBase):
          @guibbon.params
          class Params:
              k: int = SliderDescriptor(values=list(range(1, 12, 2)), default=5)

          def on_change(self, params, modified_descriptors):
              return apply_filter(image, params.k)

      MyFilterApp(refresh_rate=30).run()
"""

from .controller_app import ControllerAppBase
from .image_app import InteractiveImageAppBase

__all__ = ["ControllerAppBase", "InteractiveImageAppBase"]
