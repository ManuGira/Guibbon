import unittest
import tk4cv2 as tcv2


class TestTk4Cv2(unittest.TestCase):

    def tearDown(self) -> None:
        tcv2.Tk4Cv2.instances = {}
        tcv2.Tk4Cv2.active_instance_name = None

    def test_package(self):
        self.assertIsNotNone(tcv2.__version__)
        self.assertIsNotNone(tcv2.__version_info__)

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


def find_widget_by_name(tk4cv2_instance, widgetname):
    last_tk4cv2_widget = list(tk4cv2_instance.ctrl_frame.children.values())[-1]

    # Not sure if this is good practice because this line depends on how the widget is implemented.
    # Any minor modification of implementation could make this line raise an exception.
    widgetname_list = [key for key in last_tk4cv2_widget.children.keys() if widgetname in key]
    assert len(widgetname_list) == 1
    widgetname = widgetname_list[0]
    widget = last_tk4cv2_widget.children[widgetname]
    return widget


class TestTk4Cv2_button(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        tcv2.namedWindow(self.winname)
        self.tk4cv2_instance = tcv2.Tk4Cv2.instances["win0"]
        self.triggered = None

    def callback(self, *args):
        print("callback_button triggered", args)
        self.triggered = True

    def test_createButton(self):
        res = tcv2.createButton(text='Button', command=self.callback, winname=self.winname)
        self.assertIsNone(res, msg="function tcv2.createButton must return None")

        widget = find_widget_by_name(self.tk4cv2_instance, "button")

        self.triggered = False
        self.assertFalse(self.triggered)
        widget.invoke()
        self.assertTrue(self.triggered)

class TestTk4Cv2_checkbutton(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        tcv2.namedWindow(self.winname)
        self.tk4cv2_instance = tcv2.Tk4Cv2.instances["win0"]
        self.triggered = None

    def callback(self, *args):
        print("callback checkbutton triggered", args)
        self.triggered = True

    def test_createCheckButton(self):
        res = tcv2.createCheckbutton(name="CheckButton", windowName=self.winname, value=False, onChange=self.callback)
        self.assertIsNone(res, msg="function tcv2.createCheckbutton must return None")

        widget = find_widget_by_name(self.tk4cv2_instance, "checkbutton")

        self.triggered = False
        self.assertFalse(self.triggered)
        widget.invoke()
        self.assertTrue(self.triggered)


class TestTk4Cv2_RadioButtons(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        tcv2.namedWindow(self.winname)
        self.tk4cv2_instance = tcv2.Tk4Cv2.instances["win0"]
        self.triggered = None

    def callback(self, *args):
        print("callback radiobuttons triggered", args)
        self.triggered = True

    def test_RadioButtons(self):
        """
        testing 3 functions:
         - createRadioButtons
         - getRadioButtons
         - setRadioButtons
        """
        name = "RadioButtons"
        res = tcv2.createRadioButtons(
            name=name, options=["A", "B", "C"], winname=self.winname, value=1, onChange=self.callback)
        self.assertIsNone(res, msg="function tcv2.createRadioButtons must return None")

        i, opt = tcv2.getRadioButtons(name, self.winname)
        self.assertEqual(i , 1, msg="function tcv2.getRadioButtons must return correct index")
        self.assertEqual(opt, "B", msg="function tcv2.getRadioButtons must return correct option")

        self.triggered = False
        tcv2.setRadioButtons(name, self.winname, 2)
        self.assertTrue(self.triggered, "function tcv2.setRadioButtons must trigger callback")
        i, opt = tcv2.getRadioButtons(name, self.winname)
        self.assertEqual(i, 2, msg="function tcv2.getRadioButtons must return correct index")
        self.assertEqual(opt, "C", msg="function tcv2.getRadioButtons must return correct option")


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
        self.assertEqual(value , 1, msg="function tcv2.getTrackbarPos must return correct value")

        self.triggered = False
        tcv2.setTrackbarPos(name, self.winname, 8)
        self.assertTrue(self.triggered, "function tcv2.setTrackbarPos must trigger callback")
        value = tcv2.getTrackbarPos(name, self.winname)
        self.assertEqual(value, 8, msg="function tcv2.getTrackbarPos must return correct value")


class TestTk4Cv2_other(unittest.TestCase):
    def test_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            tcv2.not_implemented_error()


if __name__ == '__main__':
    unittest.main()
