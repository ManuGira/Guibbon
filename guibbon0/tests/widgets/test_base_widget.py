import tkinter as tk
import unittest
from unittest.mock import create_autospec

from guibbon.widgets.base import BaseWidget, BuildableWidget


class DummyBuildable:
    """Simple duck-typed widget implementing the expected build method."""

    def __init__(self):
        self.built_with: tk.Frame | None = None

    def build(self, parent: tk.Frame) -> None:
        self.built_with = parent


class ConcreteWidget(BaseWidget):
    """Concrete BaseWidget implementation used for tests."""

    def __init__(self, *, widget_color=None):
        super().__init__(widget_color=widget_color)
        self.built = False
        self.parent: tk.Frame | None = None

    def build(self, parent: tk.Frame) -> None:
        self.built = True
        self.parent = parent


class IncompleteWidget(BaseWidget):
    """BaseWidget subclass that intentionally leaves build() abstract."""

    pass


class TestBaseWidget(unittest.TestCase):

    def test_buildable_widget_protocol_accepts_duck_typed_objects(self):
        widget = DummyBuildable()
        self.assertIsInstance(widget, BuildableWidget)

    def test_buildable_widget_protocol_rejects_objects_without_build(self):
        class NotBuildable:
            pass

        self.assertNotIsInstance(NotBuildable(), BuildableWidget)

    def test_base_widget_stores_widget_color_and_build_invocation(self):
        parent = create_autospec(tk.Frame)
        widget = ConcreteWidget(widget_color="blue")

        widget.build(parent)

        self.assertEqual(widget.widget_color, "blue")
        self.assertTrue(widget.built)
        self.assertIs(widget.parent, parent)

    def test_base_widget_is_abstract_until_build_overridden(self):
        with self.assertRaises(TypeError):
            IncompleteWidget()  # type: ignore[abstract]

    def test_concrete_widget_behaves_as_buildable_widget(self):
        widget = ConcreteWidget()
        parent = create_autospec(tk.Frame)

        widget.build(parent)

        self.assertIsInstance(widget, BuildableWidget)
        self.assertIs(widget.parent, parent)

