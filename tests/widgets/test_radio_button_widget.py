import sys
import unittest

import tk4cv2 as tcv2


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
        rb_abc = tcv2.create_radio_buttons(winname=self.winname, name=name, options=["A", "B", "C"], on_change=self.callback)
        self.assertIsNotNone(rb_abc, msg="function tcv2.create_radio_buttons() must return None")
        self.assertIsInstance(rb_abc, tcv2.RadioButtonWidget)

        i, opt = rb_abc.get_current_selection()
        self.assertEqual(i, 0, msg="function get_current_selection() must return correct index")
        self.assertEqual(opt, "A", msg="function get_current_selection() must return correct option")

        self.triggered = False
        rb_abc.select(1)
        self.assertFalse(self.triggered, "function select(int) must NOT trigger callback by default")
        i, opt = rb_abc.get_current_selection()
        self.assertEqual(i, 1, msg="function get_current_selection() must return correct index")
        self.assertEqual(opt, "B", msg="function get_current_selection() must return correct option")

        rb_abc.select(2, trigger_callback=True)
        self.assertTrue(self.triggered, "function select(int, trigger_callback=True) must trigger callback")
        i, opt = rb_abc.get_current_selection()
        self.assertEqual(i, 2, msg="function get_current_selection() must return correct index")
        self.assertEqual(opt, "C", msg="function get_current_selection() must return correct option")
