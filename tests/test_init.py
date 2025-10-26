import re
import sys
import unittest
from typing import Tuple

import cv2
import numpy as np
import toml

import guibbon as gbn

eps = sys.float_info.epsilon


class TestPackage(unittest.TestCase):
    def test_version_match(self):
        ver0 = gbn.__version__
        toml_data = toml.load("pyproject.toml")
        version_line = toml_data["project"]["version"]
        ver1 = version_line.split()[-1]
        ver1 = ver1.replace(".dev0", "-dev")  # I don't know where the ".dev0" comes from but it corresponds to my "-dev"
        self.assertEqual(ver0, ver1, "Package version (in pyproject.toml) and __version__ (in __init__.py) must match")

    def test_version_format(self):
        mtch = re.match(r"(\d+).(\d+).(\d+)((-dev)?)$", gbn.__version__)
        self.assertIsNotNone(mtch, 'Version number must match regex: ' + r"(\d+).(\d+).(\d+)((-dev)?)$")

    def test_version_info_format(self):
        version_digits, mode = gbn.__version_info__
        version = ".".join([str(digit) for digit in version_digits])
        if mode is not None:
            version += "-" + mode
        self.assertEqual(version, gbn.__version__)


class TestGuibbon(unittest.TestCase):
    def tearDown(self) -> None:
        gbn.Guibbon.instances = {}
        gbn.Guibbon.active_instance_name = None

    def test_package(self):
        self.assertIsNotNone(gbn.__version__)
        self.assertIsNotNone(gbn.__version_info__)

    def test_inject(self):
        cv2_func = cv2.namedWindow
        gbn_func = gbn.namedWindow
        self.assertNotEqual(cv2_func, gbn_func)
        gbn.inject(cv2)
        self.assertEqual(cv2.namedWindow, gbn_func, msg="gbn.inject must correctly inject function to cv2")

    def test_namedWindow(self):
        self.assertEqual(len(gbn.Guibbon.instances), 0, msg="At initialisation, number of instances must be 0.")
        res = gbn.namedWindow("win0")
        self.assertIsNone(res, msg="function gbn.namedWindow(winname) must return None")
        self.assertEqual(len(gbn.Guibbon.instances), 1, msg="After first use of gbn.namedWindow(...), number of instances must be 1.")
        self.assertIsNotNone(gbn.Guibbon.instances["win0"], msg='After use of gbn.namedWindow("win0"), gbn.Guibbon.instances["win0"] must not be None')

    def test_multiple_instances(self):
        self.assertEqual(len(gbn.Guibbon.instances), 0, msg="At initialisation, number of instances must be 0.")
        gbn.namedWindow("win0")
        gbn.namedWindow("win1")
        self.assertEqual(len(gbn.Guibbon.instances), 2, msg="After 2 uses of gbn.namedWindow(...), number of instances must be 2.")

    def test_imshow_and_getWindowProperty(self):
        img = np.zeros((10, 10), dtype=np.uint8)
        winname = "win0"
        self.assertEqual(len(gbn.Guibbon.instances), 0, msg="At initialisation, number of instances must be 0.")
        res = gbn.getWindowProperty(winname, cv2.WND_PROP_VISIBLE)
        self.assertTrue(abs(res - 0.0) <= eps, msg="Non existant windows must have property WND_PROP_VISIBLE set to 0.0")
        self.assertFalse(gbn.Guibbon.is_instance(winname), msg="gbn.Guibbon.is_instance must return false for non-existant windows")
        self.assertEqual(len(gbn.Guibbon.instances), 0, msg="getWindowProperty should not be able to create new window")

        res = gbn.imshow(winname, img)
        self.assertEqual(len(gbn.Guibbon.instances), 1, msg="gbn.imshow must be able to create new window")
        self.assertTrue(gbn.Guibbon.is_instance(winname), msg="gbn.imshow must be able to create new window with given name")
        self.assertIsNone(res, msg="gbn.imshow must return None")

        res = gbn.getWindowProperty(winname, cv2.WND_PROP_VISIBLE)
        self.assertTrue(abs(res - 1.0) <= eps, msg="Existant and visible windows must have property WND_PROP_VISIBLE set to 1.0")
        gbn.Guibbon.instances = {}  # TODO: use
        res = gbn.getWindowProperty(winname, cv2.WND_PROP_VISIBLE)
        self.assertTrue(abs(res - 0.0) <= eps, msg="Deleting instance of a windows must destroy it. getWindowProperty must return 0")


