"""Tests for controller.py — Controller component assembly and event handling."""

from dataclasses import field
import sys
from typing import cast

import pytest

import guibbon
from guibbon.controller import Controller, RadioDescriptor, SliderDescriptor
from guibbon.controller.controller import _TkRadioWidget, _TkSliderWidget
from guibbon.core.descriptor import BuildableDescriptor


class _FakeWidget:
    """Custom widget used to validate controller widget instantiation."""

    def __init__(
        self,
        controller: Controller,
        params: object,
        descriptor: BuildableDescriptor,
        field_path: str,
    ) -> None:
        self.controller = controller
        self.params = params
        self.descriptor = descriptor
        self.field_path = field_path
        self.parents: list[object] = []

    def build(self, parent: object) -> None:
        self.parents.append(parent)


class _CustomDescriptor(BuildableDescriptor):
    widget_class = _FakeWidget

    def on_widget_change(self, trigger_type: str) -> None:
        if trigger_type == "custom":
            self.triggered_callbacks.append("on_custom")


class _UnsupportedDescriptor(BuildableDescriptor):
    pass


class _FakeTkWidget:
    """Minimal Tk-like widget with pack support."""

    def __init__(self, parent: object, **kwargs: object) -> None:
        self.parent = parent
        self.kwargs = kwargs
        self.pack_calls: list[dict[str, object]] = []

    def pack(self, **kwargs: object) -> None:
        self.pack_calls.append(kwargs)


class _FakeScale(_FakeTkWidget):
    """Fake Scale with bind/set/get behavior."""

    last_instance: "_FakeScale | None" = None

    def __init__(self, parent: object, **kwargs: object) -> None:
        super().__init__(parent, **kwargs)
        self.command = kwargs.get("command")
        self._value = 0
        self.bindings: dict[str, object] = {}
        _FakeScale.last_instance = self

    def set(self, value: int) -> None:
        self._value = value

    def get(self) -> int:
        return self._value

    def bind(self, event_name: str, callback: object) -> None:
        self.bindings[event_name] = callback


class _FakeStringVar:
    def __init__(self, value: object) -> None:
        self.value = value


class _FakeRadioButton(_FakeTkWidget):
    last_instances: list["_FakeRadioButton"] = []

    def __init__(self, parent: object, **kwargs: object) -> None:
        super().__init__(parent, **kwargs)
        _FakeRadioButton.last_instances.append(self)


class _FakeTkModule:
    Frame = _FakeTkWidget
    Label = _FakeTkWidget
    Scale = _FakeScale
    Radiobutton = _FakeRadioButton
    StringVar = _FakeStringVar
    HORIZONTAL = "horizontal"
    X = "x"
    W = "w"


class TestControllerInitialization:
    def test_controller_init_with_valid_params(self):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        controller = Controller(Params())

        assert controller.need_update is False
        assert list(controller._descriptors) == ["size"]

    def test_controller_rejects_non_params_object(self):
        with pytest.raises(ValueError, match="must be decorated with @guibbon.params"):
            Controller(object())


class TestDescriptorDiscovery:
    def test_collects_slider_and_radio_descriptors(self):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)
            mode: str = RadioDescriptor(options=["a", "b"], default="a")
            threshold: float = 0.5

        controller = Controller(Params())

        assert set(controller._descriptors) == {"size", "mode"}

    def test_collects_nested_descriptors_recursively(self):
        @guibbon.params
        class Resolution:
            width: int = SliderDescriptor(values=range(1, 11), default=5)

        @guibbon.params
        class Params:
            resolution: Resolution = field(default_factory=Resolution)
            mode: str = RadioDescriptor(options=["a", "b"], default="a")

        controller = Controller(Params())

        assert set(controller._descriptors) == {"mode", "resolution.width"}

    def test_add_descriptor_registers_synthetic_field_path(self):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        controller = Controller(Params())
        controller.add_descriptor(_CustomDescriptor(default=0))

        assert any(path.startswith("_extra_") for path in controller._descriptors)


class TestNeedUpdate:
    def test_need_update_setter_updates_local_flag(self):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        controller = Controller(Params())
        controller.need_update = True

        assert controller.need_update is True


