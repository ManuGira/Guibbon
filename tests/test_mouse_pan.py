import unittest

import numpy as np

from guibbon import mouse_pan
from guibbon import transform_matrix as tmat
import tkinter as tk

EPS = 1e-15


class TestMousePan(unittest.TestCase):
    def reset_counters(self):
        self.on_click_count = 0
        self.on_drag_count = 0
        self.on_release_count = 0

    def on_click(self, p0_xy):
        self.on_click_count += 1
        self.p0_xy = p0_xy

    def on_drag(self, p0_xy, p1_xy):
        self.on_drag_count += 1
        self.p0_xy = p0_xy
        self.p1_xy = p1_xy

    def on_release(self, p0_xy, p1_xy):
        self.on_release_count += 1
        self.p0_xy = p0_xy
        self.p1_xy = p1_xy

    def setUp(self):
        self.on_click_count = 0
        self.on_drag_count = 0
        self.on_release_count = 0
        self.p0_xy = (-1, -1)
        self.p1_xy = (-1, -1)
        self.mp = mouse_pan.MousePan(on_click=self.on_click, on_drag=self.on_drag, on_release=self.on_release)

    def test_MousePan_callback_triggering(self):
        self.assertFalse(self.mp.is_down, "MousePan.is_down must be initialized to False")
        event = tk.Event()
        event.x = 1
        event.y = 1

        self.reset_counters()
        event.type = tk.EventType.Motion
        self.mp.on_tk_event(event, tmat.identity_matrix())
        self.assertFalse(self.mp.is_down, 'is_down should remain the same on "Motion" event')
        self.assertEqual(self.on_click_count, 0, 'on_click callback must NOT be triggered with EventType "Motion" when is_down is False')
        self.assertEqual(self.on_drag_count, 0, 'on_drag callback must NOT be triggered with EventType "Motion" when is_down is False')
        self.assertEqual(self.on_release_count, 0, 'on_release callback must NOT be triggered with EventType "Motion" when is_down is False')

        self.reset_counters()
        event.type = tk.EventType.ButtonRelease
        self.mp.on_tk_event(event, tmat.identity_matrix())
        self.assertFalse(self.mp.is_down, '"ButtonRelease" event should have no effect when NOT is_down')
        self.assertEqual(self.on_click_count, 0, 'on_click callback must NOT be triggered with EventType "ButtonRelease" when is_down is False')
        self.assertEqual(self.on_drag_count, 0, 'on_drag callback must NOT be triggered with EventType "ButtonRelease" when is_down is False')
        self.assertEqual(self.on_release_count, 0, 'on_release callback must NOT be triggered with EventType "ButtonRelease" when is_down is False')

        self.reset_counters()
        event.type = tk.EventType.ButtonPress
        self.mp.on_tk_event(event, tmat.identity_matrix())
        self.assertTrue(self.mp.is_down, '"ButtonPress" event should should set "isdown" to True')
        self.assertEqual(self.on_click_count, 1, 'on_click callback must be triggered with EventType "ButtonPress')
        self.assertEqual(self.on_drag_count, 0, 'on_drag callback must NOT be triggered with EventType "ButtonPress')
        self.assertEqual(self.on_release_count, 0, 'on_release callback must NOT be triggered with EventType "ButtonPress')

        self.reset_counters()
        event.type = tk.EventType.Motion
        self.mp.on_tk_event(event, tmat.identity_matrix())
        self.assertTrue(self.mp.is_down, 'is_down should remain the same on "Motion" event')
        self.assertEqual(self.on_click_count, 0, 'on_click callback must NOT be triggered with EventType "Motion"')
        self.assertEqual(self.on_drag_count, 1, 'on_drag callback must be triggered with EventType "Motion')
        self.assertEqual(self.on_release_count, 0, 'on_release callback must NOT be triggered with EventType "Motion')

        self.reset_counters()
        event.type = tk.EventType.ButtonRelease
        self.mp.on_tk_event(event, tmat.identity_matrix())
        self.assertFalse(self.mp.is_down, 'is_down should be False after "ButtonRelease"')
        self.assertEqual(self.on_click_count, 0, 'on_click callback must NOT be triggered with EventType "ButtonRelease" when is_down is False')
        self.assertEqual(self.on_drag_count, 0, 'on_drag callback must NOT be triggered with EventType "ButtonRelease" when is_down is False')
        self.assertEqual(self.on_release_count, 1, 'on_release callback must be triggered with EventType "ButtonRelease" when is_down is False')

    def test_MousePan_values(self):
        def tuple_is_same(tup1, tup2, eps=EPS):
            return tuple(abs(v1 - v2) < eps for v1, v2 in zip(tup1, tup2))

        event = tk.Event()
        x0, y0 = 11, 22
        x1, y1 = 111, 222
        event.x, event.y = x0, y0

        sx, sy = (3, 4)
        scale_mat = tmat.scale_matrix((sx, sy))

        event.type = tk.EventType.ButtonPress
        self.mp.on_tk_event(event, scale_mat)
        self.assertTupleEqual((x0, y0), (event.x, event.y), "MousePan must NOT modify the event value passed as argument")
        self.assertTupleEqual(tuple_is_same((sx * x0, sy * y0), self.mp.p0_xy), (True, True), "MousePan must correctly convert canvas coordinates to image coordinates")
        self.assertTupleEqual(tuple_is_same((sx * x0, sy * y0), self.mp.p1_xy), (True, True), "MousePan must correctly convert canvas coordinates to image coordinates")

        event.type = tk.EventType.Motion
        event.x, event.y = x1, y1
        self.mp.on_tk_event(event, scale_mat)
        self.assertTupleEqual((x1, y1), (event.x, event.y), "MousePan must NOT modify the event value passed as argument")
        self.assertTupleEqual(tuple_is_same((sx * x0, sy * y0), self.mp.p0_xy), (True, True), "MousePan must correctly convert canvas coordinates to image coordinates")
        self.assertTupleEqual(tuple_is_same((sx * x1, sy * y1), self.mp.p1_xy), (True, True), "MousePan must correctly convert canvas coordinates to image coordinates")

        event.type = tk.EventType.ButtonRelease
        self.mp.on_tk_event(event, scale_mat)
        self.assertTupleEqual((x1, y1), (event.x, event.y), "MousePan must NOT modify the event value passed as argument")
        self.assertTupleEqual(tuple_is_same((sx * x0, sy * y0), self.mp.p0_xy), (True, True), "MousePan must correctly convert canvas coordinates to image coordinates")
        self.assertTupleEqual(tuple_is_same((sx * x1, sy * y1), self.mp.p1_xy), (True, True), "MousePan must correctly convert canvas coordinates to image coordinates")


if __name__ == "__main__":
    unittest.main()
