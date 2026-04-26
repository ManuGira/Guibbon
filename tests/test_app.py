"""Tests for app.py — App orchestrator.

Tests cover:
  - App initialization with @guibbon.params
  - Component registration (add_component)
  - is_running() lifecycle
  - need_update cascading from components
  - modified_descriptors collection from descriptors
  - Clearing triggered_callbacks after collection
  - Validation that params must be @guibbon.params decorated
  - Edge cases (None params, empty components, etc.)
"""

from dataclasses import field

import pytest

import guibbon
from guibbon.controller import SliderDescriptor
from guibbon.core.app import App


# ---------------------------------------------------------------------------
# Test Helpers — Mock components and params classes
# ---------------------------------------------------------------------------

class MockComponent:
    """Simulates a component with need_update property."""

    def __init__(self, need_update: bool = False) -> None:
        self._need_update = need_update

    @property
    def need_update(self) -> bool:
        return self._need_update

    @need_update.setter
    def need_update(self, value: bool) -> None:
        self._need_update = value


class MockComponentNoNeedUpdate:
    """Component without need_update property."""

    pass


# ---------------------------------------------------------------------------
# Test: App Initialization
# ---------------------------------------------------------------------------

class TestAppInitialization:
    """App requires @guibbon.params decorated params."""

    def test_app_init_with_valid_params(self):
        """App initializes with @guibbon.params decorated params."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        params = Params()
        app = App(params)
        assert app.params is params

    def test_app_init_rejects_non_params_object(self):
        """App raises ValueError if params lacks __guibbon_descriptors__."""

        class NotParams:
            pass

        with pytest.raises(ValueError, match="must be decorated with @guibbon.params"):
            App(NotParams())

    def test_app_init_requires_guibbon_descriptors_attribute(self):
        """App checks for __guibbon_descriptors__ marker."""

        class FakeParams:
            pass

        with pytest.raises(ValueError):
            App(FakeParams())


# ---------------------------------------------------------------------------
# Test: Component Registration
# ---------------------------------------------------------------------------

class TestComponentRegistration:
    """add_component() manages component lifecycle."""

    def test_add_single_component(self):
        """add_component() registers a component."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        component = MockComponent()
        app.add_component(component)
        # Component is stored internally (no public list, but next tests verify)

    def test_add_multiple_components(self):
        """add_component() can register multiple components."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        comp1 = MockComponent()
        comp2 = MockComponent()
        app.add_component(comp1)
        app.add_component(comp2)
        # Both should be stored and cascading should include both

    def test_add_none_component(self):
        """add_component(None) is handled gracefully."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        app.add_component(None)  # Should not raise
        assert app.is_running()

    def test_add_component_without_need_update(self):
        """add_component() accepts components without need_update property."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        comp = MockComponentNoNeedUpdate()
        app.add_component(comp)  # Should not raise


# ---------------------------------------------------------------------------
# Test: is_running() Lifecycle
# ---------------------------------------------------------------------------

class TestIsRunning:
    """is_running() reflects app state."""

    def test_is_running_default_true(self):
        """is_running() returns True on initialization."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        assert app.is_running() is True

    def test_is_running_after_stop(self):
        """is_running() returns False after stop()."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        app.stop()
        assert app.is_running() is False


# ---------------------------------------------------------------------------
# Test: need_update Cascading
# ---------------------------------------------------------------------------

class TestNeedUpdateCascading:
    """need_update property cascades from components."""

    def test_need_update_default_false(self):
        """need_update is False when no components added."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        assert app.need_update is False

    def test_need_update_single_component_true(self):
        """need_update is True if one component has need_update=True."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        comp = MockComponent(need_update=True)
        app.add_component(comp)
        assert app.need_update is True

    def test_need_update_single_component_false(self):
        """need_update is False if one component has need_update=False."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        comp = MockComponent(need_update=False)
        app.add_component(comp)
        assert app.need_update is False

    def test_need_update_multiple_components_or_logic(self):
        """need_update ORs multiple component flags."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        app.add_component(MockComponent(need_update=False))
        app.add_component(MockComponent(need_update=True))
        app.add_component(MockComponent(need_update=False))
        assert app.need_update is True

    def test_need_update_multiple_components_all_false(self):
        """need_update is False if all components are False."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        app.add_component(MockComponent(need_update=False))
        app.add_component(MockComponent(need_update=False))
        assert app.need_update is False

    def test_need_update_ignores_components_without_property(self):
        """need_update ignores components without need_update property."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        app.add_component(MockComponentNoNeedUpdate())
        app.add_component(MockComponent(need_update=True))
        assert app.need_update is True

    def test_need_update_setter_propagates_to_all_components(self):
        """Setting need_update propagates to all components that support it."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        comp1 = MockComponent(need_update=False)
        comp2 = MockComponent(need_update=False)
        app.add_component(comp1)
        app.add_component(comp2)

        app.need_update = True

        assert comp1.need_update is True
        assert comp2.need_update is True
        assert app.need_update is True

    def test_need_update_setter_ignores_components_without_property(self):
        """Setting need_update skips components without the property."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        app.add_component(MockComponentNoNeedUpdate())
        app.need_update = True  # Should not raise


# ---------------------------------------------------------------------------
# Test: Modified Descriptors Collection
# ---------------------------------------------------------------------------

class TestModifiedDescriptorsCollection:
    """collect_modified_descriptors() gathers triggered callbacks."""

    def test_collect_modified_descriptors_empty(self):
        """collect_modified_descriptors() returns empty list when no callbacks fired."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        modified = app.collect_modified_descriptors()
        assert modified == []

    def test_collect_modified_descriptors_single_callback(self):
        """collect_modified_descriptors() includes single triggered callback."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)

        app = App(Params())
        # Manually trigger a callback (simulate widget interaction)
        size_descriptor = Params.__guibbon_descriptors__["size"]
        size_descriptor.triggered_callbacks.append("on_drag")

        modified = app.collect_modified_descriptors()
        assert "size.on_drag" in modified

    def test_collect_modified_descriptors_multiple_callbacks_same_field(self):
        """collect_modified_descriptors() includes multiple callbacks from same field."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(
                values=range(1, 11), default=5, on_drag=True, on_release=True
            )

        app = App(Params())
        size_descriptor = Params.__guibbon_descriptors__["size"]
        size_descriptor.triggered_callbacks.extend(["on_drag", "on_release"])

        modified = app.collect_modified_descriptors()
        assert "size.on_drag" in modified
        assert "size.on_release" in modified

    def test_collect_modified_descriptors_multiple_fields(self):
        """collect_modified_descriptors() includes callbacks from multiple fields."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(
                values=range(1, 11), default=5, on_drag=True
            )
            sigma: float = SliderDescriptor(values=[0.1, 1.0, 5.0], default=1.0, on_release=True)

        app = App(Params())
        Params.__guibbon_descriptors__["size"].triggered_callbacks.append("on_drag")
        Params.__guibbon_descriptors__["sigma"].triggered_callbacks.append("on_release")

        modified = app.collect_modified_descriptors()
        assert "size.on_drag" in modified
        assert "sigma.on_release" in modified

    def test_collect_modified_descriptors_returns_new_list_each_time(self):
        """collect_modified_descriptors() returns a new list each call."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)

        app = App(Params())
        Params.__guibbon_descriptors__["size"].triggered_callbacks.append("on_drag")

        list1 = app.collect_modified_descriptors()
        list2 = app.collect_modified_descriptors()
        assert list1 == list2
        assert list1 is not list2  # Different list objects

    def test_collect_modified_descriptors_recurses_into_nested_params(self):
        """collect_modified_descriptors() includes nested dotted paths."""

        @guibbon.params
        class Resolution:
            width: int = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)

        @guibbon.params
        class Params:
            resolution: Resolution = field(default_factory=Resolution)

        app = App(Params())
        Resolution.__guibbon_descriptors__["width"].triggered_callbacks.append("on_drag")

        modified = app.collect_modified_descriptors()

        assert modified == ["resolution.width.on_drag"]