class TestWidgetChangeHandling:
    def test_handle_slider_drag_updates_param_and_callbacks(self):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)

        params = Params()
        controller = Controller(params)
        descriptor = controller._descriptors["size"]

        controller._handle_widget_change("size", descriptor, 7, "drag")

        assert params.size == 7
        assert controller.need_update is True
        assert descriptor.triggered_callbacks == ["on_drag"]

    def test_handle_slider_release_updates_param_and_callbacks(self):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(
                values=range(1, 11),
                default=5,
                on_drag=False,
                on_release=True,
            )

        params = Params()
        controller = Controller(params)
        descriptor = controller._descriptors["size"]

        controller._handle_widget_change("size", descriptor, 9, "release")

        assert params.size == 9
        assert descriptor.triggered_callbacks == ["on_release"]

    def test_handle_radio_change_updates_param_and_callbacks(self):
        @guibbon.params
        class Params:
            mode: str = RadioDescriptor(options=["fast", "accurate"], default="fast")

        params = Params()
        controller = Controller(params)
        descriptor = controller._descriptors["mode"]

        controller._handle_widget_change("mode", descriptor, "accurate", "change")

        assert params.mode == "accurate"
        assert descriptor.triggered_callbacks == ["on_change"]

    def test_handle_nested_field_updates_nested_param(self):
        @guibbon.params
        class Resolution:
            width: int = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)

        @guibbon.params
        class Params:
            resolution: Resolution = field(default_factory=Resolution)

        params = Params()
        controller = Controller(params)
        descriptor = controller._descriptors["resolution.width"]

        controller._handle_widget_change("resolution.width", descriptor, 8, "drag")

        assert params.resolution.width == 8
        assert descriptor.triggered_callbacks == ["on_drag"]

    def test_get_and_set_param_value_helpers_handle_nested_paths(self):
        @guibbon.params
        class Resolution:
            width: int = SliderDescriptor(values=range(1, 11), default=5)

        @guibbon.params
        class Params:
            resolution: Resolution = field(default_factory=Resolution)

        params = Params()
        controller = Controller(params)

        assert controller._get_param_value("resolution.width") == 5

        controller._set_param_value("resolution.width", 9)

        assert controller._get_param_value("resolution.width") == 9


class TestBuild:
    def test_build_uses_default_widget_for_slider_and_radio(self, monkeypatch: pytest.MonkeyPatch):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)
            mode: str = RadioDescriptor(options=["a", "b"], default="a")

        controller = Controller(Params())
        built: list[tuple[str, object]] = []

        class _BuiltWidget:
            def __init__(self, field_path: str) -> None:
                self.field_path = field_path

            def build(self, parent: object) -> None:
                built.append((self.field_path, parent))

        def fake_build_descriptor_widget(field_path: str, descriptor: BuildableDescriptor) -> _BuiltWidget:
            return _BuiltWidget(field_path)

        monkeypatch.setattr(controller, "_build_descriptor_widget", fake_build_descriptor_widget)

        parent = object()
        controller.build(parent)

        assert built == [("size", parent), ("mode", parent)]

    def test_build_skips_invisible_descriptors(self, monkeypatch: pytest.MonkeyPatch):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        controller = Controller(Params())
        controller._descriptors["size"].is_visible = False
        called = False

        def fake_build_descriptor_widget(field_path: str, descriptor: BuildableDescriptor) -> None:
            nonlocal called
            called = True
            return None

        monkeypatch.setattr(controller, "_build_descriptor_widget", fake_build_descriptor_widget)
        controller.build(object())

        assert called is False

    def test_build_instantiates_custom_widget_class_with_context(self):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        controller = Controller(Params())
        descriptor = _CustomDescriptor(default=0)

        widget = controller._instantiate_custom_widget(
            descriptor.widget_class,
            "custom.threshold",
            descriptor,
        )

        assert isinstance(widget, _FakeWidget)
        assert widget.controller is controller
        assert widget.params is controller.params
        assert widget.descriptor is descriptor
        assert widget.field_path == "custom.threshold"

    def test_build_descriptor_widget_chooses_slider_widget(self):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        controller = Controller(Params())

        widget = controller._build_descriptor_widget("size", controller._descriptors["size"])

        assert isinstance(widget, _TkSliderWidget)

    def test_build_descriptor_widget_chooses_radio_widget(self):
        @guibbon.params
        class Params:
            mode: str = RadioDescriptor(options=["a", "b"], default="a")

        controller = Controller(Params())

        widget = controller._build_descriptor_widget("mode", controller._descriptors["mode"])

        assert isinstance(widget, _TkRadioWidget)

    def test_build_descriptor_widget_returns_none_for_unsupported_descriptor(self):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        controller = Controller(Params())
        descriptor = _UnsupportedDescriptor(default=0)

        assert controller._build_descriptor_widget("unsupported", descriptor) is None

    def test_build_skips_none_widgets(self, monkeypatch: pytest.MonkeyPatch):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        controller = Controller(Params())

        monkeypatch.setattr(controller, "_build_descriptor_widget", lambda field_path, descriptor: None)

        controller.build(object())

        assert controller._built_widgets == []


