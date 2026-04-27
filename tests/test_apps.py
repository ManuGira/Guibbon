"""Tests for Phase 3 app base classes: ControllerAppBase, InteractiveImageAppBase,
and ImageViewer.wait().

Design: test ALL non-GUI orchestration logic (params wiring, component
registration, abstract method enforcement, refresh-rate maths).  Tkinter
rendering and mainloop are not exercised here.
"""

from __future__ import annotations

import pytest
import numpy as np

import guibbon
from guibbon import SliderDescriptor, RadioDescriptor
from guibbon.apps import ControllerAppBase, InteractiveImageAppBase


# ---------------------------------------------------------------------------
# Concrete fixture subclasses
# ---------------------------------------------------------------------------


class _ConcreteControllerApp(ControllerAppBase):
    @guibbon.params
    class Params:
        sigma: float = SliderDescriptor(values=[0.1, 1.0, 5.0], default=1.0)
        mode: str = RadioDescriptor(options=["a", "b"], default="a")

    def on_change(self, params, modified_descriptors):
        pass


class _ConcreteImageApp(InteractiveImageAppBase):
    @guibbon.params
    class Params:
        k: int = SliderDescriptor(values=list(range(1, 10, 2)), default=3)

    def on_change(self, params, modified_descriptors):
        return np.zeros((100, 100, 3), dtype=np.uint8)


# ===========================================================================
# ControllerAppBase
# ===========================================================================


class TestControllerAppBaseAbstract:
    def test_cannot_instantiate_without_on_change(self):
        """Subclass that defines Params but not on_change raises TypeError."""

        class BadApp(ControllerAppBase):
            @guibbon.params
            class Params:
                x: int = SliderDescriptor(values=[1, 2, 3], default=1)

        with pytest.raises(TypeError):
            BadApp()

    def test_cannot_instantiate_without_params_class(self):
        """Subclass that implements on_change but has no Params raises AttributeError."""

        class BadApp(ControllerAppBase):
            def on_change(self, params, modified_descriptors):
                pass

        with pytest.raises(AttributeError):
            BadApp()

    def test_cannot_instantiate_base_directly(self):
        with pytest.raises(TypeError):
            ControllerAppBase()  # type: ignore[abstract]


class TestControllerAppBaseWiring:
    def test_params_instantiated(self):
        app = _ConcreteControllerApp()
        assert hasattr(app.params, "__guibbon_descriptors__")

    def test_params_has_correct_fields(self):
        app = _ConcreteControllerApp()
        assert hasattr(app.params, "sigma")
        assert hasattr(app.params, "mode")

    def test_controller_created(self):
        from guibbon.controller import Controller

        app = _ConcreteControllerApp()
        assert isinstance(app._controller, Controller)

    def test_app_orchestrator_created(self):
        from guibbon.core.app import App

        app = _ConcreteControllerApp()
        assert isinstance(app._app, App)

    def test_app_holds_correct_params(self):
        app = _ConcreteControllerApp()
        assert app._app.params is app.params

    def test_controller_registered_with_app(self):
        app = _ConcreteControllerApp()
        assert app._controller in app._app._components

    def test_need_update_cascades_through_app(self):
        app = _ConcreteControllerApp()
        assert not app._app.need_update
        app._controller._need_update = True
        assert app._app.need_update


class TestControllerAppBaseRefreshRate:
    def test_default_refresh_ms(self):
        app = _ConcreteControllerApp()
        assert app._refresh_ms == 1000 // 30

    def test_custom_refresh_rate(self):
        app = _ConcreteControllerApp(refresh_rate=10)
        assert app._refresh_ms == 100

    def test_high_refresh_rate_clamped_to_one(self):
        app = _ConcreteControllerApp(refresh_rate=100_000)
        assert app._refresh_ms >= 1

    def test_custom_title_stored(self):
        app = _ConcreteControllerApp(title="My Tuner")
        assert app._title == "My Tuner"


class TestControllerAppBaseExports:
    def test_exported_from_guibbon(self):
        from guibbon import ControllerAppBase as CAB

        assert CAB is ControllerAppBase

    def test_exported_from_guibbon_apps(self):
        from guibbon.apps import ControllerAppBase as CAB

        assert CAB is ControllerAppBase