def find_widget_by_name(guibbon_instance, widgetname):
    last_guibbon_widget = list(guibbon_instance.ctrl_frame.children.values())[-1]

    # Not sure if this is good practice because this line depends on how the widget is implemented.
    # Any minor modification of implementation could make this line raise an exception.
    widgetname_list = [key for key in last_guibbon_widget.children.keys() if widgetname in key]
    assert len(widgetname_list) == 1
    widgetname = widgetname_list[0]
    widget = last_guibbon_widget.children[widgetname]
    return widget


class TestGuibbon_checkbutton(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        gbn.namedWindow(self.winname)
        self.guibbon_instance = gbn.Guibbon.instances["win0"]
        self.triggered = None
        self.args: Tuple[bool, ...]

    def callback(self, *args: bool):
        print("callback checkbutton triggered", args)
        self.triggered = True
        self.args = args

    def test_create_check_button(self):
        widget = gbn.create_check_button(winname=self.winname, name="CheckButton", on_change=self.callback, initial_value=False)
        self.assertIsNotNone(widget, msg="function gbn.create_check_button must not return None")
        self.assertIsInstance(widget, gbn.CheckButtonWidget, msg="function gbn.create_check_button must return instance of CheckButtonWidget")

        self.assertIsNone(self.triggered)

        widget.on_change(True)
        self.assertTrue(self.triggered)
        self.assertTupleEqual(self.args, (True,))

        widget.on_change(False)
        self.assertTrue(self.triggered)
        self.assertTupleEqual(self.args, (False,))


class TestGuibbon_TrackBar(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        gbn.namedWindow(self.winname)
        self.guibbon_instance = gbn.Guibbon.instances["win0"]
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
        res = gbn.createTrackbar(trackbarName=name, windowName=self.winname, value=1, count=10, onChange=self.callback)
        self.assertIsNone(res, msg="function gbn.createTrackBar must return None")

        value = gbn.getTrackbarPos(name, self.winname)
        self.assertEqual(value, 1, msg="function gbn.getTrackbarPos must return correct value")

        self.triggered = False
        gbn.setTrackbarPos(name, self.winname, 8)
        self.assertTrue(self.triggered, "function gbn.setTrackbarPos must trigger callback")
        value = gbn.getTrackbarPos(name, self.winname)
        self.assertEqual(value, 8, msg="function gbn.getTrackbarPos must return correct value")

    def test_TrackBar_min_max(self):
        """
        testing 4 functions:
         - setTrackbarMax
         - setTrackbarMin
         - getTrackbarMax
         - getTrackbarMin
        """
        name = "TrackBar"
        gbn.createTrackbar(trackbarName=name, windowName=self.winname, value=1, count=10, onChange=self.callback)
        initial_min = gbn.getTrackbarMin(trackbarname=name, winname=self.winname)
        initial_max = gbn.getTrackbarMax(trackbarname=name, winname=self.winname)

        self.assertEqual(initial_min, 0)
        self.assertEqual(initial_max, 10)

        gbn.setTrackbarMin(trackbarname=name, winname=self.winname, minval=5)
        gbn.setTrackbarMax(trackbarname=name, winname=self.winname, maxval=20)

        new_min = gbn.getTrackbarMin(trackbarname=name, winname=self.winname)
        new_max = gbn.getTrackbarMax(trackbarname=name, winname=self.winname)

        self.assertEqual(new_min, 5)
        self.assertEqual(new_max, 20)


class TestGuibbon_other(unittest.TestCase):
    def test_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            gbn.not_implemented_error()


if __name__ == "__main__":
    unittest.main()
