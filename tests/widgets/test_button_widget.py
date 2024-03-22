import guibbon as gbn
import unittest


class Test_ButtonWidget(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        gbn.namedWindow(self.winname)
        self.guibbon_instance = gbn.Guibbon.instances["win0"]
        self.triggered = None

    def callback(self, *args):
        print("callback_button triggered", args)
        self.triggered = True

    def test_create_button(self):
        button = gbn.create_button(winname=self.winname, text="Button", on_click=self.callback)
        self.assertIsInstance(button, gbn.ButtonWidget, msg="function gbn.create_button must return an instance of ButtonWidget")

        # widget = find_widget_by_name(self.guibbon_instance, "button")

        self.triggered = False
        self.assertFalse(self.triggered)
        button.button.invoke()
        self.assertTrue(self.triggered)