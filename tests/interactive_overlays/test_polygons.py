import dataclasses
import sys
import tkinter
import unittest

from guibbon import interactive_overlays
from guibbon.typedef import InteractivePolygon

eps = sys.float_info.epsilon


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



class TestPolygon(unittest.TestCase):
    def setUp(self) -> None:
        self.event_count = 0
        self.drag_count = 0
        self.release_count = 0
        self.point_xy_list = [
            (0.0, 0.0),
            (0.0, 100.0),
            (100.0, 100.0),
        ]
        self.event = None

        self.canvas = tkinter.Canvas()

    def tearDown(self) -> None:
        pass

    def on_event(self, event, point_xy_list):
        self.event_count += 1
        self.point_xy_list = point_xy_list + []

    def on_event_error(self, event, point_xy_list):
        raise

    def test_interface(self):
        self.plg = interactive_overlays.Polygon(canvas=self.canvas, point_xy_list=self.point_xy_list)
        self.assertIsInstance(self.plg, InteractivePolygon)

    def test_callback(self):
        point_xy_list_bck = self.point_xy_list + []

        self.plg = interactive_overlays.Polygon(
            canvas=self.canvas, point_xy_list=self.point_xy_list, label="ok", on_click=self.on_event, on_drag=self.on_event, on_release=self.on_event
        )

        self.assertEqual(len(self.plg.ipoints), len(self.point_xy_list), "Polygon must have 1 Interactive Point instance for each point in point_xy_list")

        for k in range(len(self.plg.ipoints)):
            binds = self.canvas.tag_bind(self.plg.ipoints[k].circle_id)
            self.assertIn(EventName.CLICK, binds, f"{EventName.CLICK} tag not binded")
            self.assertIn(EventName.DRAG, binds, f"{EventName.DRAG} tag not binded")
            self.assertIn(EventName.RELEASE, binds, f"{EventName.RELEASE} tag not binded")
            self.assertIn(EventName.ENTER, binds, f"{EventName.ENTER} tag not binded")
            self.assertIn(EventName.LEAVE, binds, f"{EventName.LEAVE} tag not binded")

        self.assertEqual(0, self.event_count)
        self.assertEqual(point_xy_list_bck, self.point_xy_list, "point_xy_list should not change at Polygon creation")

        point_xy_list_bck = self.point_xy_list + []
        event = Event(x=11, y=12)
        self.plg._on_click(event)
        self.assertEqual(1, self.event_count)
        self.assertEqual(point_xy_list_bck, self.point_xy_list, "_on_click should not change point_xy_list")

        event = Event(x=21, y=22)
        k = 0
        self.plg._on_drag(k, event)
        self.assertEqual(2, self.event_count, "Event must not be triggered")
        self.assertEqual(point_xy_list_bck, self.point_xy_list, "_on_drag should not change point_xy_list (on_drag of Point should)")

        event = Event(x=31, y=32)
        k = 1
        self.plg._on_drag(k, event)
        self.assertEqual(3, self.event_count, "Event must not be triggered")
        self.assertEqual(point_xy_list_bck, self.point_xy_list, "_on_drag should not change point_xy_list (on_drag of Point should)")

        event = Event(x=41, y=42)
        point_xy_list_bck = self.point_xy_list + []
        self.plg._on_release(event)
        self.assertEqual(4, self.event_count, "Event must not be triggered")
        self.assertEqual(point_xy_list_bck, self.point_xy_list, "_on_release should not change point_xy_list")

    def test_none_callback(self):
        point_xy_list_bck = self.point_xy_list + []

        self.plg = interactive_overlays.Polygon(canvas=self.canvas, point_xy_list=self.point_xy_list, label="ok", on_click=None, on_drag=None, on_release=None)

        for k in range(len(self.plg.ipoints)):
            binds = self.canvas.tag_bind(self.plg.ipoints[k].circle_id)
            self.assertIn(EventName.CLICK, binds, f"{EventName.CLICK} tag not binded")
            self.assertIn(EventName.DRAG, binds, f"{EventName.DRAG} tag not binded")
            self.assertIn(EventName.RELEASE, binds, f"{EventName.RELEASE} tag not binded")
            self.assertIn(EventName.ENTER, binds, f"{EventName.ENTER} tag not binded")
            self.assertIn(EventName.LEAVE, binds, f"{EventName.LEAVE} tag not binded")

        self.assertEqual(0, self.event_count, "Event should not be triggered")
        self.assertEqual(point_xy_list_bck, self.point_xy_list, "point_xy_list should not change at Polygon creation")

        event = Event(123, 456)
        self.plg._on_click(event)
        self.plg._on_drag(0, event)
        self.plg._on_release(event)

        self.assertEqual(0, self.event_count, "Event should not be triggered")
        self.assertEqual(point_xy_list_bck, self.point_xy_list, "those callbacks should not be able to change self.point_xy_list")

    def test_event_sequence(self):
        self.plg = interactive_overlays.Polygon(canvas=self.canvas, point_xy_list=self.point_xy_list, label="ok", on_click=None, on_drag=None, on_release=None)
        event = Event(0, 0)

        for k, pt in enumerate(self.plg.ipoints):
            self.assertEqual(interactive_overlays.State.NORMAL, pt.state, f"polygon.ipoints[{k}] must interact")

            pt._on_enter(event)
            self.assertEqual(interactive_overlays.State.HOVERED, pt.state, f"polygon.ipoints[{k}] must interact")

            pt._on_click(event)
            self.assertEqual(interactive_overlays.State.DRAGGED, pt.state, f"polygon.ipoints[{k}] must interact")

            pt._on_drag(event)
            self.assertEqual(interactive_overlays.State.DRAGGED, pt.state, f"polygon.ipoints[{k}] must interact")

            pt._on_release(event)
            self.assertEqual(interactive_overlays.State.HOVERED, pt.state, f"polygon.ipoints[{k}] must interact")

            pt._on_leave(event)
            self.assertEqual(interactive_overlays.State.NORMAL, pt.state, f"polygon.ipoints[{k}] must interact")

    def test_event_raise(self):
        self.plg = interactive_overlays.Polygon(
            canvas=self.canvas, point_xy_list=self.point_xy_list, label="ok", on_click=None, on_drag=self.on_event_error, on_release=None
        )
        event = Event(0, 0)

        with self.assertRaises(Exception):
            self.plg._on_drag(0, event)

    def test_visible(self):
        expected_state = {True: "normal", False: "hidden"}
        self.plg = interactive_overlays.Polygon(canvas=self.canvas, point_xy_list=self.point_xy_list, label="ok")

        self.plg.update()
        self.assertTrue(self.plg.visible, msg="Polygon must be visible by default")
        for ipoint in self.plg.ipoints:
            self.assertTrue(ipoint.visible, msg="Polygon's points must be visible by default")

        for _, _, line_id in self.plg.lines:
            state = self.canvas.itemcget(line_id, "state")
            self.assertEqual(expected_state[True], state, msg="Polygon's lines must be visible by default")

        for val in [False, False, True, True]:
            self.plg.set_visible(val)
            self.plg.update()
            self.assertEqual(self.plg.visible, val, msg="set_visible function must work properly")

            for ipoint in self.plg.ipoints:
                self.assertEqual(ipoint.visible, val, msg="Polygon's points must be visible by default")

            for _, _, line_id in self.plg.lines:
                state = self.canvas.itemcget(line_id, "state")
                self.assertEqual(state, expected_state[val], msg="set_visible function must work properly")

            self.assertEqual(self.plg.visible, val)


