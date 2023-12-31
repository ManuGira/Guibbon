import tk4cv2 as tcv2
import unittest


class Test_ButtonWidget(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        tcv2.namedWindow(self.winname)
        self.tk4cv2_instance = tcv2.Tk4Cv2.instances["win0"]
        self.triggered = None

    def callback(self, *args):
        print("callback_button triggered", args)
        self.triggered = True

    def test_create_button(self):
        button = tcv2.create_button(winname=self.winname, text="Button", command=self.callback)
        self.assertIsInstance(button, tcv2.ButtonWidget, msg="function tcv2.create_button must return an instance of ButtonWidget")

        # widget = find_widget_by_name(self.tk4cv2_instance, "button")

        self.triggered = False
        self.assertFalse(self.triggered)
        button.button.invoke()
        self.assertTrue(self.triggered)