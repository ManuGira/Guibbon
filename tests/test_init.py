import sys
import unittest
import cv2
import tk4cv2 as tcv2
import numpy as np
from typing import Tuple

eps = sys.float_info.epsilon


class TestTk4Cv2(unittest.TestCase):
    def tearDown(self) -> None:
        tcv2.Tk4Cv2.instances = {}
        tcv2.Tk4Cv2.active_instance_name = None

    def test_package(self):
        self.assertIsNotNone(tcv2.__version__)
        self.assertIsNotNone(tcv2.__version_info__)

    def test_inject(self):
        cv2_func = cv2.namedWindow
        tcv2_func = tcv2.namedWindow
        self.assertNotEqual(cv2_func, tcv2_func)
        tcv2.inject(cv2)
        self.assertEqual(cv2.namedWindow, tcv2_func, msg="tcv2.inject must correctly inject function to cv2")

    def test_namedWindow(self):
        self.assertEqual(len(tcv2.Tk4Cv2.instances), 0, msg="At initialisation, number of instances must be 0.")
        res = tcv2.namedWindow("win0")
        self.assertIsNone(res, msg="function tcv2.namedWindow(winname) must return None")
        self.assertEqual(len(tcv2.Tk4Cv2.instances), 1, msg="After first use of tcv2.namedWindow(...), number of instances must be 1.")
        self.assertIsNotNone(tcv2.Tk4Cv2.instances["win0"], msg='After use of tcv2.namedWindow("win0"), tcv2.Tk4Cv2.instances["win0"] must not be None')

    def test_multiple_instances(self):
        self.assertEqual(len(tcv2.Tk4Cv2.instances), 0, msg="At initialisation, number of instances must be 0.")
        tcv2.namedWindow("win0")
        tcv2.namedWindow("win1")
        self.assertEqual(len(tcv2.Tk4Cv2.instances), 2, msg="After 2 uses of tcv2.namedWindow(...), number of instances must be 2.")

    def test_imshow_and_getWindowProperty(self):
        img = np.zeros((10, 10), dtype=np.uint8)
        winname = "win0"
        self.assertEqual(len(tcv2.Tk4Cv2.instances), 0, msg="At initialisation, number of instances must be 0.")
        res = tcv2.getWindowProperty(winname, cv2.WND_PROP_VISIBLE)
        self.assertTrue(abs(res - 0.0) <= eps, msg="Non existant windows must have property WND_PROP_VISIBLE set to 0.0")
        self.assertFalse(tcv2.Tk4Cv2.is_instance(winname), msg="tcv2.Tk4Cv2.is_instance must return false for non-existant windows")
        self.assertEqual(len(tcv2.Tk4Cv2.instances), 0, msg="getWindowProperty should not be able to create new window")

        res = tcv2.imshow(winname, img)
        self.assertEqual(len(tcv2.Tk4Cv2.instances), 1, msg="tcv2.imshow must be able to create new window")
        self.assertTrue(tcv2.Tk4Cv2.is_instance(winname), msg="tcv2.imshow must be able to create new window with given name")
        self.assertIsNone(res, msg="tcv2.imshow must return None")

        res = tcv2.getWindowProperty(winname, cv2.WND_PROP_VISIBLE)
        self.assertTrue(abs(res - 1.0) <= eps, msg="Existant and visible windows must have property WND_PROP_VISIBLE set to 1.0")
        tcv2.Tk4Cv2.instances = {}  # TODO: use
        res = tcv2.getWindowProperty(winname, cv2.WND_PROP_VISIBLE)
        self.assertTrue(abs(res - 0.0) <= eps, msg="Deleting instance of a windows must destroy it. getWindowProperty must return 0")


def find_widget_by_name(tk4cv2_instance, widgetname):
    last_tk4cv2_widget = list(tk4cv2_instance.ctrl_frame.children.values())[-1]

    # Not sure if this is good practice because this line depends on how the widget is implemented.
    # Any minor modification of implementation could make this line raise an exception.
    widgetname_list = [key for key in last_tk4cv2_widget.children.keys() if widgetname in key]
    assert len(widgetname_list) == 1
    widgetname = widgetname_list[0]
    widget = last_tk4cv2_widget.children[widgetname]
    return widget


class TestTk4Cv2_checkbutton(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        tcv2.namedWindow(self.winname)
        self.tk4cv2_instance = tcv2.Tk4Cv2.instances["win0"]
        self.triggered = None
        self.args: Tuple[bool, ...]

    def callback(self, *args: bool):
        print("callback checkbutton triggered", args)
        self.triggered = True
        self.args = args

    def test_create_check_button(self):
        widget = tcv2.create_check_button(winname=self.winname, name="CheckButton", on_change=self.callback, initial_value=False)
        self.assertIsNotNone(widget, msg="function tcv2.create_check_button must not return None")
        self.assertIsInstance(widget, tcv2.CheckButtonWidget, msg="function tcv2.create_check_button must return instance of CheckButtonWidget")

        self.assertIsNone(self.triggered)

        widget.on_change(True)
        self.assertTrue(self.triggered)
        self.assertTupleEqual(self.args, (True,))

        widget.on_change(False)
        self.assertTrue(self.triggered)
        self.assertTupleEqual(self.args, (False,))


class TestTk4Cv2_TrackBar(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        tcv2.namedWindow(self.winname)
        self.tk4cv2_instance = tcv2.Tk4Cv2.instances["win0"]
        self.triggered = None

    def callback(self, *args):
        print("callback trackBar triggered", args)
        self.triggered = True

    def test_TrackBar(self):
        """
        testing 3 functions:
         - createTrackBar
         - getTrackBarPos
         - setTrackBarPos
        """
        name = "TrackBar"
        res = tcv2.createTrackbar(trackbarName=name, windowName=self.winname, value=1, count=10, onChange=self.callback)
        self.assertIsNone(res, msg="function tcv2.createTrackBar must return None")

        value = tcv2.getTrackbarPos(name, self.winname)
        self.assertEqual(value, 1, msg="function tcv2.getTrackbarPos must return correct value")

        self.triggered = False
        tcv2.setTrackbarPos(name, self.winname, 8)
        self.assertTrue(self.triggered, "function tcv2.setTrackbarPos must trigger callback")
        value = tcv2.getTrackbarPos(name, self.winname)
        self.assertEqual(value, 8, msg="function tcv2.getTrackbarPos must return correct value")

    def test_TrackBar_min_max(self):
        """
        testing 4 functions:
         - setTrackbarMax
         - setTrackbarMin
         - getTrackbarMax
         - getTrackbarMin
        """
        name = "TrackBar"
        tcv2.createTrackbar(trackbarName=name, windowName=self.winname, value=1, count=10, onChange=self.callback)
        initial_min = tcv2.getTrackbarMin(trackbarname=name, winname=self.winname)
        initial_max = tcv2.getTrackbarMax(trackbarname=name, winname=self.winname)

        self.assertEqual(initial_min, 0)
        self.assertEqual(initial_max, 10)

        tcv2.setTrackbarMin(trackbarname=name, winname=self.winname, minval=5)
        tcv2.setTrackbarMax(trackbarname=name, winname=self.winname, maxval=20)

        new_min = tcv2.getTrackbarMin(trackbarname=name, winname=self.winname)
        new_max = tcv2.getTrackbarMax(trackbarname=name, winname=self.winname)

        self.assertEqual(new_min, 5)
        self.assertEqual(new_max, 20)


class TestTk4Cv2_other(unittest.TestCase):
    def test_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            tcv2.not_implemented_error()


if __name__ == "__main__":
    unittest.main()
