import dataclasses
import sys
import tkinter as tk
import unittest
from unittest.mock import Mock

import cv2
import numpy as np
from PIL import ImageTk

from guibbon.image_viewer import ImageViewer, MODE

from guibbon.typedef import Point2DList

from guibbon import transform_matrix as tmat

eps = sys.float_info.epsilon


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


@dataclasses.dataclass
class Event:
    x: int = 0
    y: int = 0
    type: tk.EventType = tk.EventType.Motion
    num: int = 0
    state: int = 0
    delta: int = 0


class EventName:
    CLICK = "<Button-1>"
    DRAG = "<B1-Motion>"
    RELEASE = "<ButtonRelease-1>"
    ENTER = "<Enter>"
    LEAVE = "<Leave>"


class TestImageViewer(unittest.TestCase):
    def setUp(self) -> None:
        self.point_xy = (400, 400)
        self.point_xy_list: Point2DList = []
        self.img = np.zeros(shape=(100, 200), dtype=np.uint8)

        # create an instance of the image viewer using shared root
        assert _tk_root is not None
        self.frame = tk.Frame(_tk_root, width=1000, height=1000)
        self.frame.pack(expand=True, fill='both')
        _tk_root.update_idletasks()
        _tk_root.update()
        
        self.image_viewer = ImageViewer(self.frame, height=1000, width=1000)

        # create 2 interactive points. The second one doesnt implement all callbacks
        self.image_viewer.createInteractivePoint(
            (100, 100), "point0", on_click=self.iteractive_point_event, on_drag=self.iteractive_point_event, on_release=self.iteractive_point_event
        )

        self.image_viewer.createInteractivePoint((200, 200), "point1", on_click=None, on_drag=self.iteractive_point_event, on_release=None)

        # create 2 interactive polygons. The second one doesnt implement all callbacks
        self.image_viewer.createInteractivePolygon(
            [(0, 0), (0, 100), (100, 100)],
            "poly0",
            on_click=self.iteractive_polygon_event,
            on_drag=self.iteractive_polygon_event,
            on_release=self.iteractive_polygon_event,
        )

        self.image_viewer.createInteractivePolygon(
            [(200, 200), (200, 300), (300, 300)], "poly1", on_click=None, on_drag=self.iteractive_polygon_event, on_release=None
        )

        # create 2 interactive rectangles. The second one doesnt implement all callbacks
        self.image_viewer.createInteractiveRectangle(
            (111, 222), (333, 444), "rect0", on_click=self.iteractive_rect_event, on_drag=self.iteractive_rect_event, on_release=self.iteractive_rect_event
        )

        self.image_viewer.createInteractiveRectangle((555, 666), (777, 888), "rect1", on_click=None, on_drag=self.iteractive_rect_event, on_release=None)

        self.iteractive_point_event_count = 0
        self.iteractive_polygon_event_count = 0
        self.iteractive_rect_event_count = 0

        self.image_viewer.imshow(self.img)

    def tearDown(self) -> None:
        # Proper cleanup to avoid tkinter image reference issues
        try:
            assert _tk_root is not None
            self.image_viewer.canvas.delete("all")  # Clear all canvas items
            if hasattr(self.image_viewer, 'imgtk'):
                del self.image_viewer.imgtk
            _tk_root.update_idletasks()
            self.frame.destroy()
        except (Exception, tk.TclError):
            pass

    def iteractive_point_event(self, event):
        self.iteractive_point_event_count += 1
        self.point_xy = (event.x, event.y)

    def iteractive_polygon_event(self, event, point_xy_list):
        self.iteractive_polygon_event_count += 1
        self.point_xy_list = point_xy_list + []

    def iteractive_rect_event(self, event, point0_xy, point1_xy):
        self.iteractive_rect_event_count += 1
        self.point0_xy = point0_xy
        self.point1_xy = point1_xy

    def test_imshow(self):
        expected_zoom = 5
        self.image_viewer.imshow(self.img)
        actual_zoom = self.image_viewer.img2can_matrix[0, 0]
        self.assertEqual(expected_zoom, actual_zoom)

        self.assertIsNotNone(self.image_viewer.imgtk)

    def test_overlay_number(self):
        self.assertEqual(6, len(self.image_viewer.interactive_overlay_instance_list), "2 points and 2 polygons and 2 rectangles are 6 interactives overlays")

    def test_createInteractivePoint(self):
        """
        Make sure the method createInteractivePoint() correctly creates the 2 points
        """
        point0 = self.image_viewer.interactive_overlay_instance_list[0]
        point1 = self.image_viewer.interactive_overlay_instance_list[1]
        x_screen, y_screen = tmat.apply(self.image_viewer.img2can_matrix, (400, 400))
        x_screen, y_screen = int(round(x_screen)), int(round(y_screen))

        self.iteractive_point_event_count = 0
        point0._on_click(Event(x_screen, y_screen))
        self.assertEqual(1, self.iteractive_point_event_count, "Callback should be triggered")
        point0._on_drag(Event(x_screen, y_screen))
        self.assertEqual(2, self.iteractive_point_event_count, "Callback should be triggered")
        point0._on_release(Event(x_screen, y_screen))
        self.assertEqual(3, self.iteractive_point_event_count, "Callback should be triggered")

        self.iteractive_point_event_count = 0
        point1._on_click(Event(x_screen, y_screen))
        self.assertEqual(0, self.iteractive_point_event_count, "Undefined callback should not be triggered")
        point1._on_drag(Event(x_screen, y_screen))
        self.assertEqual(1, self.iteractive_point_event_count, "Callback should be triggered")
        point1._on_release(Event(x_screen, y_screen))
        self.assertEqual(1, self.iteractive_point_event_count, "Undefined callback should not be triggered")

    def test_createInteractivePolygon(self):
        poly0 = self.image_viewer.interactive_overlay_instance_list[2]
        poly1 = self.image_viewer.interactive_overlay_instance_list[3]
        x_screen, y_screen = tmat.apply(self.image_viewer.img2can_matrix, (400, 400))
        x_screen, y_screen = int(round(x_screen)), int(round(y_screen))

        self.iteractive_polygon_event_count = 0
        poly0._on_click(Event(x_screen, y_screen))
        self.assertEqual(1, self.iteractive_polygon_event_count, "Callback should be triggered")
        poly0._on_drag(0, Event(x_screen, y_screen))
        self.assertEqual(2, self.iteractive_polygon_event_count, "Callback should be triggered")
        poly0._on_release(Event(x_screen, y_screen))
        self.assertEqual(3, self.iteractive_polygon_event_count, "Callback should be triggered")

        self.iteractive_polygon_event_count = 0
        poly1._on_click(Event(x_screen, y_screen))
        self.assertEqual(0, self.iteractive_polygon_event_count, "Undefined callback should not be triggered")
        poly1._on_drag(0, Event(x_screen, y_screen))
        self.assertEqual(1, self.iteractive_polygon_event_count, "Callback should be triggered")
        poly1._on_release(Event(x_screen, y_screen))
        self.assertEqual(1, self.iteractive_polygon_event_count, "Undefined callback should not be triggered")

    def test_createInteractiveRectangle(self):
        rect0 = self.image_viewer.interactive_overlay_instance_list[4]
        rect1 = self.image_viewer.interactive_overlay_instance_list[5]
        x_screen, y_screen = tmat.apply(self.image_viewer.img2can_matrix, (400, 400))
        x_screen, y_screen = int(round(x_screen)), int(round(y_screen))

        self.iteractive_rect_event_count = 0
        rect0._on_click(Event(x_screen, y_screen))
        self.assertEqual(1, self.iteractive_rect_event_count, "Callback should be triggered")
        rect0._on_drag(0, Event(x_screen, y_screen))
        self.assertEqual(2, self.iteractive_rect_event_count, "Callback should be triggered")
        rect0._on_release(Event(x_screen, y_screen))
        self.assertEqual(3, self.iteractive_rect_event_count, "Callback should be triggered")

        self.iteractive_rect_event_count = 0
        rect1._on_click(Event(x_screen, y_screen))
        self.assertEqual(0, self.iteractive_rect_event_count, "Undefined callback should not be triggered")
        rect1._on_drag(0, Event(x_screen, y_screen))
        self.assertEqual(1, self.iteractive_rect_event_count, "Callback should be triggered")
        rect1._on_release(Event(x_screen, y_screen))
        self.assertEqual(1, self.iteractive_rect_event_count, "Undefined callback should not be triggered")


