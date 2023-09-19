import dataclasses
import sys
import tkinter
import unittest
from tk4cv2 import interactive_overlays
from tk4cv2 import transform_matrix as tmat

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

class TestMagnets(unittest.TestCase):
    def foo(self, x_img, y_img):
        return self.val, self.val

    def setUp(self) -> None:
        self.canvas = tkinter.Canvas()
        self.val = 0
        self.points_img = [(10.1*k, 10.1*k) for k in range(4)]
        self.img2can_matrix = tmat.T((123, 456)) @ tmat.S((100, 200))

    def test_magnets_creation(self):
        magnets = interactive_overlays.Magnets(self.canvas, self.points_img)
        self.assertListEqual(tmat.I().tolist(), magnets.img2can_matrix.tolist(), "Default img2can_matrix must be indentity")
        magnets.set_img2can_matrix(self.img2can_matrix)
        self.assertListEqual(self.img2can_matrix.tolist(), magnets.img2can_matrix.tolist(), "img2can_matrix must be settable")
        self.assertNotEqual(id(self.img2can_matrix), id(magnets.img2can_matrix), "set_img2can_matrix must deeply copy the matrix")

        # giving empty Point2DList should not raise any exception
        interactive_overlays.Magnets(self.canvas, [])

        # default threshold is bigger than 0
        self.assertTrue(magnets.dist_threshold > 0)


    def test_snap_to_nearest_magnet(self):
        empty_magnet = interactive_overlays.Magnets(self.canvas, [])
        for point_xy in [(0, 0), (10, 20), (300, 400), (-10.2, -12.2)]:
            self.assertTupleEqual(point_xy, empty_magnet.snap_to_nearest_magnet(point_xy), "empty magnet should not snap")

        magnets = interactive_overlays.Magnets(self.canvas, self.points_img)
        x, y = self.points_img[-1]
        for thresh in [10, 50]:
            magnets.dist_threshold = thresh
            self.assertTupleEqual((x, y), magnets.snap_to_nearest_magnet((x, y)))
            self.assertTupleEqual((x, y), magnets.snap_to_nearest_magnet((x+thresh-1, y)))
            self.assertTupleEqual((x+thresh+1, y), magnets.snap_to_nearest_magnet((x+thresh+1, y)))

        magnets.dist_threshold = 50
        self.assertTupleEqual((10.1, 10.1), magnets.snap_to_nearest_magnet((14, 14)))
        self.assertTupleEqual((20.2, 20.2), magnets.snap_to_nearest_magnet((16, 16)))

    def test_update(self):
        magnets = interactive_overlays.Magnets(self.canvas, self.points_img)
        magnets.set_img2can_matrix(self.img2can_matrix)

        self.assertEqual(len(self.points_img), len(magnets.circle_id_list), "Each points must have its circle on the canvas")

        magnets.update()
        for point_img_xy, circle_id in zip(self.points_img, magnets.circle_id_list):
            x_can_expected, y_can_expected = tmat.apply(self.img2can_matrix, point_img_xy)
            x1, y1, x2, y2 = self.canvas.coords(circle_id)
            x = round((x1 + x2)/2)
            y = round((y1 + y2)/2)
            self.assertLess(abs(x-x_can_expected), 0.1, "Coordinates of magnet points must be accurately placed on the canvas")
            self.assertLess(abs(y-y_can_expected), 0.1, "Coordinates of magnet points must be accurately placed on the canvas")


