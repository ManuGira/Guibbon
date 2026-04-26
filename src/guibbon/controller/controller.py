"""Controller component: parameter controls for buildable descriptors.

Design: Descriptor Routing + Widget Assembly
============================================
Controller owns the control-side descriptors (sliders, radio buttons, custom
buildable widgets) for a single ``@guibbon.params`` instance.

Responsibilities:
  1. Discover supported descriptors from the params tree, including nested
     ``@guibbon.params`` objects.
  2. Track local ``need_update`` state for the app orchestrator.
  3. Build widget instances for supported descriptors.
  4. Update params values and descriptor callback state when widgets fire.

The controller module may use Tkinter for default widgets, but tests exercise
the non-GUI orchestration logic and monkeypatch build helpers when needed.
"""

from __future__ import annotations

from dataclasses import is_dataclass
import inspect
from typing import Any

from guibbon.core.buildable import BuildableWidget
from guibbon.core.descriptor import BuildableDescriptor

from .radio import RadioDescriptor
from .slider import SliderDescriptor


class Controller:
    """Parameter control component for buildable descriptors.

    Args:
        params: ``@guibbon.params`` decorated dataclass instance.
    """

    def __init__(self, params: Any) -> None:
        if not hasattr(params, "__guibbon_descriptors__"):
            raise ValueError(
                f"params must be decorated with @guibbon.params; got {type(params).__name__}"
            )
        self.params = params
        self._need_update = False
        self._descriptors: dict[str, BuildableDescriptor] = {}
        self._built_widgets: list[BuildableWidget] = []
        self._collect_descriptors(params)

    @property
    def need_update(self) -> bool:
        """Whether any widget interaction requires an app refresh."""
        return self._need_update

    @need_update.setter
    def need_update(self, value: bool) -> None:
        self._need_update = value

    def add_descriptor(self, descriptor: BuildableDescriptor) -> None:
        """Register an extra buildable descriptor.

        Extra descriptors are assigned synthetic field names because they do not
        originate from the params tree.
        """
        field_path = f"_extra_{len(self._descriptors)}"
        self._descriptors[field_path] = descriptor

    def build(self, parent: Any) -> None:
        """Build widgets for all visible supported descriptors."""
        self._built_widgets = []
        for field_path, descriptor in self._descriptors.items():
            if not descriptor.is_visible:
                continue
            widget = self._build_descriptor_widget(field_path, descriptor)
            if widget is None:
                continue
            widget.build(parent)
            self._built_widgets.append(widget)

    def _build_descriptor_widget(
        self,
        field_path: str,
        descriptor: BuildableDescriptor,
    ) -> BuildableWidget | None:
        if descriptor.widget_class is not None:
            return self._instantiate_custom_widget(
                descriptor.widget_class,
                field_path,
                descriptor,
            )
        if isinstance(descriptor, SliderDescriptor):
            return _TkSliderWidget(self, field_path, descriptor)
        if isinstance(descriptor, RadioDescriptor):
            return _TkRadioWidget(self, field_path, descriptor)
        return None

    def _instantiate_custom_widget(
        self,
        widget_class: type,
        field_path: str,
        descriptor: BuildableDescriptor,
    ) -> BuildableWidget:
        signature = inspect.signature(widget_class)
        kwargs: dict[str, Any] = {}
        for name in signature.parameters:
            if name == "params":
                kwargs[name] = self.params
            elif name == "field_path":
                kwargs[name] = field_path
            elif name == "descriptor":
                kwargs[name] = descriptor
            elif name == "controller":
                kwargs[name] = self
        widget = widget_class(**kwargs)
        return widget

    def _collect_descriptors(self, instance: Any, prefix: str = "") -> None:
        descriptors = getattr(instance.__class__, "__guibbon_descriptors__", {})
        for field_name, descriptor in descriptors.items():
            field_path = f"{prefix}.{field_name}" if prefix else field_name
            if isinstance(descriptor, BuildableDescriptor):
                self._descriptors[field_path] = descriptor

        if not is_dataclass(instance):
            return

        for field_name in getattr(instance.__class__, "__annotations__", {}):
            value = getattr(instance, field_name, None)
            if (
                value is not None
                and is_dataclass(value)
                and hasattr(value.__class__, "__guibbon_descriptors__")
            ):
                field_path = f"{prefix}.{field_name}" if prefix else field_name
                self._collect_descriptors(value, field_path)

    def _get_param_value(self, field_path: str) -> Any:
        current = self.params
        for part in field_path.split("."):
            current = getattr(current, part)
        return current

    def _set_param_value(self, field_path: str, value: Any) -> None:
        parts = field_path.split(".")
        parent = self.params
        for part in parts[:-1]:
            parent = getattr(parent, part)
        setattr(parent, parts[-1], value)

    def _handle_widget_change(
        self,
        field_path: str,
        descriptor: BuildableDescriptor,
        value: Any,
        trigger_type: str,
    ) -> None:
        self._set_param_value(field_path, value)
        descriptor.on_widget_change(trigger_type)
        self._need_update = True


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

        frame = tk.Frame(parent)
        label = tk.Label(frame, text=self.field_path)
        scale = tk.Scale(
            frame,
            from_=0,
            to=len(self.descriptor.values) - 1,
            orient=tk.HORIZONTAL,
            command=self._on_drag,
        )
        scale.set(current_index)
        scale.bind("<ButtonRelease-1>", self._on_release)
        label.pack()
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

        frame = tk.Frame(parent)
        label = tk.Label(frame, text=self.field_path)
        selected = tk.StringVar(value=self.controller._get_param_value(self.field_path))
        label.pack(anchor=tk.W)
        for option in self.descriptor.options:
            button = tk.Radiobutton(
                frame,
                text=option,
                value=option,
                variable=selected,
                command=lambda chosen=option: self._on_change(chosen),
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