# ---------------------------------------------------------------------------
# Test: Clear Modified Descriptors
# ---------------------------------------------------------------------------

class TestClearModifiedDescriptors:
    """clear_modified_descriptors() resets triggered_callbacks."""

    def test_clear_modified_descriptors_empties_triggered_callbacks(self):
        """clear_modified_descriptors() clears all descriptor triggered_callbacks."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)

        app = App(Params())
        Params.__guibbon_descriptors__["size"].triggered_callbacks.append("on_drag")

        # Before clear
        modified_before = app.collect_modified_descriptors()
        assert len(modified_before) > 0

        app.clear_modified_descriptors()

        # After clear
        modified_after = app.collect_modified_descriptors()
        assert modified_after == []

    def test_clear_modified_descriptors_multiple_fields(self):
        """clear_modified_descriptors() clears all fields."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(
                values=range(1, 11), default=5, on_drag=True
            )
            sigma: float = SliderDescriptor(values=[0.1, 1.0, 5.0], default=1.0, on_release=True)

        app = App(Params())
        Params.__guibbon_descriptors__["size"].triggered_callbacks.append("on_drag")
        Params.__guibbon_descriptors__["sigma"].triggered_callbacks.append("on_release")

        app.clear_modified_descriptors()

        assert Params.__guibbon_descriptors__["size"].triggered_callbacks == []
        assert Params.__guibbon_descriptors__["sigma"].triggered_callbacks == []

    def test_clear_modified_descriptors_recurses_into_nested_params(self):
        """clear_modified_descriptors() clears nested descriptor callbacks."""

        @guibbon.params
        class Resolution:
            width: int = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)

        @guibbon.params
        class Params:
            resolution: Resolution = field(default_factory=Resolution)

        app = App(Params())
        Resolution.__guibbon_descriptors__["width"].triggered_callbacks.append("on_drag")

        app.clear_modified_descriptors()

        assert Resolution.__guibbon_descriptors__["width"].triggered_callbacks == []


