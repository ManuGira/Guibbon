from typing import Optional, Callable, NoReturn, List, Tuple, Literal, Annotated
import numpy as np
import numpy.typing as npt
import tkinter as tk
import abc

Image_t = Optional[npt.NDArray[np.uint8]]

Point2D = Tuple[float, float]

Point2DList = List[Point2D]

# foo(event) -> None
CallbackPoint = Optional[Callable[[tk.Event], NoReturn]]

# foo(event, point_xy_list) -> None
CallbackPolygon = Optional[Callable[[tk.Event, Point2DList], NoReturn]]

# foo(event, point0_xy, point1_xy) -> None
CallbackRect = Optional[Callable[[tk.Event, Point2D, Point2D], NoReturn]]

# foo(cvevent, x, y, flag, param) -> None
MouseCallback = Optional[Callable[[int, int, int, int, None], NoReturn]]

class InteractivePolygon(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def update(self):
        raise NotImplementedError

    @abc.abstractmethod
    def set_point_xy_list(self, point_xy_list: Point2DList):
        raise NotImplementedError