class TestPoint(unittest.TestCase):
    def setUp(self) -> None:
        self.event_count = 0
        self.drag_count = 0
        self.release_count = 0
        self.point_xy = (0, 0)

        self.canvas = tkinter.Canvas()
        self.magnets = interactive_overlays.Magnets(self.canvas, [(1000.0, 1000.0)], (lambda x, y: (2 * x, 2 * y)))

    def tearDown(self) -> None:
        pass

    def on_event(self, event):
        self.event_count += 1
        self.point_xy = (event.x, event.y)

    def on_event_error(self, event):
        raise

    def test_callback(self):
        self.pt = interactive_overlays.Point(
            canvas=self.canvas,
            point_xy=self.point_xy,
            label="ok",
            on_click=self.on_event,
            on_drag=self.on_event,
            on_release=self.on_event)

        binds = self.canvas.tag_bind(self.pt.circle_id)
        self.assertIn(EventName.CLICK, binds, f"{EventName.CLICK} tag not binded")
        self.assertIn(EventName.DRAG, binds, f"{EventName.DRAG} tag not binded")
        self.assertIn(EventName.RELEASE, binds, f"{EventName.RELEASE} tag not binded")
        self.assertIn(EventName.ENTER, binds, f"{EventName.ENTER} tag not binded")
        self.assertIn(EventName.LEAVE, binds, f"{EventName.LEAVE} tag not binded")

        self.assertEqual(0, self.event_count)
        self.assertEqual((0, 0), self.point_xy)

        pt_point_bck = self.pt.point_xy
        event = Event(x=11, y=12)
        self.pt._on_click(event)
        self.assertEqual(1, self.event_count, "Event must be triggered")
        self.assertEqual((11, 12), self.point_xy, "Event coordinate must be passed to callback")
        self.assertEqual(pt_point_bck, self.pt.point_xy, "point._on_click() must not set point_xy coordinates")

        event = Event(x=21, y=22)
        self.pt._on_drag(event)
        self.assertEqual(2, self.event_count, "Event must be triggered")
        self.assertEqual((21, 22), self.point_xy, "Event coordinate must be passed to callback")
        self.assertEqual((21, 22), self.pt.point_xy, "point._on_drag() must correctly set point_xy coordinates")

        pt_point_bck = self.pt.point_xy
        event = Event(x=31, y=32)
        self.pt._on_release(event)
        self.assertEqual(3, self.event_count, "Event must be triggered")
        self.assertEqual((31, 32), self.point_xy, "Event coordinate must be passed to callback")
        self.assertEqual(pt_point_bck, self.pt.point_xy, "point._on_release() must correctly set point_xy coordinates")


    def test_none_callback(self):
        self.pt = interactive_overlays.Point(canvas=self.canvas, point_xy=self.point_xy, label="ok",
                on_click=None,
                on_drag=None,
                on_release=None)

        binds = self.canvas.tag_bind(self.pt.circle_id)
        self.assertIn(EventName.CLICK, binds, f"{EventName.CLICK} tag not binded")
        self.assertIn(EventName.DRAG, binds, f"{EventName.DRAG} tag not binded")
        self.assertIn(EventName.RELEASE, binds, f"{EventName.RELEASE} tag not binded")
        self.assertIn(EventName.ENTER, binds, f"{EventName.ENTER} tag not binded")
        self.assertIn(EventName.LEAVE, binds, f"{EventName.LEAVE} tag not binded")

        self.assertEqual(0, self.event_count)
        self.assertEqual((0, 0), self.point_xy)

        event = Event(123, 456)
        self.pt._on_click(event)
        self.pt._on_drag(event)
        self.pt._on_release(event)

        self.assertEqual(0, self.event_count, "Event must not be triggered")
        self.assertEqual((0, 0), self.point_xy, "Event must not be triggered")
        self.assertEqual((123, 456), self.pt.point_xy, "point.point_xy must change even if no user callback is set")

    def test_event_sequence(self):
        self.pt = interactive_overlays.Point(canvas=self.canvas, point_xy=self.point_xy, label="ok",
            on_click=None,
            on_drag=None,
            on_release=None)
        event = Event(0, 0)

        self.assertEqual(self.pt.state, interactive_overlays.State.NORMAL)

        self.pt._on_enter(event)
        self.assertEqual(self.pt.state, interactive_overlays.State.HOVERED)

        self.pt._on_click(event)
        self.assertEqual(self.pt.state, interactive_overlays.State.DRAGGED)

        self.pt._on_drag(event)
        self.assertEqual(self.pt.state, interactive_overlays.State.DRAGGED)

        self.pt._on_release(event)
        self.assertEqual(self.pt.state, interactive_overlays.State.HOVERED)

        self.pt._on_leave(event)
        self.assertEqual(self.pt.state, interactive_overlays.State.NORMAL)

    def test_event_raise(self):
        self.pt = interactive_overlays.Point(canvas=self.canvas, point_xy=self.point_xy, label="ok",
            on_click=None,
            on_drag=self.on_event_error,
            on_release=None)
        event = Event(0, 0)

        with self.assertRaises(Exception):
            self.pt._on_drag(event)


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

    def test_callback(self):
        point_xy_list_bck = self.point_xy_list + []

        self.plg = interactive_overlays.Polygon(
            canvas=self.canvas,
            point_xy_list=self.point_xy_list,
            label="ok",
            on_click=self.on_event,
            on_drag=self.on_event,
            on_release=self.on_event)

        self.assertEqual(len(self.plg.ipoints), len(self.point_xy_list), "Polygon must have 1 Interactive Point instance for each point in point_xy_list")

        for k in range(len(self.plg.ipoints)):
            binds = self.canvas.tag_bind(self.plg.ipoints[k].circle_id)
            self.assertIn(EventName.CLICK, binds, f"{EventName.CLICK} tag not binded")
            self.assertIn(EventName.DRAG, binds, f"{EventName.DRAG} tag not binded")
            self.assertIn(EventName.RELEASE, binds, f"{EventName.RELEASE} tag not binded")
            self.assertIn(EventName.ENTER, binds, f"{EventName.ENTER} tag not binded")
            self.assertIn(EventName.LEAVE, binds, f"{EventName.LEAVE} tag not binded")

        self.assertEqual(0, self.event_count)
        self.assertEqual(point_xy_list_bck, self.point_xy_list,
                         "point_xy_list should not change at Polygon creation")

        point_xy_list_bck = self.point_xy_list + []
        event = Event(x=11, y=12)
        self.plg._on_click(event)
        self.assertEqual(1, self.event_count)
        self.assertEqual(point_xy_list_bck, self.point_xy_list, "_on_click should not change point_xy_list")

        event = Event(x=21, y=22)
        k = 0
        self.plg._on_drag(k, event)
        self.assertEqual(2, self.event_count, "Event must not be triggered")
        self.assertEqual([(21, 22), (0, 100), (100, 100)], self.point_xy_list, "Event coordinate must pass to callback")

        event = Event(x=31, y=32)
        k = 1
        self.plg._on_drag(k, event)
        self.assertEqual(3, self.event_count, "Event must not be triggered")
        self.assertEqual([(21, 22), (31, 32), (100, 100)], self.point_xy_list, "Event coordinate must pass to callback")

        event = Event(x=41, y=42)
        point_xy_list_bck = self.point_xy_list + []
        self.plg._on_release(event)
        self.assertEqual(4, self.event_count, "Event must not be triggered")
        self.assertEqual(point_xy_list_bck, self.point_xy_list, "_on_release should not change point_xy_list")


    def test_none_callback(self):
        point_xy_list_bck = self.point_xy_list + []

        self.plg = interactive_overlays.Polygon(canvas=self.canvas, point_xy_list=self.point_xy_list, label="ok",
                on_click=None,
                on_drag=None,
                on_release=None)

        for k in range(len(self.plg.ipoints)):
            binds = self.canvas.tag_bind(self.plg.ipoints[k].circle_id)
            self.assertIn(EventName.CLICK, binds, f"{EventName.CLICK} tag not binded")
            self.assertIn(EventName.DRAG, binds, f"{EventName.DRAG} tag not binded")
            self.assertIn(EventName.RELEASE, binds, f"{EventName.RELEASE} tag not binded")
            self.assertIn(EventName.ENTER, binds, f"{EventName.ENTER} tag not binded")
            self.assertIn(EventName.LEAVE, binds, f"{EventName.LEAVE} tag not binded")

        self.assertEqual(0, self.event_count, "Event should not be triggered")
        self.assertEqual(point_xy_list_bck,self.point_xy_list,
                         "point_xy_list should not change at Polygon creation")

        event = Event(123, 456)
        self.plg._on_click(event)
        self.plg._on_drag(0, event)
        self.plg._on_release(event)

        self.assertEqual(0, self.event_count, "Event should not be triggered")
        self.assertEqual(point_xy_list_bck, self.point_xy_list, "those callbacks should not be able to change self.point_xy_list")
        self.assertEqual([(123, 456), (0, 100), (100, 100)], self.plg.point_xy_list,
                         "even with no user callback subscribed, the polygon should still respond to mouse drag...")

    def test_event_sequence(self):
        self.plg = interactive_overlays.Polygon(canvas=self.canvas, point_xy_list=self.point_xy_list, label="ok",
            on_click=None,
            on_drag=None,
            on_release=None)
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
        self.plg = interactive_overlays.Polygon(canvas=self.canvas, point_xy_list=self.point_xy_list, label="ok",
            on_click=None,
            on_drag=self.on_event_error,
            on_release=None)
        event = Event(0, 0)

        with self.assertRaises(Exception):
            self.plg._on_drag(0, event)


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
            on_release=self.on_event)

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
        self.assertEqual((21, 22), self.point0_xy, "Event coordinate must pass to callback")
        self.assertEqual((100, 100), self.point1_xy, "Event coordinate must pass to callback")

        event = Event(x=31, y=32)
        k = 1
        self.rect._on_drag(k, event)
        self.assertEqual(3, self.event_count, "Event must not be triggered")
        self.assertEqual((21, 22), self.point0_xy, "Event coordinate must pass to callback")
        self.assertEqual((31, 32), self.point1_xy, "Event coordinate must pass to callback")

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
                canvas=self.canvas,
                point0_xy=self.point0_xy,
                point1_xy=self.point1_xy,
                label="ok",
                on_click=None,
                on_drag=None,
                on_release=None)

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
        self.assertEqual([(123, 456), (100, 100)], self.rect.point_xy_list,
                "even with no user callback subscribed, the rectangle should still respond to mouse drag...")


    def test_event_sequence(self):
        self.rect = interactive_overlays.Rectangle(canvas=self.canvas, point0_xy=self.point0_xy, point1_xy=self.point1_xy, label="ok",
                on_click=None,
                on_drag=None,
                on_release=None)
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
        self.rect = interactive_overlays.Rectangle(canvas=self.canvas, point0_xy=self.point0_xy, point1_xy=self.point1_xy, label="ok",
                on_click=None,
                on_drag=self.on_event_error,
                on_release=None)
        event = Event(0, 0)

        with self.assertRaises(Exception):
            self.rect._on_drag(0, event)


if __name__ == '__main__':
    unittest.main()
