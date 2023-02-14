import unittest
import tk4cv2 as tcv2

class TestTk4Cv2(unittest.TestCase):
    def test_package(self):
        self.assertIsNotNone(tcv2.__version__)
        self.assertIsNotNone(tcv2.__version_info__)

    def test_namedWindow(self):
        self.assertEqual(len(tcv2.Tk4Cv2.instances), 0, msg="At initialisation, number of instances must be 0.")
        res = tcv2.namedWindow("win0")
        self.assertIsNone(res, msg="function tcv2.namedWindow(winname) must return None")
        self.assertEqual(len(tcv2.Tk4Cv2.instances), 1, msg="After first use of tcv2.namedWindow(...), number of instances must be 1.")
        self.assertIsNotNone(tcv2.Tk4Cv2.instances["win0"], msg='After use of tcv2.namedWindow("win0"), tcv2.Tk4Cv2.instances["win0"] must not be None')


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
        tcv2.createButton(text='Button', command=self.callback, winname=self.winname)

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
        tcv2.createCheckbutton(name="CheckButton", windowName=self.winname, value=False, onChange=self.callback)

        widget = find_widget_by_name(self.tk4cv2_instance, "checkbutton")

        self.triggered = False
        self.assertFalse(self.triggered)
        widget.invoke()
        self.assertTrue(self.triggered)


if __name__ == '__main__':
    unittest.main()