# ---------------------------------------------------------------------------
# Test: wait() Method
# ---------------------------------------------------------------------------

class TestWait:
    """wait() is a Phase 1 placeholder."""

    def test_wait_returns_true_when_running(self):
        """wait() returns True if app is running."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        assert app.wait() is True
        assert app.wait(timeout_ms=100) is True

    def test_wait_returns_false_when_stopped(self):
        """wait() returns False if app is stopped (Phase 1 placeholder)."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        app = App(Params())
        app.stop()
        # Phase 1: wait still returns based on _running flag
        assert app.wait() is False


# ---------------------------------------------------------------------------
# Test: Integration Cycle
# ---------------------------------------------------------------------------

class TestIntegrationCycle:
    """Full event cycle: trigger → collect → clear."""

    def test_full_event_cycle(self):
        """App handles a complete event: trigger, collect, clear."""

        @guibbon.params
        class Params:
            size: int = SliderDescriptor(
                values=range(1, 11), default=5, on_drag=True, on_release=True
            )

        app = App(Params())

        # Step 1: Simulate widget interaction (trigger callbacks)
        size_descriptor = Params.__guibbon_descriptors__["size"]
        size_descriptor.triggered_callbacks.append("on_drag")

        # Step 2: Collect what was triggered
        modified = app.collect_modified_descriptors()
        assert "size.on_drag" in modified

        # Step 3: App clears for next cycle
        app.clear_modified_descriptors()
        assert app.collect_modified_descriptors() == []

        # Step 4: Next interaction
        size_descriptor.triggered_callbacks.append("on_release")
        modified = app.collect_modified_descriptors()
        assert "size.on_release" in modified