class TestRectangle(unittest.TestCase):
    def setUp(self) -> None:
        self.event_count = 0
        self.drag_count = 0
        self.release_count = 0
        self.point0_xy = (0.0, 0.0)
        self.point1_xy = (100.0, 100.0)

        self.event = None
        self.canvas = tkinter.Canvas()

        self.magnets = interactive_overlays.Magnets(self.canvas, [(110.0, 110.0)], (lambda x, y: (2 * x, 2 * y)))

    def tearDown(self) -> None:
        pass

    def on_event(self, event, point0_xy, point1_xy):
        self.event_count += 1
        self.point0_xy = point0_xy
        self.point1_xy = point1_xy

    def on_event_error(self, event, point0_xy, point1_xy):
        raise

    def test_interface(self):
        self.rect = interactive_overlays.Rectangle(canvas=self.canvas, point0_xy=self.point0_xy, point1_xy=self.point1_xy)
        self.assertIsInstance(self.rect, InteractivePolygon)

    def test_callback(self):
        point0_xy_bck = self.point0_xy
        point1_xy_bck = self.point1_xy

        self.rect = interactive_overlays.Rectangle(
            canvas=self.canvas,
            point0_xy=self.point0_xy,
            point1_xy=self.point1_xy,
            label="ok",
            on_click=self.on_event,
            on_drag=self.on_event,
            on_release=self.on_event,
        )

        self.assertEqual(2, len(self.rect.ipoints), "Rectangle must have 2 Interactive Point instances")

        for k in range(2):
            binds = self.canvas.tag_bind(self.rect.ipoints[k].circle_id)
            self.assertIn(EventName.CLICK, binds, f"{EventName.CLICK} tag not binded")
            self.assertIn(EventName.DRAG, binds, f"{EventName.DRAG} tag not binded")
            self.assertIn(EventName.RELEASE, binds, f"{EventName.RELEASE} tag not binded")
            self.assertIn(EventName.ENTER, binds, f"{EventName.ENTER} tag not binded")
            self.assertIn(EventName.LEAVE, binds, f"{EventName.LEAVE} tag not binded")

        self.assertEqual(0, self.event_count)
        self.assertEqual(point0_xy_bck, self.point0_xy, "point0_xy should not change at Rectangle creation")
        self.assertEqual(point1_xy_bck, self.point1_xy, "point1_xy should not change at Rectangle creation")

        point0_xy_bck = self.point0_xy
        point1_xy_bck = self.point1_xy
        event = Event(x=11, y=12)
        self.rect._on_click(event)
        self.assertEqual(1, self.event_count)
        self.assertEqual(point0_xy_bck, self.point0_xy, "_on_click should not change point0_xy")
        self.assertEqual(point1_xy_bck, self.point1_xy, "_on_click should not change point1_xy")

        event = Event(x=21, y=22)
        k = 0
        self.rect._on_drag(k, event)
        self.assertEqual(2, self.event_count, "Event must not be triggered")
        self.assertEqual(point0_xy_bck, self.point0_xy, "Event coordinate must pass to callback")
        self.assertEqual(point1_xy_bck, self.point1_xy, "Event coordinate must pass to callback")

        event = Event(x=31, y=32)
        k = 1
        self.rect._on_drag(k, event)
        self.assertEqual(3, self.event_count, "Event must not be triggered")
        self.assertEqual(point0_xy_bck, self.point0_xy, "_on_drag should not change point0_xy (Point.on_drag should)")
        self.assertEqual(point1_xy_bck, self.point1_xy, "_on_drag should not change point0_xy (Point.on_drag should)")

        event = Event(x=41, y=42)
        point0_xy_bck = self.point0_xy
        point1_xy_bck = self.point1_xy
        self.rect._on_release(event)
        self.assertEqual(4, self.event_count, "Event must not be triggered")
        self.assertEqual(point0_xy_bck, self.point0_xy, "_on_release should not change point0_xy")
        self.assertEqual(point1_xy_bck, self.point1_xy, "_on_release should not change point1_xy")

    def test_none_callback(self):
        point0_xy_bck = self.point0_xy
        point1_xy_bck = self.point1_xy

        self.rect = interactive_overlays.Rectangle(
            canvas=self.canvas, point0_xy=self.point0_xy, point1_xy=self.point1_xy, label="ok", on_click=None, on_drag=None, on_release=None
        )

        for k in range(2):
            binds = self.canvas.tag_bind(self.rect.ipoints[k].circle_id)
            self.assertIn(EventName.CLICK, binds, f"{EventName.CLICK} tag not binded")
            self.assertIn(EventName.DRAG, binds, f"{EventName.DRAG} tag not binded")
            self.assertIn(EventName.RELEASE, binds, f"{EventName.RELEASE} tag not binded")
            self.assertIn(EventName.ENTER, binds, f"{EventName.ENTER} tag not binded")
            self.assertIn(EventName.LEAVE, binds, f"{EventName.LEAVE} tag not binded")

        self.assertEqual(0, self.event_count, "Event should not be triggered")
        self.assertEqual(point0_xy_bck, self.point0_xy, "point0_xy should not change at Rectangle creation")
        self.assertEqual(point1_xy_bck, self.point1_xy, "point1_xy should not change at Rectangle creation")

        event = Event(123, 456)
        self.rect._on_click(event)
        self.rect._on_drag(0, event)
        self.rect._on_release(event)

        self.assertEqual(0, self.event_count, "Event should not be triggered")
        self.assertEqual(point0_xy_bck, self.point0_xy, "those callbacks should not be able to change self.point0_xy_bck")
        self.assertEqual(point1_xy_bck, self.point1_xy, "those callbacks should not be able to change self.point0_xy_bck")

    def test_event_sequence(self):
        self.rect = interactive_overlays.Rectangle(
            canvas=self.canvas, point0_xy=self.point0_xy, point1_xy=self.point1_xy, label="ok", on_click=None, on_drag=None, on_release=None
        )
        event = Event(0, 0)

        for k, pt in enumerate(self.rect.ipoints):
            self.assertEqual(interactive_overlays.State.NORMAL, pt.state, f"rectangle.ipoints[{k}] must interact")

            pt._on_enter(event)
            self.assertEqual(interactive_overlays.State.HOVERED, pt.state, f"rectangle.ipoints[{k}] must interact")

            pt._on_click(event)
            self.assertEqual(interactive_overlays.State.DRAGGED, pt.state, f"rectangle.ipoints[{k}] must interact")

            pt._on_drag(event)
            self.assertEqual(interactive_overlays.State.DRAGGED, pt.state, f"rectangle.ipoints[{k}] must interact")

            pt._on_release(event)
            self.assertEqual(interactive_overlays.State.HOVERED, pt.state, f"rectangle.ipoints[{k}] must interact")

            pt._on_leave(event)
            self.assertEqual(interactive_overlays.State.NORMAL, pt.state, f"rectangle.ipoints[{k}] must interact")

    def test_event_raise(self):
        self.rect = interactive_overlays.Rectangle(
            canvas=self.canvas, point0_xy=self.point0_xy, point1_xy=self.point1_xy, label="ok", on_click=None, on_drag=self.on_event_error, on_release=None
        )
        event = Event(0, 0)

        with self.assertRaises(Exception):
            self.rect._on_drag(0, event)