"""Tests for buildable.py — BuildableWidget protocol.

Tests cover:
  - Protocol has exactly one method: build(self, parent: Any)
  - No framework imports (tk, PyQt, PySide6, nicegui) in the module
  - Structural satisfaction (no explicit inheritance required)
  - Explicit subclassing also satisfies the protocol
  - Multiple independent implementations satisfy the protocol
  - Non-conforming classes do NOT satisfy the protocol
  - runtime_checkable isinstance() checks
  - build() accepts any parent type (None, str, dict, mock objects)
  - Docstring content: Tkinter, nicegui, PySide6 examples are present
  - Protocol is exported from guibbon.core
"""

import inspect


from guibbon.core.buildable import BuildableWidget


# ---------------------------------------------------------------------------
# Helpers — concrete implementations used across tests
# ---------------------------------------------------------------------------

class _TkinterLike:
    """Simulates a Tkinter-style implementation."""

    def __init__(self) -> None:
        self.last_parent: object = None

    def build(self, parent: object) -> None:
        self.last_parent = parent


class _NiceguiLike:
    """Simulates a nicegui-style implementation (parent may be None)."""

    def __init__(self) -> None:
        self.built = False

    def build(self, parent: object) -> None:
        self.built = True


class _PySide6Like:
    """Simulates a PySide6-style implementation."""

    def build(self, parent: object) -> None:
        pass


class _ExplicitSubclass(BuildableWidget):
    """Explicit subclass (structural + nominal)."""

    def build(self, parent: object) -> None:
        pass


class _NoBuildMethod:
    """Does NOT implement build(); must NOT satisfy the protocol."""

    def render(self, parent: object) -> None:  # wrong method name
        pass


class _BuildWrongSignature:
    """Has build() but wrong signature (no parent argument)."""

    def build(self) -> None:  # missing parent
        pass


# ---------------------------------------------------------------------------
# Test: Protocol structure
# ---------------------------------------------------------------------------

class TestBuildableWidgetProtocolStructure:
    """Verify the protocol itself is shaped correctly."""

    def test_buildable_widget_has_build_method(self):
        """BuildableWidget protocol defines a 'build' method."""
        assert hasattr(BuildableWidget, "build")

    def test_build_method_is_the_only_protocol_method(self):
        """Protocol exposes exactly one abstract method: build."""
        members = {
            name
            for name, _ in inspect.getmembers(BuildableWidget, predicate=inspect.isfunction)
            if not name.startswith("_")
        }
        assert members == {"build"}

    def test_build_signature_has_parent_parameter(self):
        """build() has a 'parent' parameter."""
        sig = inspect.signature(BuildableWidget.build)
        assert "parent" in sig.parameters

    def test_build_returns_none(self):
        """build() is annotated to return None."""
        sig = inspect.signature(BuildableWidget.build)
        # from __future__ import annotations makes annotations strings
        assert sig.return_annotation in (None, type(None), "None", inspect.Parameter.empty)

    def test_protocol_is_runtime_checkable(self):
        """BuildableWidget is decorated with @runtime_checkable."""
        widget = _TkinterLike()
        # Would raise TypeError if not runtime_checkable
        result = isinstance(widget, BuildableWidget)
        assert result is True


# ---------------------------------------------------------------------------
# Test: No framework imports
# ---------------------------------------------------------------------------

class TestNoFrameworkImports:
    """buildable.py must not import any GUI framework at module level."""

    def _module(self) -> object:
        import guibbon.core.buildable as mod
        return mod

    def test_no_tkinter_import(self):
        """buildable.py does not import tkinter at module level."""
        mod = self._module()
        assert not hasattr(mod, "tk") and not hasattr(mod, "tkinter")

    def test_no_pyqt_import(self):
        """buildable.py does not import PyQt at module level."""
        mod = self._module()
        assert not hasattr(mod, "PyQt5") and not hasattr(mod, "PyQt6")

    def test_no_pyside_import(self):
        """buildable.py does not import PySide6 at module level."""
        mod = self._module()
        assert not hasattr(mod, "PySide6")

    def test_no_nicegui_import(self):
        """buildable.py does not import nicegui at module level."""
        mod = self._module()
        assert not hasattr(mod, "nicegui") and not hasattr(mod, "ui")


# ---------------------------------------------------------------------------
# Test: Structural satisfaction (no inheritance needed)
# ---------------------------------------------------------------------------

