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

from ._theme import BG_CARD, BG_PANEL
from .radio import RadioDescriptor
from .slider import SliderDescriptor
from .tk_radio_widget import _TkRadioWidget
from .tk_slider_widget import _TkSliderWidget


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

    def build(self, parent: Any, width: int = 360, expand: bool = False) -> None:
        """Build widgets for all visible supported descriptors.

        Each descriptor is embedded in its own "card" frame (slightly darker
        background, small inner padding) separated by a 4-pixel vertical gap.

        Args:
            parent:  Tk container to embed the control panel in.
            width:   Fixed pixel width of the control panel (default 360).
            expand:  If True the panel expands to fill all available vertical
                     space (use when the controller is the only widget in the
                     window).  Default False (panel fills the height offered by
                     sibling widgets such as an ImageViewer canvas).
        """
        import tkinter as tk

        container = tk.Frame(parent, bg=BG_PANEL)
        # Enforce minimum width via a hidden spacer — works whether or not
        # there are sibling widgets providing the window height.  This avoids
        # pack_propagate(False) which suppresses height propagation and makes
        # the panel invisible when there is no sibling (expand=True case).
        tk.Frame(container, width=width, height=0, bg=BG_PANEL).pack()
        container.pack(side=tk.LEFT, fill=tk.BOTH if expand else tk.Y, expand=expand)

        self._built_widgets = []
        for field_path, descriptor in self._descriptors.items():
            if not descriptor.is_visible:
                continue
            widget = self._build_descriptor_widget(field_path, descriptor)
            if widget is None:
                continue
            card = tk.Frame(
                container,
                bg=BG_CARD,
                padx=6,
                pady=6,
            )
            card.pack(fill=tk.X, padx=4, pady=(4, 0))
            widget.build(card)
            self._built_widgets.append(widget)

        # Bottom spacer so the last card has a gap below it, matching the top gap.
        tk.Frame(container, height=4, bg=BG_PANEL).pack()

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