from typing import Optional, Callable
import numpy as np
import numpy.typing as npt
import tkinter as tk
import abc

Image_t = npt.NDArray[np.uint8]

Point2D = tuple[float, float]

Point2DList = list[Point2D]

CallbackRadioButtons = Optional[Callable[[int, str], None]]

# foo(event) -> None
CallbackPoint = Optional[Callable[[tk.Event], None]]

# foo(event, point_xy_list) -> None
CallbackPolygon = Optional[Callable[[tk.Event, Point2DList], None]]

# foo(event, point0_xy, point1_xy) -> None
CallbackRect = Optional[Callable[[tk.Event, Point2D, Point2D], None]]

# foo(cvevent, x, y, flag, param) -> None
CallbackMouse = Optional[Callable[[int, int, int, int, None], None]]


class InteractivePoint(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def set_img_point_xy(self, img_point_xy: Point2D):
        pass

    @abc.abstractmethod
    def set_visible(self, value: bool):
        pass


class InteractivePolygon(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def set_point_xy_list(self, point_xy_list: Point2DList):
        pass

    @abc.abstractmethod
    def set_visible(self, value: bool):
        pass
