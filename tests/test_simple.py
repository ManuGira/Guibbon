# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest
import sys, os

# from sample.simple import add_one
sys.path.insert(0, os.path.abspath("../src/"))
import tk4cv2.tk4cv2 as tcv2


class TestTk4Cv2(unittest.TestCase):
    def test_namedWindow(self):
        self.assertEqual(len(tcv2.Tk4Cv2.instances), 0, msg="At initialisation, number of instances must be 0.")
        res = tcv2.namedWindow("win0")
        self.assertIsNone(res, msg="function tcv2.namedWindow(winname) must return None")
        self.assertEqual(len(tcv2.Tk4Cv2.instances), 1, msg="After first use of tcv2.namedWindow(...), number of instances must be 1.")
        self.assertIsNotNone(tcv2.Tk4Cv2.instances["win0"], msg='After use of tcv2.namedWindow("win0"), tcv2.Tk4Cv2.instances["win0"] must not be None')



if __name__ == '__main__':
    unittest.main()
