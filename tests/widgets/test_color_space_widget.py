import unittest
import tkinter as tk

from guibbon.widgets.color_space_widget import ColorSpaceWidget, ColorSpace


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


class TestColorSpaceWidget(unittest.TestCase):
    """Test suite for ColorSpaceWidget"""

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

    def test_create_color_space_widget(self) -> None:
        """Test basic ColorSpaceWidget creation"""
        initial_color_space: ColorSpace = [(100, 100, 55), (155, 155, 200)]
        
        widget = ColorSpaceWidget(
            tk_frame=self.frame,
            color_space_name="Test Color Space",
            initial_color_space=initial_color_space,
        )
        
        # Verify widget was created
        self.assertIsNotNone(widget)
        self.assertEqual(widget.M, 2)
        self.assertEqual(len(widget.multi_slider_overlays), 3)  # RGB channels
        
        # Verify color space was properly stored
        self.assertEqual(len(widget.color_space), 2)
        self.assertEqual(widget.color_space[0], (100, 100, 55))
        self.assertEqual(widget.color_space[1], (155, 155, 200))

    def test_get_color_space(self) -> None:
        """Test getting the color space returns a copy"""
        initial_color_space: ColorSpace = [(50, 60, 70), (205, 195, 185)]
        
        widget = ColorSpaceWidget(
            tk_frame=self.frame,
            color_space_name="Test",
            initial_color_space=initial_color_space,
        )
        
        color_space = widget.get_color_space()
        
        # Verify we get a copy (not the same list)
        self.assertIsNot(color_space, widget.color_space)
        self.assertEqual(color_space, [(50, 60, 70), (205, 195, 185)])
        
        # Modifying returned list shouldn't affect widget
        color_space.append((0, 0, 0))
        self.assertEqual(len(widget.color_space), 2)

    def test_callbacks_none(self) -> None:
        """Test widget works with no callbacks"""
        initial_color_space: ColorSpace = [(128, 128, 127), (127, 127, 128)]
        
        widget = ColorSpaceWidget(
            tk_frame=self.frame,
            color_space_name="Test",
            initial_color_space=initial_color_space,
            on_drag=None,
            on_release=None,
        )
        
        # Should not raise any exceptions
        widget.on_drag_callback(0, [(100, 100)])
        widget.on_release_callback([(100, 100)])

    def test_on_drag_callback(self) -> None:
        """Test on_drag callback is called correctly"""
        initial_color_space: ColorSpace = [(100, 100, 100), (155, 155, 155)]
        
        callback_data = []
        def on_drag(color_space: ColorSpace) -> None:
            callback_data.append(("drag", color_space))
        
        widget = ColorSpaceWidget(
            tk_frame=self.frame,
            color_space_name="Test",
            initial_color_space=initial_color_space,
            on_drag=on_drag,
        )
        
        # Simulate drag callback
        widget.on_drag_callback(0, [(50, 50)])
        
        # Verify callback was called
        self.assertEqual(len(callback_data), 1)
        self.assertEqual(callback_data[0][0], "drag")
        self.assertIsInstance(callback_data[0][1], list)

    def test_on_release_callback(self) -> None:
        """Test on_release callback is called correctly"""
        initial_color_space: ColorSpace = [(100, 100, 100), (155, 155, 155)]
        
        callback_data = []
        def on_release(color_space: ColorSpace) -> None:
            callback_data.append(("release", color_space))
        
        widget = ColorSpaceWidget(
            tk_frame=self.frame,
            color_space_name="Test",
            initial_color_space=initial_color_space,
            on_release=on_release,
        )
        
        # Simulate release callback
        widget.on_release_callback([(50, 50)])
        
        # Verify callback was called
        self.assertEqual(len(callback_data), 1)
        self.assertEqual(callback_data[0][0], "release")
        self.assertIsInstance(callback_data[0][1], list)

    def test_update_color_space(self) -> None:
        """Test update_color_space updates the internal color space"""
        initial_color_space: ColorSpace = [(100, 50, 25), (155, 205, 230)]
        
        widget = ColorSpaceWidget(
            tk_frame=self.frame,
            color_space_name="Test",
            initial_color_space=initial_color_space,
        )
        
        # Call update_color_space
        widget.update_color_space()
        
        # Verify color_space is updated
        self.assertIsNotNone(widget.color_space)
        self.assertIsInstance(widget.color_space, list)

    def test_widget_color_parameter(self) -> None:
        """Test widget_color parameter is accepted"""
        initial_color_space: ColorSpace = [(128, 128, 128), (127, 127, 127)]
        
        widget = ColorSpaceWidget(
            tk_frame=self.frame,
            color_space_name="Test",
            initial_color_space=initial_color_space,
            widget_color="#FFFFFF",
        )
        
        self.assertIsNotNone(widget)


