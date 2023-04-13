import tkinter

import enum
from typing import Optional, Callable, NoReturn, Tuple
import tkinter as tk

# foo(event) -> None
Callback = Optional[Callable[[tk.Event], NoReturn]]

class Point:
    class State(enum.IntEnum):
        NORMAL = 0
        HOVERED = 1
        DRAGGED = 2

    colors = {
        State.NORMAL: '#%02x%02x%02x' % (0, 0, 255),
        State.HOVERED: '#%02x%02x%02x' % (0, 255, 255),
        State.DRAGGED: '#%02x%02x%02x' % (255, 255, 0),
    }

    radius = {
        State.NORMAL: 5,
        State.HOVERED: 7,
        State.DRAGGED: 7,
    }

    def __init__(self, canvas: tk.Canvas, point_xy: Tuple[float, float], label:str="", on_click:Callback=None, on_drag:Callback=None, on_release:Callback=None):
        self.canvas = canvas
        self.state: Point.State = Point.State.NORMAL
        self.point_xy = point_xy
        self.label = label
        self.visible: bool = True

        self.circle_id = self.canvas.create_oval(0, 0, 1, 1, fill=Point.colors[self.state], outline="#FFFFFF", width=2)

        self.on_click = on_click
        self.canvas.tag_bind(self.circle_id, "<Button-1>", self._on_click)

        self.on_drag = on_drag
        self.canvas.tag_bind(self.circle_id, "<B1-Motion>", self._on_drag)

        self.on_release = on_release
        self.canvas.tag_bind(self.circle_id, "<ButtonRelease-1>", self._on_release)

        self.canvas.tag_bind(self.circle_id, "<Enter>", self._on_enter)
        self.canvas.tag_bind(self.circle_id, "<Leave>", self._on_leave)

    def update(self):
        radius = Point.radius[self.state]
        x1 = self.point_xy[0] - radius
        y1 = self.point_xy[1] - radius
        x2 = self.point_xy[0] + radius
        y2 = self.point_xy[1] + radius
        self.canvas.coords(self.circle_id, x1, y1, x2, y2)
        self.canvas.itemconfig(self.circle_id, fill=Point.colors[self.state])
        self.canvas.tag_raise(self.circle_id)


    def _on_click(self, event):
        self.state = Point.State.DRAGGED
        self.update()
        if self.on_click is not None:
            self.on_click(event)


    def _on_drag(self, event):
        try:
            self.point_xy = (event.x, event.y)
            self.state = Point.State.DRAGGED
            self.update()
            if self.on_drag is not None:
                self.on_drag(event)
        except Exception as e:
            print(f"ERROR: {self}: self._on_drag({event}) --->", e)
            raise(e)

    def _on_release(self, event):
        self.state = Point.State.HOVERED
        self.update()
        if self.on_release is not None:
            self.on_release(event)

    def _on_enter(self, event):
        if self.state is not Point.State.DRAGGED:
            self.state = Point.State.HOVERED
            self.update()

    def _on_leave(self, event):
        self.state = Point.State.NORMAL
        self.update()


# class Polygon:
#     def __init__(self, canvas: tk.Canvas, xs: float, ys: float, labels: str = "", on_click: Callback = None, on_drag: Callback = None, on_release: Callback = None):
#         self.canvas = canvas