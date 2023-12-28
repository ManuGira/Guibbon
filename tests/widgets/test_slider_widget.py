import tk4cv2 as tcv2
import unittest


class Test_SliderWidget(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        tcv2.namedWindow(self.winname)
        self.tk4cv2_instance = tcv2.Tk4Cv2.instances["win0"]
        self.triggered = None

    def callback(self, *args):
        print("callback slider triggered", args)
        self.triggered = True

    def test_Slider(self):
        values = [10, 13, 100]
        name = "Slider"
        slider = tcv2.create_slider(winname=self.winname, slider_name=name, values=values + [], initial_index=2, on_change=self.callback)
        self.assertIsInstance(slider, tcv2.SliderWidget, msg="function tcv2.create_slider must return an instance of a SliderWidget")

        slider = tcv2.get_slider_instance(self.winname, name)
        self.assertIsInstance(slider, tcv2.SliderWidget, msg="function tcv2.get_slider_instance must return an instance of a SliderWidget")

        index = slider.get_index()
        self.assertEqual(index, 2, msg="function get_values of SliderWidget instance must return correct value")

        self.triggered = False
        slider.set_index(0)
        self.assertTrue(self.triggered, "function set_index of SliderWidget instance must trigger callback by default")
        slider.set_index(1, trigger_callback=False)
        self.assertTrue(self.triggered, "function set_index of SliderWidget instance should not trigger callback when trigger_callback=False")
        index = slider.get_index()
        self.assertEqual(index, 1, msg="function get_index of SliderWidget instance must return correct index")
        values_res = slider.get_values()
        for expected, actual in zip(values, values_res):
            self.assertEqual(expected, actual, msg="function get_values of SliderWidget instance must return correct values")

        values = [100, 200, 300, 400]
        slider.set_values(values + [])

        values_res = slider.get_values()
        for expected, actual in zip(values, values_res):
            self.assertEqual(expected, actual, msg="function get_values of SliderWidget instance must return correct values")
