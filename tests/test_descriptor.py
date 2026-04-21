"""Tests for descriptor.py — Descriptor base classes and concrete types.

Tests cover:
  - Descriptor ABC enforcement (cannot instantiate directly)
  - BuildableDescriptor (widget_class, default no-op on_widget_change)
  - SliderDescriptor: metadata, on_widget_change, get_triggered_descriptors
  - RadioDescriptor: metadata, on_widget_change, get_triggered_descriptors
  - Callback flags (on_drag, on_release, on_change enable/disable)
  - triggered_callbacks accumulation and clearing
  - isVisible visibility flag
  - Invalid defaults (ValueError)
  - Integration with @guibbon.params decorator
"""

import pytest

import guibbon
from guibbon.core.descriptor import (
    BuildableDescriptor,
    Descriptor,
    RadioDescriptor,
    SliderDescriptor,
)


# ---------------------------------------------------------------------------
# Test: Descriptor ABC
# ---------------------------------------------------------------------------

class TestDescriptorABC:
    """Descriptor is abstract; cannot be instantiated directly."""

    def test_descriptor_cannot_be_instantiated(self):
        """Descriptor is ABC; direct instantiation raises TypeError."""
        with pytest.raises(TypeError):
            Descriptor(default=0)  # type: ignore[abstract]

    def test_descriptor_subclass_must_implement_on_widget_change(self):
        """Subclass without on_widget_change raises TypeError on instantiation."""
        class IncompleteDescriptor(Descriptor):
            pass  # Does not implement on_widget_change

        with pytest.raises(TypeError):
            IncompleteDescriptor(default=0)  # type: ignore[abstract]

    def test_descriptor_subclass_with_on_widget_change_is_valid(self):
        """Concrete subclass implementing on_widget_change can be instantiated."""
        class ConcreteDescriptor(Descriptor):
            def on_widget_change(self, trigger_type: str) -> None:
                pass

        desc = ConcreteDescriptor(default=42)
        assert desc.default == 42


# ---------------------------------------------------------------------------
# Test: Descriptor base attributes
# ---------------------------------------------------------------------------

class TestDescriptorBaseAttributes:
    """Test inherited attributes on all Descriptor subclasses."""

    def test_slider_descriptor_has_default(self):
        """SliderDescriptor exposes .default from Descriptor base."""
        desc = SliderDescriptor(values=range(1, 11), default=5)
        assert desc.default == 5

    def test_radio_descriptor_has_default(self):
        """RadioDescriptor exposes .default from Descriptor base."""
        desc = RadioDescriptor(options=["A", "B"], default="B")
        assert desc.default == "B"

    def test_is_visible_defaults_to_true(self):
        """isVisible is True by default for all descriptors."""
        slider = SliderDescriptor(values=range(1, 11), default=5)
        radio = RadioDescriptor(options=["A", "B"], default="A")
        assert slider.isVisible is True
        assert radio.isVisible is True

    def test_is_visible_can_be_set(self):
        """isVisible can be toggled."""
        desc = SliderDescriptor(values=range(1, 11), default=5)
        desc.isVisible = False
        assert desc.isVisible is False

    def test_triggered_callbacks_starts_empty(self):
        """triggered_callbacks is empty list on creation."""
        slider = SliderDescriptor(values=range(1, 11), default=5)
        radio = RadioDescriptor(options=["A", "B"], default="A")
        assert slider.triggered_callbacks == []
        assert radio.triggered_callbacks == []

    def test_descriptor_is_descriptor_instance(self):
        """SliderDescriptor and RadioDescriptor are Descriptor instances."""
        slider = SliderDescriptor(values=range(1, 11), default=5)
        radio = RadioDescriptor(options=["A"], default="A")
        assert isinstance(slider, Descriptor)
        assert isinstance(radio, Descriptor)

    def test_descriptor_is_buildable_descriptor_instance(self):
        """SliderDescriptor and RadioDescriptor are BuildableDescriptor instances."""
        slider = SliderDescriptor(values=range(1, 11), default=5)
        radio = RadioDescriptor(options=["A"], default="A")
        assert isinstance(slider, BuildableDescriptor)
        assert isinstance(radio, BuildableDescriptor)


