import unittest
import tkinter as tk
from unittest.mock import Mock

from guibbon.widgets.check_button_widget import CheckButtonWidget


# Shared Tk root for all tests to avoid tkinter instability
_tk_root = None


def setUpModule():
    """Create a single shared Tk root for all tests in this module"""
    global _tk_root
    _tk_root = tk.Tk()
    _tk_root.withdraw()  # Hide the window


def tearDownModule():
    """Destroy the shared Tk root after all tests"""
    global _tk_root
    if _tk_root:
        try:
            _tk_root.destroy()
        except tk.TclError:
            pass
        _tk_root = None


class TestCheckButtonWidget(unittest.TestCase):
    """Test suite for CheckButtonWidget"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        # Use a Frame as child of the shared root instead of creating new Tk()
        self.frame = tk.Frame(_tk_root, width=400, height=300)
        self.frame.pack(expand=True, fill='both')
        # Update to ensure frame is rendered and has dimensions
        _tk_root.update_idletasks()
        _tk_root.update()

    def tearDown(self) -> None:
        """Clean up after tests"""
        try:
            self.frame.destroy()
        except tk.TclError:
            pass

    def test_create_check_button_widget_default(self) -> None:
        """Test basic CheckButtonWidget creation with default value (False)"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test CheckButton",
            on_change=callback,
        )

        # Check widget was created
        self.assertIsNotNone(widget)
        self.assertIsNotNone(widget.frame)
        self.assertIsNotNone(widget.var)
        
        # Check default value is False
        self.assertEqual(widget.get_current_value(), False)
        self.assertEqual(widget.var.get(), False)

    def test_create_with_initial_value_true(self) -> None:
        """Test creating widget with initial value True"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test CheckButton",
            on_change=callback,
            initial_value=True,
        )

        # Check initial value is True
        self.assertEqual(widget.get_current_value(), True)
        self.assertEqual(widget.var.get(), True)

    def test_create_with_initial_value_false(self) -> None:
        """Test creating widget with initial value False"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test CheckButton",
            on_change=callback,
            initial_value=False,
        )

        # Check initial value is False
        self.assertEqual(widget.get_current_value(), False)
        self.assertEqual(widget.var.get(), False)

    def test_widget_name_stored(self) -> None:
        """Test that widget stores its name"""
        callback = Mock()
        widget_name = "My CheckButton"
        
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name=widget_name,
            on_change=callback,
        )

        self.assertEqual(widget.name, widget_name)

    def test_get_current_value_false(self) -> None:
        """Test get_current_value returns False when unchecked"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_value=False,
        )

        value = widget.get_current_value()
        self.assertIsInstance(value, bool)
        self.assertEqual(value, False)

    def test_get_current_value_true(self) -> None:
        """Test get_current_value returns True when checked"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_value=True,
        )

        value = widget.get_current_value()
        self.assertIsInstance(value, bool)
        self.assertEqual(value, True)

    def test_callback_on_check(self) -> None:
        """Test callback is called with True when checkbox is checked"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_value=False,
        )

        # Simulate checking the checkbox
        widget.var.set(True)
        widget.callback()

        # Check callback was called with True
        callback.assert_called_once_with(True)

    def test_callback_on_uncheck(self) -> None:
        """Test callback is called with False when checkbox is unchecked"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_value=True,
        )

        # Simulate unchecking the checkbox
        widget.var.set(False)
        widget.callback()

        # Check callback was called with False
        callback.assert_called_once_with(False)

    def test_multiple_state_changes(self) -> None:
        """Test multiple state changes call callback correctly"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_value=False,
        )

        # First change: False -> True
        widget.var.set(True)
        widget.callback()
        self.assertEqual(widget.get_current_value(), True)

        # Second change: True -> False
        widget.var.set(False)
        widget.callback()
        self.assertEqual(widget.get_current_value(), False)

        # Third change: False -> True
        widget.var.set(True)
        widget.callback()
        self.assertEqual(widget.get_current_value(), True)

        # Verify callback was called 3 times
        self.assertEqual(callback.call_count, 3)
        
        # Verify the calls were made with correct values
        calls = [call[0][0] for call in callback.call_args_list]
        self.assertEqual(calls, [True, False, True])

    def test_state_consistency(self) -> None:
        """Test that var.get() and get_current_value() are consistent"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
        )

        # Initially False
        self.assertEqual(widget.var.get(), widget.get_current_value())

        # Change to True
        widget.var.set(True)
        self.assertEqual(widget.var.get(), widget.get_current_value())

        # Change back to False
        widget.var.set(False)
        self.assertEqual(widget.var.get(), widget.get_current_value())

    def test_callback_not_called_on_creation(self) -> None:
        """Test that callback is not called during widget creation"""
        callback = Mock()
        
        _ = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_value=True,
        )

        # Callback should not have been called yet
        callback.assert_not_called()

    def test_boolean_var_type(self) -> None:
        """Test that the internal variable is a BooleanVar"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
        )

        self.assertIsInstance(widget.var, tk.BooleanVar)

    def test_frame_packing(self) -> None:
        """Test that widget frame is properly packed"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
        )

        # Check that the frame has been packed (it should be a child of self.frame)
        children = self.frame.winfo_children()
        self.assertIn(widget.frame, children)

    def test_direct_var_manipulation(self) -> None:
        """Test that directly manipulating var reflects in get_current_value"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_value=False,
        )

        # Directly set the variable
        widget.var.set(True)
        _tk_root.update_idletasks()
        
        # Check it's reflected in get_current_value
        self.assertEqual(widget.get_current_value(), True)

        # Set it back
        widget.var.set(False)
        _tk_root.update_idletasks()
        
        self.assertEqual(widget.get_current_value(), False)

    def test_callback_with_alternating_values(self) -> None:
        """Test callback receives correct alternating boolean values"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_value=False,
        )

        # Simulate several state changes
        for expected_value in [True, False, True, False, True]:
            widget.var.set(expected_value)
            widget.callback()
            
            # Verify last call had expected value
            callback.assert_called_with(expected_value)

        # Verify all calls
        self.assertEqual(callback.call_count, 5)

    def test_widget_name_empty_string(self) -> None:
        """Test creating widget with empty string name"""
        callback = Mock()
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name="",
            on_change=callback,
        )

        self.assertEqual(widget.name, "")
        self.assertIsNotNone(widget.frame)

    def test_widget_name_special_characters(self) -> None:
        """Test creating widget with special characters in name"""
        callback = Mock()
        special_name = "Test @ CheckButton #123 & More!"
        
        widget = CheckButtonWidget(
            tk_frame=self.frame,
            name=special_name,
            on_change=callback,
        )

        self.assertEqual(widget.name, special_name)


if __name__ == "__main__":
    unittest.main()
