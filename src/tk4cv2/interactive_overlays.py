from typing import Optional, Callable, NoReturn, Tuple, List, Sequence
from .typedef import Point2D, Point2DList, CallbackPoint, CallbackPolygon

import enum
import tkinter as tk

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

    def __init__(self, canvas: tk.Canvas, point_xy: Point2D, label:str="", on_click:CallbackPoint=None, on_drag:CallbackPoint=None, on_release:CallbackPoint=None):
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


class Polygon:
    def __init__(self, canvas: tk.Canvas, point_xy_list: Point2DList, label:str="", on_click:CallbackPolygon=None, on_drag:CallbackPolygon=None, on_release:CallbackPolygon=None):
        self.canvas = canvas
        self.point_xy_list = point_xy_list + []
        self.label = label
        self.visible: bool = True

        self.on_click = on_click
        self.on_drag = on_drag
        self.on_release = on_release
        N = len(self.point_xy_list)

        self.ipoints = []
        on_drag_lambdas: Sequence[CallbackPoint] = [lambda event, k_=k: self._on_drag(k_, event) for k in range(N)]

        for k, point_xy in enumerate(self.point_xy_list):
            # subscribe to on_click only if needed.
            # subscribe to on_drag in any cases (to update points coordinates). Use lambda to pass point index.
            # subscribe to on_release only if needed.
            ipoint = Point(canvas, point_xy, label="",
                    on_click=None if on_click is None else self._on_click,
                    on_drag=on_drag_lambdas[k],  # k_=k to fix value of k
                    on_release=None if on_release is None else self._on_release)
            self.ipoints.append(ipoint)

        self.lines = []
        for i in range(N):
            i1 = i
            i2 = (i+1)%N
            line_id = self.canvas.create_line(-1, -1, -1, -1, fill="green", width=5)
            self.lines.append((i1, i2, line_id))
        self.update()


    def update(self):
        # draw lines
        for i1, i2, line_id in self.lines:
            x1, y1 = self.point_xy_list[i1]
            x2, y2 = self.point_xy_list[i2]
            self.canvas.coords(line_id, x1, y1, x2, y2)
            self.canvas.tag_raise(line_id)


        for ipoint in self.ipoints:
            ipoint.update()

    def _on_click(self, event):
        if self.on_click is not None:
            self.on_click(event, self.point_xy_list)

    def _on_drag(self, i, event):
        try:
            print(i, event)
            self.point_xy_list[i] = (event.x, event.y)
            if self.on_drag is not None:
                self.on_drag(event, self.point_xy_list)
        except Exception as e:
            print(f"ERROR: {self}: self._on_drag({event}) --->", e)
            raise(e)

    def _on_release(self, event):
        if self.on_release is not None:
            self.on_release(event, self.point_xy_list)
