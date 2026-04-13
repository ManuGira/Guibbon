import guibbon as gbn
import unittest


class Test_SliderWidget(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        gbn.namedWindow(self.winname)
        self.guibbon_instance = gbn.Guibbon.instances["win0"]
        self.triggered = None

    def callback(self, *args):
        print("callback slider triggered", args)
        self.triggered = True

    def test_Slider(self):
        values = [10, 13, 100]
        name = "Slider"
        slider = gbn.create_slider(winname=self.winname, slider_name=name, values=values + [], on_change=self.callback, initial_index=2)
        self.assertIsInstance(slider, gbn.SliderWidget, msg="function gbn.create_slider must return an instance of a SliderWidget")

        slider = gbn.get_slider_instance(self.winname, name)
        self.assertIsInstance(slider, gbn.SliderWidget, msg="function gbn.get_slider_instance must return an instance of a SliderWidget")

        index = slider.get_position()
        self.assertEqual(index, 2, msg="function get_values of SliderWidget instance must return correct value")

        self.triggered = False
        slider.set_position(0)
        self.assertTrue(self.triggered, "function set_index of SliderWidget instance must trigger callback by default")
        slider.set_position(1, trigger_callback=False)
        self.assertTrue(self.triggered, "function set_index of SliderWidget instance should not trigger callback when trigger_callback=False")
        index = slider.get_position()
        self.assertEqual(index, 1, msg="function get_index of SliderWidget instance must return correct position")
        values_res = slider.get_values()
        for expected, actual in zip(values, values_res):
            self.assertEqual(expected, actual, msg="function get_values of SliderWidget instance must return correct values")

        values = [100, 200, 300, 400]
        slider.set_values(values + [])

        values_res = slider.get_values()
        for expected, actual in zip(values, values_res):
            self.assertEqual(expected, actual, msg="function get_values of SliderWidget instance must return correct values")