class TestImageViewerModes(unittest.TestCase):
    """Test suite for ImageViewer display modes"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        assert _tk_root is not None
        self.frame = tk.Frame(_tk_root, width=1000, height=1000)
        self.frame.pack(expand=True, fill='both')
        _tk_root.update_idletasks()
        _tk_root.update()
        
        self.image_viewer = ImageViewer(self.frame, height=800, width=800)
        self.img = np.zeros(shape=(100, 200, 3), dtype=np.uint8)
        self.img[:, :] = [50, 100, 150]  # BGR color

    def tearDown(self) -> None:
        """Clean up after tests"""
        try:
            assert _tk_root is not None
            self.image_viewer.canvas.delete("all")
            if hasattr(self.image_viewer, 'imgtk'):
                del self.image_viewer.imgtk
            _tk_root.update_idletasks()
            self.frame.destroy()
        except (Exception, tk.TclError):
            pass

    def test_imshow_mode_fit(self) -> None:
        """Test imshow with FIT mode"""
        self.image_viewer.imshow(self.img, mode=MODE.FIT)
        
        # Check mode is set
        self.assertEqual(self.image_viewer.mode, MODE.FIT)
        
        # Check image is displayed
        self.assertIsNotNone(self.image_viewer.imgtk)
        
        # Check zoom factor makes image fit canvas
        canh, canw = self.image_viewer.canvas_shape_hw
        imgh, imgw = self.img.shape[:2]
        expected_zoom = min(canh / imgh, canw / imgw)
        self.assertAlmostEqual(self.image_viewer.zoom_factor, expected_zoom, places=5)

    def test_imshow_mode_fill(self) -> None:
        """Test imshow with FILL mode"""
        self.image_viewer.imshow(self.img, mode=MODE.FILL)
        
        self.assertEqual(self.image_viewer.mode, MODE.FILL)
        self.assertIsNotNone(self.image_viewer.imgtk)
        
        # Check zoom factor makes image fill canvas
        canh, canw = self.image_viewer.canvas_shape_hw
        imgh, imgw = self.img.shape[:2]
        expected_zoom = max(canh / imgh, canw / imgw)
        self.assertAlmostEqual(self.image_viewer.zoom_factor, expected_zoom, places=5)

    def test_imshow_mode_p100(self) -> None:
        """Test imshow with 100% mode"""
        self.image_viewer.imshow(self.img, mode=MODE.P100)
        
        self.assertEqual(self.image_viewer.mode, MODE.P100)
        self.assertIsNotNone(self.image_viewer.imgtk)
        
        # Check zoom factor is 1.0 (100%)
        self.assertEqual(self.image_viewer.zoom_factor, 1.0)

    def test_imshow_float_image(self) -> None:
        """Test imshow with float image (0.0-1.0 range)"""
        float_img = np.random.rand(50, 100, 3).astype(float)
        self.image_viewer.imshow(float_img)
        
        # Should convert float to uint8
        self.assertIsNotNone(self.image_viewer.imgtk)
        self.assertEqual(self.image_viewer.mat.dtype, np.uint8)

    def test_imshow_custom_interpolation(self) -> None:
        """Test imshow with custom cv2 interpolation"""
        self.image_viewer.imshow(self.img, cv2_interpolation=cv2.INTER_NEAREST)
        
        self.assertEqual(self.image_viewer.cv2_interpolation, cv2.INTER_NEAREST)

    def test_onclick_zoom_fit(self) -> None:
        """Test fit button callback"""
        self.image_viewer.imshow(self.img, mode=MODE.P100)
        initial_zoom = self.image_viewer.zoom_factor
        
        self.image_viewer.onclick_zoom_fit()
        
        # Zoom should change to fit mode
        canh, canw = self.image_viewer.canvas_shape_hw
        imgh, imgw = self.img.shape[:2]
        expected_zoom = min(canh / imgh, canw / imgw)
        self.assertAlmostEqual(self.image_viewer.zoom_factor, expected_zoom, places=5)
        self.assertNotEqual(self.image_viewer.zoom_factor, initial_zoom)

    def test_onclick_zoom_fill(self) -> None:
        """Test fill button callback"""
        self.image_viewer.imshow(self.img, mode=MODE.P100)
        _ = self.image_viewer.zoom_factor
        
        self.image_viewer.onclick_zoom_fill()
        
        # Zoom should change to fill mode
        canh, canw = self.image_viewer.canvas_shape_hw
        imgh, imgw = self.img.shape[:2]
        expected_zoom = max(canh / imgh, canw / imgw)
        self.assertAlmostEqual(self.image_viewer.zoom_factor, expected_zoom, places=5)

    def test_onclick_zoom_100(self) -> None:
        """Test 100% button callback"""
        self.image_viewer.imshow(self.img, mode=MODE.FIT)
        
        self.image_viewer.onclick_zoom_100()
        
        self.assertEqual(self.image_viewer.zoom_factor, 1.0)

    def test_onclick_zoom_home(self) -> None:
        """Test home button callback"""
        self.image_viewer.imshow(self.img, mode=MODE.FIT)
        
        # Change pan and zoom
        self.image_viewer.pan_xy = (50.0, 50.0)
        self.image_viewer.zoom_factor = 2.0
        
        self.image_viewer.onclick_zoom_home()
        
        # Should reset to original mode settings
        self.assertEqual(self.image_viewer.pan_xy, (0.0, 0.0))
        canh, canw = self.image_viewer.canvas_shape_hw
        imgh, imgw = self.img.shape[:2]
        expected_zoom = min(canh / imgh, canw / imgw)
        self.assertAlmostEqual(self.image_viewer.zoom_factor, expected_zoom, places=5)

    def test_on_change_zoom_valid(self) -> None:
        """Test zoom entry with valid value"""
        self.image_viewer.imshow(self.img)
        
        self.image_viewer.on_change_zoom("200")
        
        self.assertEqual(self.image_viewer.zoom_factor, 2.0)

    def test_on_change_zoom_invalid(self) -> None:
        """Test zoom entry with invalid value"""
        self.image_viewer.imshow(self.img)
        initial_zoom = self.image_viewer.zoom_factor
        
        self.image_viewer.on_change_zoom("invalid")
        
        # Zoom should not change
        self.assertEqual(self.image_viewer.zoom_factor, initial_zoom)

    def test_on_change_zoom_decimal(self) -> None:
        """Test zoom entry with decimal value"""
        self.image_viewer.imshow(self.img)
        
        self.image_viewer.on_change_zoom("150.5")
        
        self.assertAlmostEqual(self.image_viewer.zoom_factor, 1.505, places=5)


class TestImageViewerMouseCallbacks(unittest.TestCase):
    """Test suite for ImageViewer mouse callbacks"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        assert _tk_root is not None
        self.frame = tk.Frame(_tk_root, width=800, height=800)
        self.frame.pack(expand=True, fill='both')
        _tk_root.update_idletasks()
        _tk_root.update()
        
        self.image_viewer = ImageViewer(self.frame, height=800, width=800)
        self.img = np.zeros(shape=(100, 200, 3), dtype=np.uint8)
        self.image_viewer.imshow(self.img)

    def tearDown(self) -> None:
        """Clean up after tests"""
        try:
            assert _tk_root is not None
            self.image_viewer.canvas.delete("all")
            if hasattr(self.image_viewer, 'imgtk'):
                del self.image_viewer.imgtk
            _tk_root.update_idletasks()
            self.frame.destroy()
        except (Exception, tk.TclError):
            pass

    def test_setMouseCallback_valid(self) -> None:
        """Test setting a valid mouse callback"""
        def callback(event, x, y, flags, param):
            pass
        
        self.image_viewer.setMouseCallback(callback)
        
        self.assertEqual(self.image_viewer.onMouse, callback)

    def test_setMouseCallback_invalid_type(self) -> None:
        """Test that invalid callback type raises TypeError"""
        with self.assertRaises(TypeError):
            self.image_viewer.setMouseCallback("not a function")  # type: ignore

    def test_setMouseCallback_userdata_not_supported(self) -> None:
        """Test that userdata parameter raises NotImplementedError"""
        def callback(event, x, y, flags, param):
            pass
        
        with self.assertRaises(NotImplementedError):
            self.image_viewer.setMouseCallback(callback, userdata="some data")

    def test_mouse_callback_triggered(self) -> None:
        """Test that mouse callback is triggered on events"""
        callback = Mock()
        # Bypass the type check by setting onMouse directly
        self.image_viewer.onMouse = callback
        
        # Simulate a button press event
        event = Event(x=100, y=100)
        event.type = tk.EventType.ButtonPress
        event.num = ImageViewer.BUTTONNUM.LEFT
        event.state = 0
        
        self.image_viewer.on_event(event)
        
        # Callback should have been called
        callback.assert_called_once()

    def test_on_mouse_pan_drag(self) -> None:
        """Test mouse pan drag updates pan position"""
        self.image_viewer.cumulative_pan_xy = (10.0, 20.0)
        
        self.image_viewer.on_mouse_pan_drag((5.0, 5.0), (15.0, 25.0))
        
        expected_pan = (10.0 + 10.0, 20.0 + 20.0)
        self.assertEqual(self.image_viewer.pan_xy, expected_pan)

    def test_on_mouse_pan_release(self) -> None:
        """Test mouse pan release updates cumulative pan"""
        self.image_viewer.pan_xy = (30.0, 40.0)
        
        self.image_viewer.on_mouse_pan_release((0.0, 0.0), (10.0, 10.0))
        
        self.assertEqual(self.image_viewer.cumulative_pan_xy, (30.0, 40.0))


