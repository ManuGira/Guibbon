"""Tests for @guibbon.params decorator and tracked value system.

Tests cover:
  - Tracked type generation (IS-A inheritance, operations)
  - GetPath() path reconstruction for nested structures
  - @guibbon.params decorator (extraction, @dataclass, parent wiring)
  - Descriptor metadata storage on classes
  - Nested @guibbon.params classes
  - IDE autocompletion support (real types)
"""

import pytest

import guibbon
from guibbon import RadioDescriptor, SliderDescriptor
from guibbon.core import (
    GetPath,
    _make_tracked_type,
)


# ---------------------------------------------------------------------------
# Test: Tracked type generation and type inheritance
# ---------------------------------------------------------------------------

class TestTrackedTypeGeneration:
    """Test that _make_tracked_type creates real subclasses."""

    def test_tracked_int_is_int(self):
        """TrackedInt inherits from int; isinstance check passes."""
        TrackedInt = _make_tracked_type(int)
        tracked = TrackedInt(5, _parent=None, _field_name="test")
        assert isinstance(tracked, int)
        assert tracked == 5

    def test_tracked_str_is_str(self):
        """TrackedStr inherits from str; normal string operations work."""
        TrackedStr = _make_tracked_type(str)
        tracked = TrackedStr("hello", _parent=None, _field_name="test")
        assert isinstance(tracked, str)
        assert tracked == "hello"
        assert tracked.upper() == "HELLO"

    def test_tracked_float_is_float(self):
        """TrackedFloat inherits from float; arithmetic works."""
        TrackedFloat = _make_tracked_type(float)
        tracked = TrackedFloat(3.14, _parent=None, _field_name="test")
        assert isinstance(tracked, float)
        assert abs((tracked + 1.0) - 4.14) < 1e-10  # Float precision
        assert abs((tracked * 2) - 6.28) < 1e-10

    def test_tracked_int_arithmetic(self):
        """TrackedInt arithmetic operations work like regular ints."""
        TrackedInt = _make_tracked_type(int)
        a = TrackedInt(5, _parent=None, _field_name="a")
        b = TrackedInt(3, _parent=None, _field_name="b")
        assert a + b == 8
        assert a * b == 15
        assert a - b == 2

    def test_tracked_list_is_list(self):
        """TrackedList inherits from list; list operations work."""
        TrackedList = _make_tracked_type(list)
        tracked = TrackedList([1, 2, 3], _parent=None, _field_name="test")
        assert isinstance(tracked, list)
        assert tracked[0] == 1
        assert len(tracked) == 3
        tracked.append(4)
        assert len(tracked) == 4

    def test_tracked_dict_is_dict(self):
        """TrackedDict inherits from dict; dict operations work."""
        TrackedDict = _make_tracked_type(dict)
        tracked = TrackedDict({"a": 1}, _parent=None, _field_name="test")
        assert isinstance(tracked, dict)
        assert tracked["a"] == 1
        tracked["b"] = 2
        assert len(tracked) == 2

    def test_tracked_cache_reuses_types(self):
        """_make_tracked_type caches types; repeated calls return same type."""
        TrackedInt1 = _make_tracked_type(int)
        TrackedInt2 = _make_tracked_type(int)
        assert TrackedInt1 is TrackedInt2

    def test_tracked_type_carries_parent_metadata(self):
        """Tracked values carry _parent and _field_name."""
        TrackedInt = _make_tracked_type(int)
        parent_obj = object()
        tracked = TrackedInt(5, _parent=parent_obj, _field_name="myfield")
        assert tracked._parent is parent_obj
        assert tracked._field_name == "myfield"


# ---------------------------------------------------------------------------
# Test: GetPath path reconstruction
# ---------------------------------------------------------------------------

class TestGetPath:
    """Test GetPath() walks parent chain to reconstruct dotted paths."""

    class _Container:
        """Simple container for testing parent chain construction."""
        pass

    def test_getpath_simple_field(self):
        """GetPath on root-level field returns just the field name."""
        TrackedInt = _make_tracked_type(int)
        parent = self._Container()
        value = TrackedInt(5, _parent=parent, _field_name="sigma")
        object.__setattr__(parent, '_field_name', "")
        object.__setattr__(parent, '_parent', None)
        assert GetPath(value) == "sigma"

    def test_getpath_nested_field(self):
        """GetPath reconstructs nested dotted paths."""
        # Manually construct parent chain
        root = self._Container()
        object.__setattr__(root, '_field_name', "")
        object.__setattr__(root, '_parent', None)

        resolution = self._Container()
        object.__setattr__(resolution, '_field_name', "resolution")
        object.__setattr__(resolution, '_parent', root)

        TrackedInt = _make_tracked_type(int)
        width = TrackedInt(512, _parent=resolution, _field_name="width")

        assert GetPath(width) == "resolution.width"

    def test_getpath_deep_nesting(self):
        """GetPath works with deeply nested structures."""
        # Build chain: root -> foo -> bar -> baz
        root = self._Container()
        object.__setattr__(root, '_field_name', "")
        object.__setattr__(root, '_parent', None)

        foo = self._Container()
        object.__setattr__(foo, '_field_name', "foo")
        object.__setattr__(foo, '_parent', root)

        bar = self._Container()
        object.__setattr__(bar, '_field_name', "bar")
        object.__setattr__(bar, '_parent', foo)

        baz = self._Container()
        object.__setattr__(baz, '_field_name', "baz")
        object.__setattr__(baz, '_parent', bar)

        TrackedInt = _make_tracked_type(int)
        value = TrackedInt(99, _parent=baz, _field_name="value")

        assert GetPath(value) == "foo.bar.baz.value"