class TestStructuralSatisfaction:
    """Any class with build(self, parent) satisfies the protocol structurally."""

    def test_tkinter_like_satisfies_protocol(self):
        """_TkinterLike satisfies BuildableWidget without explicit subclassing."""
        assert isinstance(_TkinterLike(), BuildableWidget)

    def test_nicegui_like_satisfies_protocol(self):
        """_NiceguiLike satisfies BuildableWidget without explicit subclassing."""
        assert isinstance(_NiceguiLike(), BuildableWidget)

    def test_pyside6_like_satisfies_protocol(self):
        """_PySide6Like satisfies BuildableWidget without explicit subclassing."""
        assert isinstance(_PySide6Like(), BuildableWidget)

    def test_explicit_subclass_satisfies_protocol(self):
        """Explicit subclass also satisfies the protocol."""
        assert isinstance(_ExplicitSubclass(), BuildableWidget)

    def test_no_build_method_does_not_satisfy_protocol(self):
        """Class without build() does NOT satisfy BuildableWidget."""
        assert not isinstance(_NoBuildMethod(), BuildableWidget)


# ---------------------------------------------------------------------------
# Test: Multiple independent implementations
# ---------------------------------------------------------------------------

class TestMultipleImplementations:
    """Multiple unrelated classes can each satisfy BuildableWidget."""

    def test_all_three_framework_styles_are_valid(self):
        """Three independent implementations all satisfy BuildableWidget."""
        widgets: list[BuildableWidget] = [
            _TkinterLike(),  # type: ignore[list-item]
            _NiceguiLike(),  # type: ignore[list-item]
            _PySide6Like(),  # type: ignore[list-item]
        ]
        for widget in widgets:
            assert isinstance(widget, BuildableWidget)

    def test_build_is_callable_on_all_implementations(self):
        """build() can be called on any implementation with any parent."""
        parents = [None, "frame", 42, object(), {"key": "value"}]
        for widget_cls in (_TkinterLike, _NiceguiLike, _PySide6Like, _ExplicitSubclass):
            for parent in parents:
                widget = widget_cls()
                widget.build(parent)  # must not raise


# ---------------------------------------------------------------------------
# Test: build() accepts any parent type
# ---------------------------------------------------------------------------

class TestBuildAcceptsAnyParent:
    """build(parent) must accept any type without type errors at runtime."""

    def test_build_accepts_none_parent(self):
        """build() works with parent=None (nicegui pattern)."""
        widget = _TkinterLike()
        widget.build(None)
        assert widget.last_parent is None

    def test_build_accepts_string_parent(self):
        """build() works with a string parent."""
        widget = _TkinterLike()
        widget.build("some_frame")
        assert widget.last_parent == "some_frame"

    def test_build_accepts_dict_parent(self):
        """build() works with a dict parent."""
        widget = _TkinterLike()
        widget.build({"name": "root"})
        assert widget.last_parent == {"name": "root"}


# ---------------------------------------------------------------------------
# Test: Docstring content
# ---------------------------------------------------------------------------

class TestDocstringContent:
    """Protocol docstring must document all three framework examples."""

    def _docstring(self) -> str:
        return BuildableWidget.__doc__ or ""

    def test_docstring_mentions_tkinter(self):
        """Docstring includes Tkinter example."""
        assert "Tkinter" in self._docstring() or "tkinter" in self._docstring()

    def test_docstring_mentions_nicegui(self):
        """Docstring includes nicegui example."""
        assert "nicegui" in self._docstring()

    def test_docstring_mentions_pyside6(self):
        """Docstring includes PySide6 example."""
        assert "PySide6" in self._docstring()


# ---------------------------------------------------------------------------
# Test: Export from guibbon.core
# ---------------------------------------------------------------------------

class TestCoreExport:
    """BuildableWidget must be importable from guibbon.core."""

    def test_buildable_widget_exported_from_core(self):
        """BuildableWidget is accessible via guibbon.core."""
        from guibbon.core import BuildableWidget as BW  # noqa: PLC0415

        assert BW is BuildableWidget

    def test_buildable_widget_in_core_all(self):
        """BuildableWidget appears in guibbon.core.__all__."""
        import guibbon.core as core  # noqa: PLC0415

        assert "BuildableWidget" in core.__all__
