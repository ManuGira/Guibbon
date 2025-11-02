import unittest
import tkinter as tk
from unittest.mock import Mock, patch

from guibbon.widgets.color_picker_widget import (
    ColorPickerWidget,
    convert_color_tuple3i_to_hexastr,
)


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


class TestColorConversion(unittest.TestCase):
    """Test suite for color conversion utility functions"""

    def test_convert_black(self) -> None:
        """Test converting black color"""
        result = convert_color_tuple3i_to_hexastr((0, 0, 0))
        self.assertEqual(result, "#000000")

    def test_convert_white(self) -> None:
        """Test converting white color"""
        result = convert_color_tuple3i_to_hexastr((255, 255, 255))
        self.assertEqual(result, "#ffffff")

    def test_convert_red(self) -> None:
        """Test converting pure red"""
        result = convert_color_tuple3i_to_hexastr((255, 0, 0))
        self.assertEqual(result, "#ff0000")

    def test_convert_green(self) -> None:
        """Test converting pure green"""
        result = convert_color_tuple3i_to_hexastr((0, 255, 0))
        self.assertEqual(result, "#00ff00")

    def test_convert_blue(self) -> None:
        """Test converting pure blue"""
        result = convert_color_tuple3i_to_hexastr((0, 0, 255))
        self.assertEqual(result, "#0000ff")

    def test_convert_mixed_color(self) -> None:
        """Test converting mixed color with different values"""
        result = convert_color_tuple3i_to_hexastr((123, 45, 67))
        self.assertEqual(result, "#7b2d43")

    def test_convert_single_digit_values(self) -> None:
        """Test that single digit values are zero-padded"""
        result = convert_color_tuple3i_to_hexastr((5, 10, 15))
        self.assertEqual(result, "#050a0f")

    def test_convert_invalid_tuple_length(self) -> None:
        """Test that invalid tuple length raises assertion"""
        with self.assertRaises(AssertionError):
            convert_color_tuple3i_to_hexastr((255, 255))  # type: ignore

    def test_convert_negative_value(self) -> None:
        """Test that negative values raise assertion"""
        with self.assertRaises(AssertionError):
            convert_color_tuple3i_to_hexastr((-1, 0, 0))

    def test_convert_value_too_large(self) -> None:
        """Test that values > 255 raise assertion"""
        with self.assertRaises(AssertionError):
            convert_color_tuple3i_to_hexastr((256, 0, 0))


