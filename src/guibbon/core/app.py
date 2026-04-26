"""
App orchestrator — non-GUI coordination of params, components, and event handling.

Design: Params-Centric Orchestration
=====================================
App maintains a single @guibbon.params instance as the source of truth.
Components (Controller, ImageViewer) register with the app and operate on the
shared params. The app orchestrates three key responsibilities:

1. Component registration and lifecycle
2. need_update cascading from child components
3. modified_descriptors collection from descriptor triggered_callbacks

The app layer is completely framework-agnostic: it does not import tkinter,
PyQt, nicegui, or any other framework. Components own all framework coupling.

Example:

    @guibbon.params
    class Params:
        size: int = SliderDescriptor(values=range(1, 11), default=5)

    params = Params()
    app = App(params)

    # Components register themselves
    app.add_component(controller)
    app.add_component(image_viewer)

    # App orchestrates: read need_update from components
    while app.is_running():
        if app.need_update:
            modified = app.collect_modified_descriptors()
            on_change(params, modified)
            app.clear_modified_descriptors()
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HasNeedUpdate(Protocol):
    """Component with need_update property."""

    @property
    def need_update(self) -> bool:
        """True if component needs update."""
        ...

    @need_update.setter
    def need_update(self, value: bool) -> None:
        """Set need_update flag."""
        ...


class App:
    """Framework-agnostic app orchestrator.

    Maintains a @guibbon.params instance and coordinates multiple components
    (Controller, ImageViewer, etc.). Orchestrates event flow via need_update
    cascading and modified_descriptors collection.

    Attributes:
        params: The @guibbon.params decorated dataclass instance.
    """

    def __init__(self, params: Any) -> None:
        """Initialize App with params instance.

        Args:
            params: Must be a @guibbon.params decorated dataclass.

        Raises:
            ValueError: If params does not have __guibbon_descriptors__ attribute.
        """
        if not hasattr(params, "__guibbon_descriptors__"):
            raise ValueError(
                f"params must be decorated with @guibbon.params; got {type(params).__name__}"
            )
        self.params = params
        self._components: list[Any] = []
        self._running = True

    def add_component(self, component: Any) -> None:
        """Register a component with the app.

        Args:
            component: Any object (Controller, ImageViewer, custom component).
                      Can optionally have a need_update property for cascading.
        """
        if component is not None:
            self._components.append(component)

    @property
    def need_update(self) -> bool:
        """Cascade need_update from all registered components.

        Returns:
            True if ANY component has need_update=True.
        """
        return any(
            getattr(component, "need_update", False) for component in self._components
        )

    @need_update.setter
    def need_update(self, value: bool) -> None:
        """Set need_update on all components that support it.

        Args:
            value: Boolean flag to propagate to all components.
        """
        for component in self._components:
            if hasattr(component, "need_update"):
                component.need_update = value

    def is_running(self) -> bool:
        """Check if app is running.

        Returns:
            True if app is still running (not stopped).
        """
        return self._running

    def wait(self, timeout_ms: int = 0) -> bool:
        """Wait for app event (blocking).

        Args:
            timeout_ms: Timeout in milliseconds (0 = infinite). Phase 1 placeholder.

        Returns:
            True if event occurred; False if timeout.
        """
        # Phase 1: non-GUI skeleton; Phase 2 will integrate with event loop
        return self._running

    def collect_modified_descriptors(self) -> list[str]:
        """Collect triggered_callbacks from all descriptors in params.

        Walks the params class descriptors, reads each descriptor's
        triggered_callbacks list, and returns a flat list of
        "field.callback_type" strings.

        Returns:
            List of "field.callback_type" strings (e.g., ["size.on_drag"]).
        """
        modified: list[str] = []

        # Get all descriptors from params class
        descriptors = getattr(self.params.__class__, "__guibbon_descriptors__", {})

        for field_name, descriptor in descriptors.items():
            # Read descriptor's triggered_callbacks
            triggered = getattr(descriptor, "triggered_callbacks", [])
            for callback_type in triggered:
                modified.append(f"{field_name}.{callback_type}")

        return modified

    def clear_modified_descriptors(self) -> None:
        """Clear triggered_callbacks from all descriptors.

        Should be called after processing modified_descriptors in the
        main loop to reset state for the next event cycle.
        """
        descriptors = getattr(self.params.__class__, "__guibbon_descriptors__", {})

        for descriptor in descriptors.values():
            if hasattr(descriptor, "triggered_callbacks"):
                descriptor.triggered_callbacks.clear()

    def stop(self) -> None:
        """Stop the app."""
        self._running = False