# ---------------------------------------------------------------------------
# Test: @guibbon.params decorator
# ---------------------------------------------------------------------------

class TestGuibboParamsDecorator:
    """Test @guibbon.params decorator creates dataclasses with tracking."""

    def test_simple_params_class(self):
        """@guibbon.params creates a dataclass with default values."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)
            name: str = RadioDescriptor(options=["A", "B"], default="A")

        params = Params()
        assert params.size == 5
        assert params.name == "A"

    def test_params_fields_are_tracked(self):
        """After construction, field values are tracked (know their parents)."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        params = Params()
        # The size value should be a TrackedInt with parent info
        assert hasattr(params.size, '_parent')
        assert hasattr(params.size, '_field_name')
        assert params.size._parent is params
        assert params.size._field_name == "size"

    def test_params_ide_sees_real_types(self):
        """TrackedInt IS-A int; IDE gets real type hints."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)
            sigma: float = SliderDescriptor(values=[0.1, 1.0], default=1.0)
            mode: str = RadioDescriptor(options=["blur"], default="blur")

        params = Params()
        # Each field is its real type (after wrapping)
        assert isinstance(params.size, int)
        assert isinstance(params.sigma, float)
        assert isinstance(params.mode, str)

    def test_params_descriptors_on_class(self):
        """Descriptors are stored on __guibbon_descriptors__ on the class."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)
            name: str = RadioDescriptor(options=["A", "B"], default="A")

        assert hasattr(Params, '__guibbon_descriptors__')
        assert 'size' in Params.__guibbon_descriptors__
        assert 'name' in Params.__guibbon_descriptors__
        assert isinstance(Params.__guibbon_descriptors__['size'], SliderDescriptor)
        assert isinstance(Params.__guibbon_descriptors__['name'], RadioDescriptor)

    def test_params_is_dataclass(self):
        """@guibbon.params applies @dataclass; introspection works."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        # Check that it's a dataclass
        from dataclasses import is_dataclass
        assert is_dataclass(Params)
        # Should have __init__, __repr__, __eq__, etc.
        assert hasattr(Params, '__init__')
        assert hasattr(Params, '__repr__')
        assert hasattr(Params, '__eq__')

    def test_params_repr(self):
        """Generated __repr__ shows field values."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        params = Params()
        repr_str = repr(params)
        assert "size" in repr_str
        assert "5" in repr_str or "TrackedInt(5" in repr_str

    def test_params_two_instances_independent(self):
        """Two instances have independent field values."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        p1 = Params()
        p2 = Params()

        # Modify p1's size
        TrackedInt = _make_tracked_type(int)
        object.__setattr__(p1, 'size', TrackedInt(7, _parent=p1, _field_name="size"))

        # p2's size should still be 5
        assert p1.size == 7
        assert p2.size == 5


# ---------------------------------------------------------------------------
# Test: Nested @guibbon.params
# ---------------------------------------------------------------------------

class TestNestedParams:
    """Test nested @guibbon.params classes work correctly."""

    def test_nested_params_class(self):
        """Nested @guibbon.params classes structure correctly."""

        @guibbon.params
        class Resolution:
            width: int = SliderDescriptor(values=range(1, 1025), default=512)
            height: int = SliderDescriptor(values=range(1, 1025), default=768)

        # Test that nested class works standalone
        res = Resolution()
        assert res.width == 512
        assert res.height == 768
        # Verify descriptors are stored on class
        assert hasattr(Resolution, '__guibbon_descriptors__')
        assert 'width' in Resolution.__guibbon_descriptors__

    def test_nested_params_with_field_default_factory(self):
        """Nested @guibbon.params using field(default_factory=...)."""
        from dataclasses import field

        @guibbon.params
        class Resolution:
            width: int = SliderDescriptor(values=range(1, 1025), default=512)
            height: int = SliderDescriptor(values=range(1, 1025), default=768)

        @guibbon.params
        class Params:
            sigma: float = SliderDescriptor(values=[0.1, 1.0], default=1.0)
            resolution: Resolution = field(default_factory=Resolution)

        params = Params()
        assert params.sigma == 1.0
        assert params.resolution.width == 512
        assert params.resolution.height == 768

    def test_nested_getpath(self):
        """GetPath works on nested field values."""
        from dataclasses import field

        @guibbon.params
        class Resolution:
            width: int = SliderDescriptor(values=range(1, 1025), default=512)

        @guibbon.params
        class Params:
            resolution: Resolution = field(default_factory=Resolution)

        params = Params()
        # Width should have parent chain: width -> resolution -> params
        assert GetPath(params.resolution.width) == "resolution.width"


# ---------------------------------------------------------------------------
# Test: Descriptor metadata
# ---------------------------------------------------------------------------

class TestDescriptorMetadata:
    """Test descriptor properties (defaults, options, visibility, etc.)."""

    def test_slider_descriptor_has_values(self):
        """SliderDescriptor stores values range."""
        slider = SliderDescriptor(values=range(1, 11), default=5)
        assert slider.values == list(range(1, 11))
        assert slider.default == 5

    def test_slider_descriptor_validates_default_in_values(self):
        """SliderDescriptor raises ValueError if default not in values."""
        with pytest.raises(ValueError, match="default .* is not in values"):
            SliderDescriptor(values=[1, 3, 5], default=2)

    def test_radio_descriptor_has_options(self):
        """RadioDescriptor stores options."""
        radio = RadioDescriptor(options=["A", "B", "C"], default="B")
        assert radio.options == ["A", "B", "C"]
        assert radio.default == "B"

    def test_radio_descriptor_validates_default_in_options(self):
        """RadioDescriptor raises ValueError if default not in options."""
        with pytest.raises(ValueError, match="default .* is not in options"):
            RadioDescriptor(options=["A", "B"], default="C")

    def test_descriptor_triggered_callbacks(self):
        """Descriptors have triggered_callbacks list for tracking."""
        slider = SliderDescriptor(values=range(1, 11), default=5)
        assert slider.triggered_callbacks == []
        slider.triggered_callbacks.append("on_drag")
        assert slider.triggered_callbacks == ["on_drag"]

    def test_descriptor_visibility(self):
        """Descriptors have isVisible flag (default True)."""
        slider = SliderDescriptor(values=range(1, 11), default=5)
        assert slider.isVisible is True
        slider.isVisible = False
        assert slider.isVisible is False


# ---------------------------------------------------------------------------
# Test: Callback signature patterns (from ARCHITECTURE.md examples)
# ---------------------------------------------------------------------------

class TestCallbackPatterns:
    """Test callback patterns described in architecture."""

    def test_callback_receives_params_and_modified_descriptors(self):
        """User callback receives params instance and modified list."""
        @guibbon.params
        class Params:
            size: int = SliderDescriptor(values=range(1, 11), default=5)

        params = Params()
        modified_descriptors = ["size.on_drag"]

        # Simulate what the app would do
        assert isinstance(params, Params)
        assert isinstance(modified_descriptors, list)
        assert all(isinstance(md, str) for md in modified_descriptors)

    def test_dynamic_visibility_pattern(self):
        """Callback can check modified_descriptors and update visibility."""
        @guibbon.params
        class Params:
            filter_type: str = RadioDescriptor(
                options=["Gaussian", "Bilateral"], default="Gaussian"
            )
            sigma: float = SliderDescriptor(values=[0.1, 1.0], default=1.0)

        params = Params()
        modified_descriptors = ["filter_type.on_change"]

        # Pattern: dynamic visibility based on current params
        if "filter_type.on_change" in modified_descriptors:
            if params.filter_type == "Gaussian":
                Params.__guibbon_descriptors__['sigma'].isVisible = True
            else:
                Params.__guibbon_descriptors__['sigma'].isVisible = False

        assert Params.__guibbon_descriptors__['sigma'].isVisible is True

    def test_pattern_matching_on_callbacks(self):
        """Test common pattern matching idioms on modified_descriptors."""
        modified_descriptors = [
            "size.on_drag",
            "type.on_change",
            "point1.on_release",
            "point2.on_drag",
        ]

        # Pattern 1: Check for specific descriptor callback
        assert "size.on_drag" in modified_descriptors

        # Pattern 2: Check for any drag event
        assert any("on_drag" in md for md in modified_descriptors)

        # Pattern 3: Filter by descriptor name
        point_events = [md for md in modified_descriptors if "point" in md]
        assert len(point_events) == 2
        assert "point1.on_release" in point_events

        # Pattern 4: Complex filter (release events only)
        release_events = [md for md in modified_descriptors if ".on_release" in md]
        assert release_events == ["point1.on_release"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