class TestColorPickerWidget(unittest.TestCase):
    """Test suite for ColorPickerWidget"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        # Use a Frame as child of the shared root instead of creating new Tk()
        assert _tk_root is not None
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

    def test_create_color_picker_widget(self) -> None:
        """Test basic ColorPickerWidget creation with default color"""
        callback = Mock()
        widget = ColorPickerWidget(
            tk_frame=self.frame,
            name="Test Color",
            on_change=callback,
        )

        # Check widget was created
        self.assertIsNotNone(widget)
        self.assertIsNotNone(widget.frame)
        self.assertIsNotNone(widget.canvas)
        self.assertIsNotNone(widget.button)

        # Check default color is black
        self.assertEqual(widget.get_current_value(), (0, 0, 0))
        self.assertEqual(widget.canvas["bg"], "#000000")

    def test_create_with_initial_color(self) -> None:
        """Test creating widget with custom initial color"""
        callback = Mock()
        initial_color = (128, 64, 192)
        
        widget = ColorPickerWidget(
            tk_frame=self.frame,
            name="Custom Color",
            on_change=callback,
            initial_color_rgb=initial_color,
        )

        # Check initial color is set correctly
        self.assertEqual(widget.get_current_value(), initial_color)
        self.assertEqual(widget.canvas["bg"], "#8040c0")

    def test_get_current_value(self) -> None:
        """Test get_current_value returns the correct color"""
        callback = Mock()
        initial_color = (100, 150, 200)
        
        widget = ColorPickerWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_color_rgb=initial_color,
        )

        value = widget.get_current_value()
        self.assertEqual(value, initial_color)
        self.assertIsInstance(value, tuple)
        self.assertEqual(len(value), 3)

    def test_callback_with_color_selected(self) -> None:
        """Test callback is called when color is selected"""
        callback = Mock()
        widget = ColorPickerWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_color_rgb=(50, 50, 50),
        )

        # Mock askcolor to return a new color (using integers to match widget's expectations)
        new_color_rgb = (200, 100, 50)
        new_color_hex = "#c86432"
        mock_return = (new_color_rgb, new_color_hex)

        with patch('guibbon.widgets.color_picker_widget.askcolor', return_value=mock_return):
            widget.callback()

        # Check callback was called with the new color
        callback.assert_called_once_with((200, 100, 50))
        
        # Check widget internal state was updated
        self.assertEqual(widget.get_current_value(), (200, 100, 50))

    def test_callback_with_cancel(self) -> None:
        """Test callback when user cancels color picker dialog"""
        callback = Mock()
        initial_color = (50, 50, 50)
        widget = ColorPickerWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_color_rgb=initial_color,
        )

        # Mock askcolor to return None (user cancelled)
        mock_return = (None, None)

        with patch('guibbon.widgets.color_picker_widget.askcolor', return_value=mock_return):
            widget.callback()

        # Callback should still be called (with original color)
        callback.assert_called_once()
        
        # Color should remain unchanged
        self.assertEqual(widget.get_current_value(), initial_color)
        self.assertEqual(widget.canvas["bg"], "#323232")

    def test_canvas_background_updates(self) -> None:
        """Test that canvas background color updates correctly"""
        callback = Mock()
        widget = ColorPickerWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_color_rgb=(0, 0, 0),
        )

        # Check initial background
        self.assertEqual(widget.canvas["bg"], "#000000")

        # Simulate color change
        new_color_rgb = (255, 128, 64)
        new_color_hex = "#ff8040"
        mock_return = (new_color_rgb, new_color_hex)

        with patch('guibbon.widgets.color_picker_widget.askcolor', return_value=mock_return):
            widget.callback()

        # Check background was updated
        self.assertEqual(widget.canvas["bg"], "#ff8040")

    def test_widget_name_displayed(self) -> None:
        """Test that widget displays the correct name"""
        callback = Mock()
        widget_name = "My Color Picker"
        
        widget = ColorPickerWidget(
            tk_frame=self.frame,
            name=widget_name,
            on_change=callback,
        )

        # Find the label widget in the frame
        label_found = False
        for child in widget.frame.winfo_children():
            if isinstance(child, tk.Label):
                if child.cget("text") == widget_name:
                    label_found = True
                    break
        
        self.assertTrue(label_found, f"Label with text '{widget_name}' not found")

    def test_button_text(self) -> None:
        """Test that button has correct text"""
        callback = Mock()
        widget = ColorPickerWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
        )

        self.assertEqual(widget.button.cget("text"), "Edit")

    def test_invalid_initial_color_negative(self) -> None:
        """Test that invalid initial color with negative value raises assertion"""
        callback = Mock()
        
        with self.assertRaises(AssertionError):
            ColorPickerWidget(
                tk_frame=self.frame,
                name="Test",
                on_change=callback,
                initial_color_rgb=(-1, 0, 0),  # type: ignore
            )

    def test_invalid_initial_color_too_large(self) -> None:
        """Test that invalid initial color > 255 raises assertion"""
        callback = Mock()
        
        with self.assertRaises(AssertionError):
            ColorPickerWidget(
                tk_frame=self.frame,
                name="Test",
                on_change=callback,
                initial_color_rgb=(256, 0, 0),  # type: ignore
            )

    def test_invalid_initial_color_wrong_length(self) -> None:
        """Test that initial color with wrong length raises assertion"""
        callback = Mock()
        
        with self.assertRaises(AssertionError):
            ColorPickerWidget(
                tk_frame=self.frame,
                name="Test",
                on_change=callback,
                initial_color_rgb=(255, 255),  # type: ignore
            )

    def test_multiple_color_changes(self) -> None:
        """Test multiple sequential color changes"""
        callback = Mock()
        widget = ColorPickerWidget(
            tk_frame=self.frame,
            name="Test",
            on_change=callback,
            initial_color_rgb=(0, 0, 0),
        )

        # First color change
        color1 = (100, 50, 25)
        with patch('guibbon.widgets.color_picker_widget.askcolor', return_value=(color1, "#64321a")):
            widget.callback()

        self.assertEqual(widget.get_current_value(), color1)

        # Second color change
        color2 = (200, 150, 100)
        with patch('guibbon.widgets.color_picker_widget.askcolor', return_value=(color2, "#c89664")):
            widget.callback()

        self.assertEqual(widget.get_current_value(), color2)

        # Verify callback was called twice
        self.assertEqual(callback.call_count, 2)


if __name__ == "__main__":
    unittest.main()
