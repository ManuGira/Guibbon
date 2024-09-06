from typing import Optional, Callable, NoReturn, List, Tuple, Any
import numpy as np
import numpy.typing as npt
import abc

Image_t = npt.NDArray[np.uint8]

Point2Di = Tuple[int, int]
Point2D = Tuple[float, float]

Point2DList = List[Point2D]

CallbackRadioButtons = Optional[Callable[[int, str], NoReturn]]

tkEvent = Any

# foo(event) -> None
CallbackPoint = Optional[Callable[[tkEvent], NoReturn]]

# foo(event, point_xy_list) -> None
CallbackPolygon = Optional[Callable[[tkEvent, Point2DList], NoReturn]]

# foo(event, point0_xy, point1_xy) -> None
CallbackRect = Optional[Callable[[tkEvent, Point2D, Point2D], NoReturn]]

# foo(cvevent, x, y, flag, param) -> None
CallbackMouse = Optional[Callable[[int, int, int, int, None], NoReturn]]


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