class TestImageViewerMatrix(unittest.TestCase):
    """Test suite for ImageViewer transformation matrices"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        assert _tk_root is not None
        self.frame = tk.Frame(_tk_root, width=800, height=800)
        self.frame.pack(expand=True, fill='both')
        _tk_root.update_idletasks()
        _tk_root.update()
        
        self.image_viewer = ImageViewer(self.frame, height=800, width=800)

    def tearDown(self) -> None:
        """Clean up after tests"""
        try:
            assert _tk_root is not None
            self.image_viewer.canvas.delete("all")
            if hasattr(self.image_viewer, 'imgtk'):
                del self.image_viewer.imgtk
            _tk_root.update_idletasks()
            self.frame.destroy()
        except (Exception, tk.TclError):
            pass

    def test_set_img2can_matrix(self) -> None:
        """Test setting transformation matrix"""
        test_matrix = tmat.identity_matrix()
        test_matrix[0, 2] = 10.0
        test_matrix[1, 2] = 20.0
        
        self.image_viewer.set_img2can_matrix(test_matrix)
        
        # Check img2can matrix is set
        self.assertTrue(np.allclose(self.image_viewer.img2can_matrix, test_matrix))
        
        # Check can2img matrix is inverse
        expected_inverse = np.linalg.inv(test_matrix)
        self.assertTrue(np.allclose(self.image_viewer.can2img_matrix, expected_inverse))

    def test_matrix_is_copied(self) -> None:
        """Test that matrix is copied, not referenced"""
        test_matrix = tmat.identity_matrix()
        original_matrix = test_matrix.copy()
        
        self.image_viewer.set_img2can_matrix(test_matrix)
        
        # Modify original matrix
        test_matrix[0, 0] = 999.0
        
        # ImageViewer's matrix should be unchanged
        self.assertTrue(np.allclose(self.image_viewer.img2can_matrix, original_matrix))


class TestImageViewerInteractiveOverlays(unittest.TestCase):
    """Test suite for creating interactive overlays with magnets"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        assert _tk_root is not None
        self.frame = tk.Frame(_tk_root, width=800, height=800)
        self.frame.pack(expand=True, fill='both')
        _tk_root.update_idletasks()
        _tk_root.update()
        
        self.image_viewer = ImageViewer(self.frame, height=800, width=800)
        self.img = np.zeros(shape=(100, 200, 3), dtype=np.uint8)
        self.image_viewer.imshow(self.img)

    def tearDown(self) -> None:
        """Clean up after tests"""
        try:
            assert _tk_root is not None
            self.image_viewer.canvas.delete("all")
            if hasattr(self.image_viewer, 'imgtk'):
                del self.image_viewer.imgtk
            _tk_root.update_idletasks()
            self.frame.destroy()
        except (Exception, tk.TclError):
            pass

    def test_createInteractivePoint_with_magnets(self) -> None:
        """Test creating interactive point with magnet points"""
        magnet_points = [(50.0, 50.0), (100.0, 100.0), (150.0, 150.0)]
        
        self.image_viewer.createInteractivePoint(
            (75, 75),
            label="test_point",
            magnet_points=magnet_points
        )
        
        # Check point was added
        self.assertEqual(len(self.image_viewer.interactive_overlay_instance_list), 1)
        point = self.image_viewer.interactive_overlay_instance_list[0]
        
        # Check magnets were created
        self.assertIsNotNone(point.magnets)

    def test_createInteractivePolygon_with_magnets(self) -> None:
        """Test creating interactive polygon with magnet points"""
        magnet_points = [(50.0, 50.0), (100.0, 100.0)]
        
        polygon = self.image_viewer.createInteractivePolygon(
            [(10, 10), (20, 20), (30, 10)],
            label="test_polygon",
            magnet_points=magnet_points
        )
        
        # Check polygon was added and returned
        self.assertEqual(len(self.image_viewer.interactive_overlay_instance_list), 1)
        self.assertIsNotNone(polygon)
        # Note: magnets are stored in vertex_list, not as a direct attribute

    def test_createInteractiveRectangle_with_magnets(self) -> None:
        """Test creating interactive rectangle with magnet points"""
        magnet_points = [(50.0, 50.0), (100.0, 100.0)]
        
        rectangle = self.image_viewer.createInteractiveRectangle(
            (10, 10),
            (50, 50),
            label="test_rect",
            magnet_points=magnet_points
        )
        
        # Check rectangle was added and returned
        self.assertEqual(len(self.image_viewer.interactive_overlay_instance_list), 1)
        self.assertIsNotNone(rectangle)
        # Note: magnets are stored in corner vertices, not as a direct attribute

    def test_createInteractivePoint_without_magnets(self) -> None:
        """Test creating interactive point without magnets"""
        self.image_viewer.createInteractivePoint(
            (75, 75),
            label="test_point"
        )
        
        point = self.image_viewer.interactive_overlay_instance_list[0]
        self.assertIsNone(point.magnets)

    def test_multiple_overlays(self) -> None:
        """Test creating multiple overlays"""
        self.image_viewer.createInteractivePoint((10, 10), "point1")
        self.image_viewer.createInteractivePolygon([(20, 20), (30, 30), (40, 20)], "poly1")
        self.image_viewer.createInteractiveRectangle((50, 50), (100, 100), "rect1")
        
        self.assertEqual(len(self.image_viewer.interactive_overlay_instance_list), 3)