# ===========================================================================
# InteractiveImageAppBase
# ===========================================================================


class TestInteractiveImageAppBaseAbstract:
    def test_cannot_instantiate_without_on_change(self):
        class BadApp(InteractiveImageAppBase):
            @guibbon.params
            class Params:
                x: int = SliderDescriptor(values=[1, 2, 3], default=1)

        with pytest.raises(TypeError):
            BadApp()

    def test_cannot_instantiate_without_params_class(self):
        class BadApp(InteractiveImageAppBase):
            def on_change(self, params, modified_descriptors):
                return None

        with pytest.raises(AttributeError):
            BadApp()

    def test_cannot_instantiate_base_directly(self):
        with pytest.raises(TypeError):
            InteractiveImageAppBase()  # type: ignore[abstract]


class TestInteractiveImageAppBaseWiring:
    def test_params_instantiated(self):
        app = _ConcreteImageApp()
        assert hasattr(app.params, "__guibbon_descriptors__")

    def test_controller_created(self):
        from guibbon.controller import Controller

        app = _ConcreteImageApp()
        assert isinstance(app._controller, Controller)

    def test_viewer_created(self):
        from guibbon import ImageViewer

        app = _ConcreteImageApp()
        assert isinstance(app._viewer, ImageViewer)

    def test_app_holds_correct_params(self):
        app = _ConcreteImageApp()
        assert app._app.params is app.params

    def test_controller_registered_with_app(self):
        app = _ConcreteImageApp()
        assert app._controller in app._app._components

    def test_viewer_registered_with_app(self):
        app = _ConcreteImageApp()
        assert app._viewer in app._app._components

    def test_need_update_cascades_from_controller(self):
        app = _ConcreteImageApp()
        app._controller._need_update = True
        assert app._app.need_update

    def test_need_update_cascades_from_viewer(self):
        app = _ConcreteImageApp()
        app._viewer._need_update = True
        assert app._app.need_update


class TestInteractiveImageAppBaseViewerConfig:
    def test_default_viewer_dimensions(self):
        app = _ConcreteImageApp()
        assert app._viewer._canvas_h == 720
        assert app._viewer._canvas_w == 720

    def test_custom_viewer_dimensions(self):
        app = _ConcreteImageApp(viewer_height=480, viewer_width=640)
        assert app._viewer._canvas_h == 480
        assert app._viewer._canvas_w == 640

    def test_default_viewer_mode(self):
        app = _ConcreteImageApp()
        assert app._viewer._mode == "fit"

    def test_custom_viewer_mode(self):
        app = _ConcreteImageApp(viewer_mode="100")
        assert app._viewer._mode == "100"


class TestInteractiveImageAppBaseRefreshRate:
    def test_default_refresh_ms(self):
        app = _ConcreteImageApp()
        assert app._refresh_ms == 1000 // 30

    def test_custom_refresh_rate(self):
        app = _ConcreteImageApp(refresh_rate=60)
        assert app._refresh_ms == 1000 // 60


class TestInteractiveImageAppBaseExports:
    def test_exported_from_guibbon(self):
        from guibbon import InteractiveImageAppBase as IIAB

        assert IIAB is InteractiveImageAppBase

    def test_exported_from_guibbon_apps(self):
        from guibbon.apps import InteractiveImageAppBase as IIAB

        assert IIAB is InteractiveImageAppBase


# ===========================================================================
# ImageViewer.wait() — Pattern 1
# ===========================================================================


class TestImageViewerWait:
    def test_wait_raises_if_already_built(self):
        """wait() must raise RuntimeError when viewer is already embedded."""
        from guibbon import ImageViewer

        viewer = ImageViewer()
        viewer._canvas = object()  # simulate already-built state
        with pytest.raises(RuntimeError, match="build"):
            viewer.wait(0)

    def test_wait_raises_with_message_about_build(self):
        from guibbon import ImageViewer

        viewer = ImageViewer()
        viewer._canvas = object()
        with pytest.raises(RuntimeError, match="build\\(\\)"):
            viewer.wait(0)