# ---------------------------------------------------------------------------
# Test: BuildableDescriptor
# ---------------------------------------------------------------------------

class TestBuildableDescriptor:
    """BuildableDescriptor holds optional widget_class."""

    def test_default_widget_class_is_none(self):
        """BuildableDescriptor.widget_class is None by default."""
        assert BuildableDescriptor.widget_class is None

    def test_subclass_can_set_widget_class(self):
        """Subclass may override widget_class at class level."""
        class FakeWidget:
            pass

        class MyDescriptor(BuildableDescriptor):
            widget_class = FakeWidget

        desc = MyDescriptor(default=0)
        assert desc.widget_class is FakeWidget

    def test_buildable_descriptor_on_widget_change_noop(self):
        """BuildableDescriptor.on_widget_change does nothing by default."""
        desc = BuildableDescriptor(default=0)
        desc.on_widget_change("drag")  # Should not raise or append anything
        assert desc.triggered_callbacks == []

    def test_buildable_descriptor_inherits_get_triggered_descriptors(self):
        """BuildableDescriptor.get_triggered_descriptors returns empty list initially."""
        desc = BuildableDescriptor(default=0)
        result = desc.get_triggered_descriptors("field")
        assert result == []


# ---------------------------------------------------------------------------
# Test: SliderDescriptor metadata
# ---------------------------------------------------------------------------

class TestSliderDescriptorMetadata:
    """Test SliderDescriptor metadata (values, defaults, flags)."""

    def test_stores_values_as_list(self):
        """SliderDescriptor converts values iterable to list."""
        desc = SliderDescriptor(values=range(1, 6), default=3)
        assert desc.values == [1, 2, 3, 4, 5]

    def test_stores_values_from_explicit_list(self):
        """SliderDescriptor accepts explicit list of values."""
        desc = SliderDescriptor(values=[0.1, 0.5, 1.0, 2.0], default=1.0)
        assert desc.values == [0.1, 0.5, 1.0, 2.0]

    def test_default_in_values_is_valid(self):
        """SliderDescriptor accepts default that is in values."""
        desc = SliderDescriptor(values=range(1, 11), default=1)
        assert desc.default == 1

    def test_default_not_in_values_raises(self):
        """SliderDescriptor raises ValueError when default not in values."""
        with pytest.raises(ValueError, match="default .* is not in values"):
            SliderDescriptor(values=[1, 3, 5], default=2)

    def test_on_drag_default_true(self):
        """on_drag defaults to True."""
        desc = SliderDescriptor(values=range(1, 11), default=5)
        assert desc.on_drag is True

    def test_on_release_default_false(self):
        """on_release defaults to False."""
        desc = SliderDescriptor(values=range(1, 11), default=5)
        assert desc.on_release is False

    def test_both_flags_can_be_set(self):
        """on_drag and on_release can both be enabled."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=True, on_release=True)
        assert desc.on_drag is True
        assert desc.on_release is True

    def test_both_flags_can_be_disabled(self):
        """on_drag and on_release can both be disabled."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=False, on_release=False)
        assert desc.on_drag is False
        assert desc.on_release is False


# ---------------------------------------------------------------------------
# Test: SliderDescriptor.on_widget_change
# ---------------------------------------------------------------------------

