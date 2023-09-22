import dataclasses
import sys
import unittest

import numpy as np
from tk4cv2.typedef import Point2D

from tk4cv2 import transform_matrix as tmat

def maxdiff(arr1, arr2):
    return np.max(abs(arr1-arr2).flatten())


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
            self.assertLess(maxdiff(mat, expected), 1e-6)

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
                self.assertLess(maxdiff(mat, expected), 1e-6)

        self.assertLess(maxdiff(tmat.T((0, 0)), tmat.I()), 1e-6)

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
                self.assertLess(maxdiff(mat, expected), 1e-6)

        self.assertLess(maxdiff(tmat.S((1, 1)), tmat.I()), 1e-6)


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
                self.assertLess(maxdiff(mat, expected), 1e-6)

        self.assertLess(maxdiff(tmat.R(0), tmat.I()), 1e-6)
        self.assertLess(maxdiff(tmat.R(np.pi*2), tmat.I()), 1e-6)

if __name__ == '__main__':
    unittest.main()