class TestImageViewerDraw(unittest.TestCase):
    """Test suite for ImageViewer draw method"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        assert _tk_root is not None
        self.frame = tk.Frame(_tk_root, width=800, height=800)
        self.frame.pack(expand=True, fill='both')
        _tk_root.update_idletasks()
        _tk_root.update()
        
        self.image_viewer = ImageViewer(self.frame, height=800, width=800)

    def tearDown(self) -> None:
        """Clean up after tests"""
        try:
            assert _tk_root is not None
            self.image_viewer.canvas.delete("all")
            if hasattr(self.image_viewer, 'imgtk'):
                del self.image_viewer.imgtk
            _tk_root.update_idletasks()
            self.frame.destroy()
        except (Exception, tk.TclError):
            pass

    def test_draw_without_image(self) -> None:
        """Test draw is called before imshow initializes image"""
        # draw() should handle missing mat gracefully by calling set_panzoom_home
        # which will raise ValueError if mode is not set
        with self.assertRaises((AttributeError, ValueError)):
            self.image_viewer.draw()

    def test_draw_updates_overlays(self) -> None:
        """Test that draw updates all interactive overlays"""
        img = np.zeros(shape=(100, 200, 3), dtype=np.uint8)
        self.image_viewer.imshow(img)
        
        # Create overlays
        self.image_viewer.createInteractivePoint((50, 50), "point1")
        self.image_viewer.createInteractivePolygon([(10, 10), (20, 20), (30, 10)], "poly1")
        
        # Mock the update method to verify it's called
        for overlay in self.image_viewer.interactive_overlay_instance_list:
            overlay.update = Mock()
        
        self.image_viewer.draw()
        
        # Check all overlays were updated
        for overlay in self.image_viewer.interactive_overlay_instance_list:
            overlay.update.assert_called_once()

    def test_draw_creates_photoimage(self) -> None:
        """Test that draw creates a PhotoImage"""
        img = np.zeros(shape=(100, 200, 3), dtype=np.uint8)
        self.image_viewer.imshow(img)
        
        self.assertIsNotNone(self.image_viewer.imgtk)
        self.assertIsInstance(self.image_viewer.imgtk, ImageTk.PhotoImage)


class TestImageViewerEnums(unittest.TestCase):
    """Test suite for ImageViewer enum classes"""

    def test_mode_enum_values(self) -> None:
        """Test MODE enum has expected values"""
        self.assertTrue(hasattr(MODE, 'FIT'))
        self.assertTrue(hasattr(MODE, 'FILL'))
        self.assertTrue(hasattr(MODE, 'P100'))

    def test_buttonnum_enum_values(self) -> None:
        """Test BUTTONNUM enum has expected values"""
        self.assertEqual(ImageViewer.BUTTONNUM.LEFT, 1)
        self.assertEqual(ImageViewer.BUTTONNUM.MID, 2)
        self.assertEqual(ImageViewer.BUTTONNUM.RIGHT, 3)

    def test_modifier_dataclass(self) -> None:
        """Test Modifier dataclass"""
        modifier = ImageViewer.Modifier()
        
        # Check all fields default to False
        self.assertFalse(modifier.SHIFT)
        self.assertFalse(modifier.CONTROL)
        self.assertFalse(modifier.LEFT_ALT)
        
        # Check fields can be set
        modifier.SHIFT = True
        self.assertTrue(modifier.SHIFT)


if __name__ == "__main__":
    unittest.main()
