import unittest

import numpy as np

from tk4cv2 import transform_matrix as tmat

def maxdiff(arr1, arr2):
    return np.max(np.abs(np.array(arr1)-np.array(arr2)).flatten())

eps = 1e-15

class TestTransformMatrix(unittest.TestCase):
    def test_identity_matrix(self):
        expected = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]])

        mat1 = tmat.identity_matrix()
        mat2 = tmat.I()

        for mat in [mat1, mat2]:
            self.assertTrue(mat.dtype == float)
            self.assertTupleEqual(mat.shape, (3, 3))
            self.assertLess(maxdiff(mat, expected), eps)

    def test_translation_matrix(self):
        trans_list = [(0, 0), (1.1, 2.2), (-3, 19.2)]
        for (tx, ty) in trans_list:
            expected = np.array([
                [1, 0, tx],
                [0, 1, ty],
                [0, 0, 1]])

            mat1 = tmat.translation_matrix((tx, ty))
            mat2 = tmat.T((tx, ty))

            for mat in [mat1, mat2]:
                self.assertTrue(mat.dtype == float)
                self.assertTupleEqual(mat.shape, (3, 3))
                self.assertLess(maxdiff(mat, expected), eps)

        self.assertLess(maxdiff(tmat.T((0, 0)), tmat.I()), eps)

    def test_scale_matrix(self):
        scale_list = [(0, 0), (1, 1), (-1, -1), (1.0, 2.3)]
        for (sx, sy) in scale_list:
            expected = np.array([
                [sx, 0, 0],
                [0, sy, 0],
                [0, 0, 1]])

            mat1 = tmat.scale_matrix((sx, sy))
            mat2 = tmat.S((sx, sy))

            for mat in [mat1, mat2]:
                self.assertTrue(mat.dtype == float)
                self.assertTupleEqual(mat.shape, (3, 3))
                self.assertLess(maxdiff(mat, expected), eps)

        self.assertLess(maxdiff(tmat.S((1, 1)), tmat.I()), eps)


    def test_rotation_matrix(self):
        thetas_list = [0, -1, 1, 1.2]
        for theta in thetas_list:
            cs, sn = np.cos(theta), np.sin(theta)
            expected = np.array([
                [cs,-sn, 0],
                [sn, cs, 0],
                [0, 0, 1]])

            mat1 = tmat.rotation_matrix(theta)
            mat2 = tmat.R(theta)

            for mat in [mat1, mat2]:
                self.assertTrue(mat.dtype == float)
                self.assertTupleEqual(mat.shape, (3, 3))
                self.assertLess(maxdiff(mat, expected), eps)

        self.assertLess(maxdiff(tmat.R(0), tmat.I()), eps)
        self.assertLess(maxdiff(tmat.R(np.pi*2), tmat.I()), eps)


    def test_apply(self):

        def assertIsPoint2D(point_xy):
            self.assertTrue(isinstance(point_xy, tuple), f'Point2D must be a tuple, got {type(point_xy)} instead')
            self.assertEqual(len(point_xy), 2, "Point2D must be of size 2")
            for val in point_xy:
                self.assertTrue(isinstance(val, int) or isinstance(val, float), "Point2D must contains numeric values (either int or float)")

        for point_xy in [(0, 0), (0.0, 0.0)]:
            point_res = tmat.apply(tmat.I(), point_xy)
            assertIsPoint2D(point_res)


        point_xy_list = [(0, 0), (1, 1), (-1, -1), (1.0, 2.3)]
        tx, ty = 10, -20.5
        sx, sy = 2, -2.3
        mat = tmat.T((tx, ty)) @ tmat.S((sx, sy))
        for x, y in point_xy_list:
            x_expected = x*sx + tx
            y_expected = y*sy + ty
            point_expected = x_expected, y_expected
            point_res = tmat.apply(mat, (x, y))
            assertIsPoint2D(point_res)
            self.assertLess(maxdiff(point_res, point_expected), eps)

if __name__ == '__main__':
    unittest.main()
