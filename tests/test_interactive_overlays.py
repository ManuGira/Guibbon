import dataclasses
import sys
import tkinter
import unittest
from tk4cv2 import interactive_overlays

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

class TestPoint(unittest.TestCase):
    def setUp(self) -> None:
        self.event_count = 0
        self.drag_count = 0
        self.release_count = 0
        self.x = 0
        self.y = 0

        self.canvas = tkinter.Canvas()

    def tearDown(self) -> None:
        pass

    def on_event(self, event):
        self.event_count += 1
        self.x = event.x
        self.y = event.y

    def on_event_error(self, event):
        raise

    def test_callback(self):
        self.pt = interactive_overlays.Point(
            canvas=self.canvas,
            x=self.x,
            y=self.y,
            label="ok",
            on_click=self.on_event,
            on_drag=self.on_event,
            on_release=self.on_event)

        binds = self.canvas.tag_bind(self.pt.circle_id)
        self.assertIn(EventName.CLICK, binds)
        self.assertIn(EventName.DRAG, binds)
        self.assertIn(EventName.RELEASE, binds)
        self.assertIn(EventName.ENTER, binds)
        self.assertIn(EventName.LEAVE, binds)

        self.assertEqual(self.event_count, 0)
        self.assertEqual(self.x, 0)
        self.assertEqual(self.y, 0)

        event = Event(x=11, y=12)
        self.pt._on_click(event)

        self.assertEqual(self.event_count, 1)
        self.assertEqual(self.x, 11)
        self.assertEqual(self.y, 12)

        event = Event(x=21, y=22)
        self.pt._on_drag(event)

        self.assertEqual(self.event_count, 2)
        self.assertEqual(self.x, 21)
        self.assertEqual(self.y, 22)

        event = Event(x=31, y=32)
        self.pt._on_release(event)

        self.assertEqual(self.event_count, 3)
        self.assertEqual(self.x, 31)
        self.assertEqual(self.y, 32)


    def test_none_callback(self):
        self.pt = interactive_overlays.Point(canvas=self.canvas, x=self.x, y=self.y, label="ok",
                on_click=None,
                on_drag=None,
                on_release=None)

        binds = self.canvas.tag_bind(self.pt.circle_id)
        self.assertIn(EventName.CLICK, binds)
        self.assertIn(EventName.DRAG, binds)
        self.assertIn(EventName.RELEASE, binds)
        self.assertIn(EventName.ENTER, binds)
        self.assertIn(EventName.LEAVE, binds)

        self.assertEqual(self.event_count, 0)
        self.assertEqual(self.x, 0)
        self.assertEqual(self.y, 0)

        event = Event(123, 456)
        self.pt._on_click(event)
        self.pt._on_drag(event)
        self.pt._on_release(event)

        self.assertEqual(self.event_count, 0)
        self.assertEqual(self.x, 0)
        self.assertEqual(self.y, 0)

    def test_event_sequence(self):
        self.pt = interactive_overlays.Point(canvas=self.canvas, x=self.x, y=self.y, label="ok",
            on_click=None,
            on_drag=None,
            on_release=None)
        event = Event(0, 0)

        self.assertEqual(self.pt.state, interactive_overlays.Point.State.NORMAL)

        self.pt._on_enter(event)
        self.assertEqual(self.pt.state, interactive_overlays.Point.State.HOVERED)

        self.pt._on_click(event)
        self.assertEqual(self.pt.state, interactive_overlays.Point.State.DRAGGED)

        self.pt._on_drag(event)
        self.assertEqual(self.pt.state, interactive_overlays.Point.State.DRAGGED)

        self.pt._on_release(event)
        self.assertEqual(self.pt.state, interactive_overlays.Point.State.HOVERED)

        self.pt._on_leave(event)
        self.assertEqual(self.pt.state, interactive_overlays.Point.State.NORMAL)

    def test_event_raise(self):
        self.pt = interactive_overlays.Point(canvas=self.canvas, x=self.x, y=self.y, label="ok",
            on_click=None,
            on_drag=self.on_event_error,
            on_release=None)
        event = Event(0, 0)

        with self.assertRaises(Exception):
            self.pt._on_drag(event)


if __name__ == '__main__':
    unittest.main()