class TestSliderDescriptorOnWidgetChange:
    """Test SliderDescriptor.on_widget_change appends correct callback names."""

    def test_drag_appends_on_drag_when_enabled(self):
        """Drag trigger appends 'on_drag' when on_drag=True."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)
        desc.on_widget_change("drag")
        assert desc.triggered_callbacks == ["on_drag"]

    def test_drag_does_not_append_when_disabled(self):
        """Drag trigger is ignored when on_drag=False."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=False)
        desc.on_widget_change("drag")
        assert desc.triggered_callbacks == []

    def test_release_appends_on_release_when_enabled(self):
        """Release trigger appends 'on_release' when on_release=True."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_release=True)
        desc.on_widget_change("release")
        assert desc.triggered_callbacks == ["on_release"]

    def test_release_does_not_append_when_disabled(self):
        """Release trigger is ignored when on_release=False (default)."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_release=False)
        desc.on_widget_change("release")
        assert desc.triggered_callbacks == []

    def test_unknown_trigger_type_is_ignored(self):
        """Unknown trigger types are silently ignored."""
        desc = SliderDescriptor(values=range(1, 11), default=5)
        desc.on_widget_change("click")
        desc.on_widget_change("unknown")
        assert desc.triggered_callbacks == []

    def test_both_drag_and_release_enabled(self):
        """Both drag and release can fire in the same cycle."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=True, on_release=True)
        desc.on_widget_change("drag")
        desc.on_widget_change("release")
        assert desc.triggered_callbacks == ["on_drag", "on_release"]

    def test_multiple_drags_accumulate(self):
        """Multiple drag events accumulate in triggered_callbacks."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)
        desc.on_widget_change("drag")
        desc.on_widget_change("drag")
        desc.on_widget_change("drag")
        assert desc.triggered_callbacks == ["on_drag", "on_drag", "on_drag"]

    def test_clearing_triggered_callbacks(self):
        """App can clear triggered_callbacks between cycles."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)
        desc.on_widget_change("drag")
        assert desc.triggered_callbacks == ["on_drag"]
        desc.triggered_callbacks.clear()
        assert desc.triggered_callbacks == []

    def test_on_widget_change_change_trigger_ignored(self):
        """'change' trigger type is ignored by SliderDescriptor."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)
        desc.on_widget_change("change")
        assert desc.triggered_callbacks == []


# ---------------------------------------------------------------------------
# Test: SliderDescriptor.get_triggered_descriptors
# ---------------------------------------------------------------------------

