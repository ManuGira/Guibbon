import unittest
import tkinter as tk
from guibbon.widgets.multi_slider_widget import MultiSliderOverlay


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


class TestMultiSliderOverlay(unittest.TestCase):
    def setUp(self):
        # Use the shared root and create a canvas as a child
        self.canvas = tk.Canvas(_tk_root, width=200, height=30)
        self.callback_count = 0
        self.last_positions_values = None

    def tearDown(self):
        try:
            self.canvas.destroy()
        except tk.TclError:
            pass

    def callback(self, positions_values):
        self.callback_count += 1
        self.last_positions_values = positions_values

    def test_create_overlay(self):
        """Test basic creation of MultiSliderOverlay"""
        values = list(range(10))
        initial_positions = [2, 5]
        
        overlay = MultiSliderOverlay(
            canvas=self.canvas,
            values=values,
            initial_positions=initial_positions,
            on_drag=self.callback,
            on_release=self.callback
        )
        
        self.assertEqual(len(overlay.cursors), 2)
        self.assertEqual(overlay.get_positions(), initial_positions)

    def test_canvas_to_slider_conversion(self):
        """Test coordinate conversion from canvas to slider"""
        values = list(range(10))
        initial_positions = [0]
        
        overlay = MultiSliderOverlay(
            canvas=self.canvas,
            values=values,
            initial_positions=initial_positions
        )
        
        # Update canvas to get proper dimensions
        self.canvas.update_idletasks()
        
        # Test conversion (basic sanity check)
        slider_point = overlay.canvas2slider((100, 15))
        self.assertIsInstance(slider_point, tuple)
        self.assertEqual(len(slider_point), 2)
        
        # x should be within valid range
        x, y = slider_point
        self.assertGreaterEqual(x, 0)
        self.assertLessEqual(x, len(values) - 1)

    def test_slider_to_canvas_conversion(self):
        """Test coordinate conversion from slider to canvas"""
        values = list(range(10))
        initial_positions = [0]
        
        overlay = MultiSliderOverlay(
            canvas=self.canvas,
            values=values,
            initial_positions=initial_positions
        )
        
        # Update canvas to get proper dimensions
        self.canvas.update_idletasks()
        
        # Test conversion
        canvas_point = overlay.slider2canvas((5, 0))
        self.assertIsInstance(canvas_point, tuple)
        self.assertEqual(len(canvas_point), 2)
        
        # Coordinates should be within canvas bounds
        x, y = canvas_point
        self.assertGreaterEqual(x, 0)
        self.assertLessEqual(x, self.canvas.winfo_width())


if __name__ == "__main__":
    unittest.main()
