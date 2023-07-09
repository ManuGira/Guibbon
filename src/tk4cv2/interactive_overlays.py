from typing import Sequence, Optional

import numpy as np

from .typedef import Point2D, Point2DList, CallbackPoint, CallbackPolygon, CallbackRect

import enum
import tkinter as tk


class Magnets:
    def __init__(self, canvas, point_xy_list: Point2DList, img2canvas_space_func, visible=False):
        self.canvas = canvas
        self.point_xy_list = point_xy_list
        self.img2canvas_space_func = img2canvas_space_func
        self.visible = visible

    def get_point_in_canvas_space(self) -> Point2DList:
        return [self.img2canvas_space_func(x_img, y_img) for x_img, y_img in self.point_xy_list]

    def get_point_in_img_space(self) -> Point2DList:
        return self.point_xy_list

    def find_nearest_magnet(self, x_can, y_can):
        magnets_can = self.get_point_in_canvas_space()
        dists = np.array([x_can, y_can]) - magnets_can
        dists = np.sqrt(np.sum(dists**2, axis=1))
        ind = np.argmin(dists)
        if dists[ind] < 50:
            return magnets_can[ind]
        else:
            return x_can, y_can


class State(enum.IntEnum):
    NORMAL = 0
    HOVERED = 1
    DRAGGED = 2

class Point:
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

    def __init__(self, canvas: tk.Canvas, point_xy: Point2D, label:str="",
                 on_click:CallbackPoint=None,
                 on_drag:CallbackPoint=None,
                 on_release:CallbackPoint=None,
                 magnets: Optional[Magnets]=None):
        self.canvas = canvas
        self.state: State = State.NORMAL
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

        self.magnets = magnets


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
        self.state = State.DRAGGED
        self.update()
        if self.on_click is not None:
            self.on_click(event)


    def _on_drag(self, event):
        try:
            if self.magnets is not None:
                event.x, event.y = self.magnets.find_nearest_magnet(event.x, event.y)
            self.point_xy = (event.x, event.y)
            self.state = State.DRAGGED
            self.update()
            if self.on_drag is not None:
                self.on_drag(event)
        except Exception as e:
            print(f"ERROR: {self}: self._on_drag({event}) --->", e)
            raise e

    def _on_release(self, event):
        self.state = State.HOVERED
        self.update()
        if self.on_release is not None:
            self.on_release(event)

    def _on_enter(self, event):
        if self.state is not State.DRAGGED:
            self.state = State.HOVERED
            self.update()

    def _on_leave(self, event):
        self.state = State.NORMAL
        self.update()


class Polygon:
    colors = {
        State.NORMAL: '#%02x%02x%02x' % (0, 255, 0),
        State.HOVERED: '#%02x%02x%02x' % (127, 255, 127),
        State.DRAGGED: '#%02x%02x%02x' % (255, 255, 0),
    }

    def __init__(self, canvas: tk.Canvas, point_xy_list: Point2DList, label:str="",
                 on_click:CallbackPolygon=None,
                 on_drag:CallbackPolygon=None,
                 on_release:CallbackPolygon=None):
        self.canvas = canvas
        self.point_xy_list = point_xy_list + []
        self.label = label
        self.visible: bool = True
        self.state: State = State.NORMAL

        self.on_click = on_click
        self.on_drag = on_drag
        self.on_release = on_release
        N = len(self.point_xy_list)

        # k_=k to fix value of k
        on_drag_lambdas: Sequence[CallbackPoint] = [lambda event, k_=k: self._on_drag(k_, event) for k in range(N)]

        self.ipoints = []
        for k, point_xy in enumerate(self.point_xy_list):
            # subscribe to on_click only if needed.
            # subscribe to on_drag in any cases (to update points coordinates). Use lambda to pass point index.
            # subscribe to on_release only if needed.
            ipoint = Point(canvas, point_xy, label="",
                    on_click=None if on_click is None else self._on_click,
                    on_drag=on_drag_lambdas[k],
                    on_release=None if on_release is None else self._on_release)
            self.ipoints.append(ipoint)

        self.lines = self._create_lines()

        self.update()

    def _create_lines(self):
        lines = []
        N = len(self.ipoints)
        for i in range(N):
            i1 = i
            i2 = (i + 1) % N
            line_id = self.canvas.create_line(-1, -1, -1, -1, fill=Polygon.colors[self.state], width=5)
            lines.append((i1, i2, line_id))
        return lines

    def _update_lines(self):
        # draw lines
        for i1, i2, line_id in self.lines:
            x1, y1 = self.point_xy_list[i1]
            x2, y2 = self.point_xy_list[i2]
            self.canvas.coords(line_id, x1, y1, x2, y2)
            self.canvas.tag_raise(line_id)

    def _update_points(self):
        for ipoint in self.ipoints:
            ipoint.update()

    def update(self):
        self._update_lines()
        self._update_points()

    def _on_click(self, event):
        if self.on_click is not None:
            self.on_click(event, self.point_xy_list)

    def _on_drag(self, i, event):
        try:
            self.point_xy_list[i] = (event.x, event.y)
            self._update_lines()
            if self.on_drag is not None:
                self.on_drag(event, self.point_xy_list)
        except Exception as e:
            print(f"ERROR: {self}: self._on_drag({event}) --->", e)
            raise e

    def _on_release(self, event):
        if self.on_release is not None:
            self.on_release(event, self.point_xy_list)

class Rectangle(Polygon):
    def __init__(self, canvas: tk.Canvas, point0_xy: Point2D, point1_xy: Point2D, label:str="",
                on_click:CallbackRect=None,
                on_drag:CallbackRect=None,
                on_release:CallbackRect=None):

        # wrap user callback to convert signature from CallbackRect to CallbackPolygon
        lambda0 = None if on_click is None else lambda event, point_list_xy: on_click(event, point_list_xy[0], point_list_xy[1])
        on_click_rect: CallbackPolygon = lambda0

        lambda1 = None if on_drag is None else lambda event, point_list_xy:  on_drag(event, point_list_xy[0], point_list_xy[1])
        on_drag_rect: CallbackPolygon = lambda1

        lambda2 = None if on_release is None else lambda event, point_list_xy: on_release(event, point_list_xy[0], point_list_xy[1])
        on_release_rect: CallbackPolygon = lambda2

        # Create a Point2DList from the 2 Point2D
        point_list_xy = [point0_xy, point1_xy]

        # create an instance of Polygon using wrapped callbacks
        super().__init__(canvas, point_list_xy, label,
                on_click=None if on_click is None else on_click_rect,
                on_drag=None if on_drag is None else on_drag_rect,
                on_release=None if on_release is None else on_release_rect)

    def _create_lines(self):
        return [(-1, -1, self.canvas.create_line(-1, -1, -1, -1, fill=Polygon.colors[self.state], width=5)) for i in range(4)]

    def _update_lines(self):
        left = self.point_xy_list[0][0]
        top = self.point_xy_list[0][1]
        right = self.point_xy_list[1][0]
        bottom = self.point_xy_list[1][1]

        line_id = self.lines[0][2]
        self.canvas.coords(line_id, left, top, right, top)
        self.canvas.tag_raise(line_id)

        line_id = self.lines[1][2]
        self.canvas.coords(line_id, right, top, right, bottom)
        self.canvas.tag_raise(line_id)

        line_id = self.lines[2][2]
        self.canvas.coords(line_id, right, bottom, left, bottom)
        self.canvas.tag_raise(line_id)

        line_id = self.lines[3][2]
        self.canvas.coords(line_id, left, bottom, left, top)
        self.canvas.tag_raise(line_id)
