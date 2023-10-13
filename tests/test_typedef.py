import unittest
import numpy as np

from tk4cv2 import typedef

class TestTypeDef(unittest.TestCase):
    def test_is_point2d(self):
        self.assertTrue(typedef.is_point2d((0, 0)))
        self.assertTrue(typedef.is_point2d((1000, 100)))
        self.assertTrue(typedef.is_point2d((1000, 100.0)))
        self.assertTrue(typedef.is_point2d((1000.0, 100.0)))
        self.assertTrue(typedef.is_point2d((1000.0, 100)))

        self.assertFalse(typedef.is_point2d(tuple()))
        self.assertFalse(typedef.is_point2d((0,)))
        self.assertFalse(typedef.is_point2d((0, 0, 0)))
        self.assertFalse(typedef.is_point2d(("0", 0)))
        self.assertFalse(typedef.is_point2d([0, 0]))
        self.assertFalse(typedef.is_point2d(np.array([0, 0])))
        self.assertFalse(typedef.is_point2d(0))


if __name__ == '__main__':
    unittest.main()
