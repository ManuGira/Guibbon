import unittest
import guibbon as gbn


class TestGuibbon_RadioButtons(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        gbn.namedWindow(self.winname)
        self.guibbon_instance = gbn.Guibbon.instances["win0"]
        self.triggered = None

    def callback(self, *args):
        print("callback radiobuttons triggered", args)
        self.triggered = True

    def test_RadioButtons(self):
        name = "RadioButtons"
        rb_abc = gbn.create_radio_buttons(winname=self.winname, name=name, options=["A", "B", "C"], on_change=self.callback)
        self.assertIsNotNone(rb_abc, msg="function gbn.create_radio_buttons() must return None")
        self.assertIsInstance(rb_abc, gbn.RadioButtonsWidget)

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

    def test_RadioButtons_option_getter_setter(self):
        name = "RadioButtons"
        expected = ["A", "B", "C"]
        rbs = gbn.create_radio_buttons(winname=self.winname, name=name, options=expected + [], on_change=self.callback)
        result = rbs.get_options_list()
        self.assertListEqual(expected, result, "function get_options_list() must return correct result")

        expected = ["D", "E", "F"]
        rbs.set_options_list(expected + [])
        result = rbs.get_options_list()
        self.assertListEqual(expected, result, "function get_options_list() must return correct result")

        expected = ["D", "E", "F", "G"]
        rbs.set_options_list(expected + [])
        result = rbs.get_options_list()
        self.assertListEqual(expected, result, "function get_options_list() must return correct result")