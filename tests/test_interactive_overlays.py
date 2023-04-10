import sys
import tkinter
import unittest
import cv2
import tk4cv2 as tcv2
import numpy as np
import tkinter as tk
from tk4cv2 import interactive_overlays

eps = sys.float_info.epsilon

class TestPoint(unittest.TestCase):
    click_count = 0
    drag_count = 0
    release_count = 0

    def on_click(self, event):
        TestPoint.click_count += 1

    def on_drag(self, event):
        TestPoint.drag_count += 1

    def on_release(self, event):
        TestPoint.reease_count += 1

    def tearDown(self) -> None:
        pass

    def setUp(self) -> None:
        self.canvas = tkinter.Canvas()
        self.pt = interactive_overlays.Point(
            canvas=self.canvas,
            x=0,
            y=0,
            label="ok",
            on_click=self.on_click,
            on_drag=self.on_drag,
            on_release=self.on_release)
        self.assertIsNotNone(self.pt)
        self.assertIsNotNone(self.pt.canvas)
        self.assertIsNotNone(self.pt.x)
        self.assertIsNotNone(self.pt.y)
        self.assertIsNotNone(self.pt.label)

        # x1, y1, x2, y2 = self.canvas.coords(self.circle_id)
        # self.assertEqual((x1+x2)/2, 0)
        # self.assertEqual((y1+y2)/2, 0)

    def test_callback(self):
        self.assertIsNotNone(self.pt)
        # TODO:
        self.assertIsNotNone(None)

if __name__ == '__main__':
    unittest.main()