class TestTkWidgets:
    def test_slider_widget_build_creates_scale_and_binds_release(self, monkeypatch: pytest.MonkeyPatch):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=[10, 20, 30], default=20, on_drag=True)

        monkeypatch.setitem(sys.modules, "tkinter", _FakeTkModule)
        _FakeScale.last_instance = None

        controller = Controller(Params())
        descriptor = cast(SliderDescriptor, controller._descriptors["size"])
        widget = _TkSliderWidget(controller, "size", descriptor)
        widget.build(object())

        assert _FakeScale.last_instance is not None
        assert _FakeScale.last_instance.get() == 1
        assert "<ButtonRelease-1>" in _FakeScale.last_instance.bindings

    def test_slider_widget_drag_maps_index_to_descriptor_value(self):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=[10, 20, 30], default=10, on_drag=True)

        params = Params()
        controller = Controller(params)
        descriptor = cast(SliderDescriptor, controller._descriptors["size"])
        widget = _TkSliderWidget(controller, "size", descriptor)

        widget._on_drag("2")

        assert params.size == 30
        assert controller._descriptors["size"].triggered_callbacks == ["on_drag"]

    def test_slider_widget_release_uses_scale_value(self):
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=[10, 20, 30], default=10, on_release=True)

        params = Params()
        controller = Controller(params)
        descriptor = cast(SliderDescriptor, controller._descriptors["size"])
        widget = _TkSliderWidget(controller, "size", descriptor)

        class _Event:
            def __init__(self) -> None:
                self.widget = _FakeScale(object())
                self.widget.set(1)

        widget._on_release(_Event())

        assert params.size == 20
        assert controller._descriptors["size"].triggered_callbacks == ["on_release"]

    def test_radio_widget_build_creates_buttons_for_all_options(self, monkeypatch: pytest.MonkeyPatch):
        @guibbon.params
        class Params:
            mode: str = RadioDescriptor(options=["a", "b", "c"], default="a")

        monkeypatch.setitem(sys.modules, "tkinter", _FakeTkModule)
        _FakeRadioButton.last_instances = []

        controller = Controller(Params())
        descriptor = cast(RadioDescriptor, controller._descriptors["mode"])
        widget = _TkRadioWidget(controller, "mode", descriptor)
        widget.build(object())

        assert len(_FakeRadioButton.last_instances) == 3
        assert [button.kwargs["value"] for button in _FakeRadioButton.last_instances] == ["a", "b", "c"]

    def test_radio_widget_change_updates_params_and_callbacks(self):
        @guibbon.params
        class Params:
            mode: str = RadioDescriptor(options=["fast", "accurate"], default="fast")

        params = Params()
        controller = Controller(params)
        descriptor = cast(RadioDescriptor, controller._descriptors["mode"])
        widget = _TkRadioWidget(controller, "mode", descriptor)

        widget._on_change("accurate")

        assert params.mode == "accurate"
        assert controller._descriptors["mode"].triggered_callbacks == ["on_change"]


class TestPackageExports:
    def test_controller_exported_from_controller_package(self):
        from guibbon.controller import Controller as ExportedController

        assert ExportedController is Controller

    def test_controller_exported_from_root_package(self):
        assert guibbon.Controller is Controller