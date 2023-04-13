import dataclasses
import sys
import tkinter as tk
import unittest

import numpy as np

from tk4cv2.image_viewer import ImageViewer

eps = sys.float_info.epsilon

@dataclasses.dataclass
class Event:
    x: int = 0
    y: int = 0

class EventName:
    CLICK = '<Button-1>'
    DRAG = '<B1-Motion>'
    RELEASE = '<ButtonRelease-1>'
    ENTER = '<Enter>'
    LEAVE = '<Leave>'

class TestImageViewer(unittest.TestCase):
    def setUp(self) -> None:
        self.point_xy = (400, 400)
        self.img = np.zeros(shape=(100, 200), dtype=np.uint8)
        
        # create an instance of the image viewer
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.image_viewer = ImageViewer(self.frame, height=1000, width=1000)

        # create 2 interactive points. The scond one doesnt implement all callbacks
        self.image_viewer.createInteractivePoint((100, 100), "point0",
                on_click=self.iteractive_point_event,
                on_drag=self.iteractive_point_event,
                on_release=self.iteractive_point_event)

        self.image_viewer.createInteractivePoint((200, 200), "point1",
                on_click=None,
                on_drag=self.iteractive_point_event,
                on_release=None)

        self.iteractive_point_event_count = 0

        self.image_viewer.imshow(self.img)

    def tearDown(self) -> None:
        self.root.destroy()

    def iteractive_point_event(self, event):
        self.iteractive_point_event_count += 1
        self.point_xy = (event.x, event.y)


    def test_imshow(self):
        self.image_viewer.imshow(self.img, mode="fit")
        self.assertEqual(self.image_viewer.zoom_factor, 5)

        self.image_viewer.imshow(self.img, mode="fill")
        self.assertEqual(self.image_viewer.zoom_factor, 10)

        self.assertIsNotNone(self.image_viewer.imgtk)


        # print("::::::::::::::::::", binds)
        # self.assertIn(EventName.CLICK, binds)
        # self.assertIn(EventName.DRAG, binds)
        # self.assertIn(EventName.RELEASE, binds)
        # self.assertIn(EventName.ENTER, binds)
        # self.assertIn(EventName.LEAVE, binds)

    def test_createInteractivePoint(self):
        """
        Make sure the method createInteractivePoint() correctly creates the 2 points
        """
        self.assertEqual(2, len(self.image_viewer.interactive_overlays), "Calling createInteractivePoint N times should creates N interactive points")

        point0 = self.image_viewer.interactive_overlays[0]
        point1 = self.image_viewer.interactive_overlays[1]
        x_screen = 400
        y_screen = 400
        x_img, y_img = self.image_viewer.canvas2img_space(x_screen, y_screen)

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

        self.assertNotEqual((x_screen, y_screen), self.point_xy, "Coordinate must be converted in image space")
        self.assertEqual((x_img, y_img), self.point_xy, "Coordinate must be converted in image space")


if __name__ == '__main__':
    unittest.main()