class TestSliderGetTriggeredDescriptors:
    """Test get_triggered_descriptors returns correct formatted strings."""

    def test_empty_when_no_events_fired(self):
        """Returns empty list when no events fired."""
        desc = SliderDescriptor(values=range(1, 11), default=5)
        assert desc.get_triggered_descriptors("size") == []

    def test_drag_event_produces_field_on_drag_string(self):
        """Drag event produces 'field.on_drag' string."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)
        desc.on_widget_change("drag")
        assert desc.get_triggered_descriptors("size") == ["size.on_drag"]

    def test_release_event_produces_field_on_release_string(self):
        """Release event produces 'field.on_release' string."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_release=True)
        desc.on_widget_change("release")
        assert desc.get_triggered_descriptors("size") == ["size.on_release"]

    def test_both_events_produce_both_strings(self):
        """Both drag and release events produce both strings."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=True, on_release=True)
        desc.on_widget_change("drag")
        desc.on_widget_change("release")
        result = desc.get_triggered_descriptors("size")
        assert result == ["size.on_drag", "size.on_release"]

    def test_nested_field_path_used_as_prefix(self):
        """Nested dotted path used correctly as prefix."""
        desc = SliderDescriptor(values=range(1, 1025), default=512, on_drag=True)
        desc.on_widget_change("drag")
        assert desc.get_triggered_descriptors("resolution.width") == ["resolution.width.on_drag"]

    def test_does_not_consume_callbacks(self):
        """get_triggered_descriptors does not clear triggered_callbacks."""
        desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)
        desc.on_widget_change("drag")
        desc.get_triggered_descriptors("size")
        # Calling again still returns same result
        assert desc.get_triggered_descriptors("size") == ["size.on_drag"]
        assert desc.triggered_callbacks == ["on_drag"]


# ---------------------------------------------------------------------------
# Test: RadioDescriptor metadata
# ---------------------------------------------------------------------------

class TestRadioDescriptorMetadata:
    """Test RadioDescriptor metadata (options, defaults, flags)."""

    def test_stores_options(self):
        """RadioDescriptor stores options list."""
        desc = RadioDescriptor(options=["A", "B", "C"], default="B")
        assert desc.options == ["A", "B", "C"]

    def test_default_in_options_is_valid(self):
        """RadioDescriptor accepts default that is in options."""
        desc = RadioDescriptor(options=["A", "B"], default="A")
        assert desc.default == "A"

    def test_default_not_in_options_raises(self):
        """RadioDescriptor raises ValueError when default not in options."""
        with pytest.raises(ValueError, match="default .* is not in options"):
            RadioDescriptor(options=["A", "B"], default="C")

    def test_on_change_default_true(self):
        """on_change defaults to True."""
        desc = RadioDescriptor(options=["A", "B"], default="A")
        assert desc.on_change is True

    def test_on_change_can_be_disabled(self):
        """on_change can be disabled."""
        desc = RadioDescriptor(options=["A", "B"], default="A", on_change=False)
        assert desc.on_change is False


# ---------------------------------------------------------------------------
# Test: RadioDescriptor.on_widget_change
# ---------------------------------------------------------------------------

class TestRadioDescriptorOnWidgetChange:
    """Test RadioDescriptor.on_widget_change appends correct callback names."""

    def test_change_appends_on_change_when_enabled(self):
        """Change trigger appends 'on_change' when on_change=True."""
        desc = RadioDescriptor(options=["A", "B"], default="A", on_change=True)
        desc.on_widget_change("change")
        assert desc.triggered_callbacks == ["on_change"]

    def test_change_does_not_append_when_disabled(self):
        """Change trigger is ignored when on_change=False."""
        desc = RadioDescriptor(options=["A", "B"], default="A", on_change=False)
        desc.on_widget_change("change")
        assert desc.triggered_callbacks == []

    def test_unknown_trigger_type_is_ignored(self):
        """Unknown trigger types are silently ignored by RadioDescriptor."""
        desc = RadioDescriptor(options=["A", "B"], default="A")
        desc.on_widget_change("drag")
        desc.on_widget_change("release")
        desc.on_widget_change("click")
        assert desc.triggered_callbacks == []

    def test_multiple_changes_accumulate(self):
        """Multiple change events accumulate in triggered_callbacks."""
        desc = RadioDescriptor(options=["A", "B"], default="A")
        desc.on_widget_change("change")
        desc.on_widget_change("change")
        assert desc.triggered_callbacks == ["on_change", "on_change"]

    def test_clearing_triggered_callbacks(self):
        """App can clear triggered_callbacks between cycles."""
        desc = RadioDescriptor(options=["A", "B"], default="A")
        desc.on_widget_change("change")
        desc.triggered_callbacks.clear()
        assert desc.triggered_callbacks == []


# ---------------------------------------------------------------------------
# Test: RadioDescriptor.get_triggered_descriptors
# ---------------------------------------------------------------------------

class TestRadioGetTriggeredDescriptors:
    """Test RadioDescriptor.get_triggered_descriptors returns correct strings."""

    def test_empty_when_no_events_fired(self):
        """Returns empty list when no events fired."""
        desc = RadioDescriptor(options=["A", "B"], default="A")
        assert desc.get_triggered_descriptors("mode") == []

    def test_change_event_produces_field_on_change_string(self):
        """Change event produces 'field.on_change' string."""
        desc = RadioDescriptor(options=["A", "B"], default="A")
        desc.on_widget_change("change")
        assert desc.get_triggered_descriptors("mode") == ["mode.on_change"]

    def test_nested_field_path_used_as_prefix(self):
        """Nested dotted path used correctly as prefix."""
        desc = RadioDescriptor(options=["fast", "slow"], default="fast")
        desc.on_widget_change("change")
        assert desc.get_triggered_descriptors("settings.speed") == ["settings.speed.on_change"]


# ---------------------------------------------------------------------------
# Test: Descriptor independence (each instance has own triggered_callbacks)
# ---------------------------------------------------------------------------

class TestDescriptorInstanceIndependence:
    """Each descriptor instance has its own state."""

    def test_two_slider_descriptors_have_independent_callbacks(self):
        """Firing one slider does not affect another."""
        d1 = SliderDescriptor(values=range(1, 11), default=5)
        d2 = SliderDescriptor(values=range(1, 11), default=3)
        d1.on_widget_change("drag")
        assert d1.triggered_callbacks == ["on_drag"]
        assert d2.triggered_callbacks == []

    def test_two_radio_descriptors_have_independent_callbacks(self):
        """Firing one radio does not affect another."""
        d1 = RadioDescriptor(options=["A", "B"], default="A")
        d2 = RadioDescriptor(options=["X", "Y"], default="X")
        d1.on_widget_change("change")
        assert d1.triggered_callbacks == ["on_change"]
        assert d2.triggered_callbacks == []

    def test_two_slider_descriptors_have_independent_visibility(self):
        """Setting isVisible on one does not affect the other."""
        d1 = SliderDescriptor(values=range(1, 11), default=5)
        d2 = SliderDescriptor(values=range(1, 11), default=3)
        d1.isVisible = False
        assert d1.isVisible is False
        assert d2.isVisible is True


# ---------------------------------------------------------------------------
# Test: Integration with @guibbon.params
# ---------------------------------------------------------------------------

class TestDescriptorIntegrationWithParams:
    """Test that descriptor.py classes integrate correctly with @guibbon.params."""

    def test_slider_descriptor_stored_in_guibbon_descriptors(self):
        """SliderDescriptor stored in __guibbon_descriptors__ after @guibbon.params."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        assert "size" in Params.__guibbon_descriptors__
        assert isinstance(Params.__guibbon_descriptors__["size"], SliderDescriptor)

    def test_radio_descriptor_stored_in_guibbon_descriptors(self):
        """RadioDescriptor stored in __guibbon_descriptors__ after @guibbon.params."""
        @guibbon.params
        class Params:
            mode: str = RadioDescriptor(options=["A", "B"], default="A")

        assert "mode" in Params.__guibbon_descriptors__
        assert isinstance(Params.__guibbon_descriptors__["mode"], RadioDescriptor)

    def test_descriptor_on_widget_change_works_after_params_decoration(self):
        """on_widget_change works on descriptors extracted by @guibbon.params."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5, on_drag=True)

        desc = Params.__guibbon_descriptors__["size"]
        desc.on_widget_change("drag")
        assert desc.triggered_callbacks == ["on_drag"]

    def test_full_cycle_modified_descriptors_pattern(self):
        """Simulate full app cycle: fire event → collect → clear → fire again."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5, on_drag=True, on_release=True)
            mode: str = RadioDescriptor(options=["A", "B"], default="A")

        size_desc = Params.__guibbon_descriptors__["size"]
        mode_desc = Params.__guibbon_descriptors__["mode"]

        # Cycle 1: user drags size slider and changes mode
        size_desc.on_widget_change("drag")
        mode_desc.on_widget_change("change")

        modified = (
            size_desc.get_triggered_descriptors("size")
            + mode_desc.get_triggered_descriptors("mode")
        )
        assert modified == ["size.on_drag", "mode.on_change"]

        # App clears between cycles
        size_desc.triggered_callbacks.clear()
        mode_desc.triggered_callbacks.clear()

        # Cycle 2: user releases slider only
        size_desc.on_widget_change("release")

        modified = (
            size_desc.get_triggered_descriptors("size")
            + mode_desc.get_triggered_descriptors("mode")
        )
        assert modified == ["size.on_release"]

    def test_descriptor_default_sets_params_field_value(self):
        """Descriptor default is used as dataclass field default value."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=7)

        params = Params()
        assert params.size == 7

    def test_descriptor_is_buildable_descriptor(self):
        """Descriptors from params are BuildableDescriptor instances."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        desc = Params.__guibbon_descriptors__["size"]
        assert isinstance(desc, BuildableDescriptor)
        assert isinstance(desc, Descriptor)
