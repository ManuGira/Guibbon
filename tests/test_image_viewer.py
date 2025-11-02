import dataclasses
import sys
import tkinter as tk
import unittest

import numpy as np

from guibbon.image_viewer import ImageViewer

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


if __name__ == "__main__":
    unittest.main()
