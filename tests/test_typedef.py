import unittest
from tk4cv2.typedef import InteractivePoint, InteractivePolygon
from types import FunctionType


class TestPoint(unittest.TestCase):
    def test_interface_pattern(self):
        for interface in [InteractivePoint, InteractivePolygon]:
            with self.assertRaises(AttributeError, msg="Calling non existing functions must raise an AttributeError"):
                _ = interface.this_does_not_exist_and_should_raise  # type: ignore

            # makes sure the interface correctly prevent bad implementation
            class BadClass(interface):  # type: ignore
                pass

            with self.assertRaises(TypeError, msg="BadClass doesn't properly implement the interface. Its instanciation must raise a TypeError"):
                BadClass()

    def test_InteractivePoint_interface(self):
        func_list = [
            InteractivePoint.update,
            InteractivePoint.set_img_point_xy,
            InteractivePoint.set_visible,
        ]
        for func in func_list:
            self.assertIsInstance(func, FunctionType, msg=f"Attribute {func} is supposed to be a function")

    def test_InteractivePolygon_interface(self):
        func_list = [
            InteractivePolygon.update,
            InteractivePolygon.set_point_xy_list,
            InteractivePolygon.set_visible,
        ]
        for func in func_list:
            self.assertIsInstance(func, FunctionType, msg=f"Attribute {func} is supposed to be a function")


if __name__ == "__main__":
    unittest.main()