class TestColorSpaceConversion(unittest.TestCase):
    """Test suite for ColorSpaceWidget static conversion methods"""

    def test_rgb_segments_to_color_space_simple(self) -> None:
        """Test conversion from RGB segments to color space"""
        red_segments = [100]
        green_segments = [150]
        blue_segments = [200]
        
        color_space = ColorSpaceWidget.rgb_segments_to_color_space(
            red_segments, green_segments, blue_segments
        )
        
        # Expected: [(100, 150, 200), (155, 105, 55)]
        # First segment: (100, 150, 200) - (0, 0, 0)
        # Second segment: (255, 255, 255) - (100, 150, 200)
        self.assertEqual(len(color_space), 2)
        self.assertEqual(color_space[0], (100, 150, 200))
        self.assertEqual(color_space[1], (155, 105, 55))

    def test_rgb_segments_to_color_space_multiple(self) -> None:
        """Test conversion with multiple segments"""
        red_segments = [50, 100]
        green_segments = [60, 120]
        blue_segments = [70, 140]
        
        color_space = ColorSpaceWidget.rgb_segments_to_color_space(
            red_segments, green_segments, blue_segments
        )
        
        # Expected deltas:
        # Segment 0: (50, 60, 70) - (0, 0, 0) = (50, 60, 70)
        # Segment 1: (100, 120, 140) - (50, 60, 70) = (50, 60, 70)
        # Segment 2: (255, 255, 255) - (100, 120, 140) = (155, 135, 115)
        self.assertEqual(len(color_space), 3)
        self.assertEqual(color_space[0], (50, 60, 70))
        self.assertEqual(color_space[1], (50, 60, 70))
        self.assertEqual(color_space[2], (155, 135, 115))

    def test_color_space_to_rgb_segments_simple(self) -> None:
        """Test conversion from color space to RGB segments"""
        color_space: ColorSpace = [(100, 150, 200), (155, 105, 55)]
        
        red_segs, green_segs, blue_segs = ColorSpaceWidget.color_space_to_rgb_segments(
            color_space
        )
        
        # Expected cumulative sums (excluding final 255):
        # After (100, 150, 200): RGB = (100, 150, 200)
        # After (155, 105, 55): RGB = (255, 255, 255) - excluded
        self.assertEqual(red_segs, [100])
        self.assertEqual(green_segs, [150])
        self.assertEqual(blue_segs, [200])

    def test_color_space_to_rgb_segments_multiple(self) -> None:
        """Test conversion with multiple segments"""
        color_space: ColorSpace = [(50, 60, 70), (50, 60, 70), (155, 135, 115)]
        
        red_segs, green_segs, blue_segs = ColorSpaceWidget.color_space_to_rgb_segments(
            color_space
        )
        
        # Expected cumulative sums (excluding final 255):
        # After (50, 60, 70): RGB = (50, 60, 70)
        # After (50, 60, 70): RGB = (100, 120, 140)
        # After (155, 135, 115): RGB = (255, 255, 255) - excluded
        self.assertEqual(red_segs, [50, 100])
        self.assertEqual(green_segs, [60, 120])
        self.assertEqual(blue_segs, [70, 140])

    def test_conversion_roundtrip(self) -> None:
        """Test that conversion roundtrip preserves data"""
        # Start with RGB segments
        red_segments = [80, 160]
        green_segments = [90, 180]
        blue_segments = [100, 200]
        
        # Convert to color space
        color_space = ColorSpaceWidget.rgb_segments_to_color_space(
            red_segments, green_segments, blue_segments
        )
        
        # Convert back to RGB segments
        red_back, green_back, blue_back = ColorSpaceWidget.color_space_to_rgb_segments(
            color_space
        )
        
        # Should match original (sorted)
        self.assertEqual(red_back, sorted(red_segments))
        self.assertEqual(green_back, sorted(green_segments))
        self.assertEqual(blue_back, sorted(blue_segments))

    def test_rgb_segments_sorted_automatically(self) -> None:
        """Test that RGB segments are automatically sorted"""
        # Unsorted segments
        red_segments = [100, 50]
        green_segments = [150, 75]
        blue_segments = [200, 100]
        
        color_space = ColorSpaceWidget.rgb_segments_to_color_space(
            red_segments, green_segments, blue_segments
        )
        
        # Convert back - should be sorted
        red_back, green_back, blue_back = ColorSpaceWidget.color_space_to_rgb_segments(
            color_space
        )
        
        self.assertEqual(red_back, [50, 100])
        self.assertEqual(green_back, [75, 150])
        self.assertEqual(blue_back, [100, 200])

    def test_empty_segments(self) -> None:
        """Test conversion with empty segments (only 255)"""
        red_segments: list[int] = []
        green_segments: list[int] = []
        blue_segments: list[int] = []
        
        color_space = ColorSpaceWidget.rgb_segments_to_color_space(
            red_segments, green_segments, blue_segments
        )
        
        # Should have one segment: (255, 255, 255) - (0, 0, 0)
        self.assertEqual(len(color_space), 1)
        self.assertEqual(color_space[0], (255, 255, 255))

    def test_single_color_full_intensity(self) -> None:
        """Test color space with single full intensity color"""
        color_space: ColorSpace = [(255, 255, 255)]
        
        red_segs, green_segs, blue_segs = ColorSpaceWidget.color_space_to_rgb_segments(
            color_space
        )
        
        # All segments should be empty (final 255 is removed)
        self.assertEqual(red_segs, [])
        self.assertEqual(green_segs, [])
        self.assertEqual(blue_segs, [])


if __name__ == "__main__":
    unittest.main()
