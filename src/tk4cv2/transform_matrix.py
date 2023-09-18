from typing import Optional, Callable, NoReturn, List, Tuple, Literal, Annotated
import numpy as np
import numpy.typing as npt
from .typedef import Point2D, Point2DList

# 3x3 matrix of a rigid transform
TransformMatrix = Optional[Annotated[npt.NDArray[float], Literal[3, 3]]]

def identity_matrix() -> TransformMatrix:
    return np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ], dtype=float)

def I() -> TransformMatrix:
    return identity_matrix()

def scale_matrix(scale_xy: Point2D) -> TransformMatrix:
    return np.array([
        [scale_xy[0], 0, 0],
        [0, scale_xy[1], 0],
        [0, 0, 1],
    ], dtype=float)

def S(scale_xy: Point2D) -> TransformMatrix:
    return scale_matrix(scale_xy)

def translation_matrix(translate_xy: Point2D) -> TransformMatrix:
    return np.array([
        [1, 0, translate_xy[0]],
        [0, 1, translate_xy[1]],
        [0, 0, 1],
    ], dtype=float)

def T(translate_xy: Point2D) -> TransformMatrix:
    return translation_matrix(translate_xy)

def rotation_matrix(theta_rad: float) -> TransformMatrix:
    cs = np.cos(theta_rad)
    sn = np.sin(theta_rad)
    return np.array([
        [cs, -sn, 0],
        [sn, cs, 0],
        [0, 0, 1],
    ], dtype=float)

def R(theta_rad: float) -> TransformMatrix:
    return rotation_matrix(theta_rad)

def apply(mat: TransformMatrix, point_xy: Point2D) -> Point2D:
    point_xyw = np.array([[point_xy[0]], [point_xy[1]], [1]], dtype=float)
    point_xyw = mat @ point_xyw
    point_xyw /= point_xyw[2]
    return (point_xyw[0, 0], point_xyw[1, 0])
