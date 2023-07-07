from typing import Optional, Callable, NoReturn, List, Tuple
import numpy as np
import numpy.typing as npt
import tkinter as tk

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