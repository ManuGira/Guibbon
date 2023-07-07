from typing import Sequence
from .typedef import Point2D, Point2DList, CallbackPoint, CallbackPolygon, CallbackRect

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

    def __init__(self, canvas: tk.Canvas, point_xy: Point2D, label:str="",
                 on_click:CallbackPoint=None,
                 on_drag:CallbackPoint=None,
                 on_release:CallbackPoint=None):
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
            raise e

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

    def __init__(self, canvas: tk.Canvas, point_xy_list: Point2DList, label:str="",
                 on_click:CallbackPolygon=None,
                 on_drag:CallbackPolygon=None,
                 on_release:CallbackPolygon=None):
        self.canvas = canvas
        self.point_xy_list = point_xy_list + []
        self.label = label
        self.visible: bool = True

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
            line_id = self.canvas.create_line(-1, -1, -1, -1, fill="green", width=5)
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
        return [self.canvas.create_line(-1, -1, -1, -1, fill="green", width=5) for i in range(4)]

    def _update_lines(self):
        left = self.point_xy_list[0][0]
        top = self.point_xy_list[0][1]
        right = self.point_xy_list[1][0]
        bottom = self.point_xy_list[1][1]

        line_id = self.lines[0]
        self.canvas.coords(line_id, left, top, right, top)
        self.canvas.tag_raise(line_id)

        line_id = self.lines[1]
        self.canvas.coords(line_id, right, top, right, bottom)
        self.canvas.tag_raise(line_id)

        line_id = self.lines[2]
        self.canvas.coords(line_id, right, bottom, left, bottom)
        self.canvas.tag_raise(line_id)

        line_id = self.lines[3]
        self.canvas.coords(line_id, left, bottom, left, top)
        self.canvas.tag_raise(line_id)



# class Rectangle:
#     def __new__(cls, canvas: tk.Canvas, point0_xy: Point2D, point1_xy: Point2D, label:str="",
#                  on_click:CallbackRect=None,
#                  on_drag:CallbackRect=None,
#                  on_release:CallbackRect=None):
#
#         # wrap user callback to convert signature from CallbackRect to CallbackPolygon
#         on_click_rect: CallbackPolygon = lambda event, point_list_xy: on_click(event, point_list_xy[0], point_list_xy[1])
#         on_drag_rect: CallbackPolygon = lambda event, point_list_xy: on_drag(event, point_list_xy[0], point_list_xy[1])
#         on_release_rect: CallbackPolygon = lambda event, point_list_xy: on_release(event, point_list_xy[0], point_list_xy[1])
#
#         # Create a Point2DList from the 2 Point2D
#         point_list_xy = [point0_xy, point1_xy]
#
#         # create an instance of Polygon using wrapped callbacks
#         polygon_instance = Polygon(canvas, point_list_xy, label, on_click_rect, on_drag_rect, on_release_rect)
#
#         # override methods to draw a rectangle instead of a polygon
#         polygon_instance._create_lines = lambda canvas, N: cls._create_lines(polygon_instance, canvas)
#         polygon_instance._update_lines = lambda: cls._update_lines(polygon_instance)
#
#         # returns the Polygon instance
#         return polygon_instance
#
#     @staticmethod
#     def _create_lines(self, canvas):
#         return [canvas.create_line(-1, -1, -1, -1, fill="green", width=5) for i in range(4)]
#
#     @staticmethod
#     def _update_lines(self):
#         left = self.point_xy_list[0][0]
#         top = self.point_xy_list[0][1]
#         right = self.point_xy_list[1][0]
#         bottom = self.point_xy_list[1][1]
#
#         line_id = self.lines[0]
#         self.canvas.coords(line_id, left, top, right, top)
#         self.canvas.tag_raise(line_id)
#
#         line_id = self.lines[1]
#         self.canvas.coords(line_id, right, top, right, bottom)
#         self.canvas.tag_raise(line_id)
#
#         line_id = self.lines[2]
#         self.canvas.coords(line_id, right, bottom, left, bottom)
#         self.canvas.tag_raise(line_id)
#
#         line_id = self.lines[3]
#         self.canvas.coords(line_id, left, bottom, left, top)
#         self.canvas.tag_raise(line_id)


# class Rectangle:
#     def __init__(self, canvas: tk.Canvas, point0_xy: Point2D, point1_xy: Point2D, label:str="",
#                  on_click:CallbackPolygon=None,
#                  on_drag:CallbackPolygon=None,
#                  on_release:CallbackPolygon=None):
#         self.canvas = canvas
#         self.point_xy_list = [point0_xy, point1_xy]
#         self.label = label
#         self.visible: bool = True
#
#         self.on_click = on_click
#         self.on_drag = on_drag
#         self.on_release = on_release
#         N = len(self.point_xy_list)
#
#         # k_=k to fix value of k
#         on_drag_lambdas: Sequence[CallbackPoint] = [lambda event, k_=k: self._on_drag(k_, event) for k in range(N)]
#
#         self.ipoints = []
#         for k, point_xy in enumerate(self.point_xy_list):
#             # subscribe to on_click only if needed.
#             # subscribe to on_drag in any cases (to update points coordinates). Use lambda to pass point index.
#             # subscribe to on_release only if needed.
#             ipoint = Point(canvas, point_xy, label="",
#                     on_click=None if on_click is None else self._on_click,
#                     on_drag=on_drag_lambdas[k],
#                     on_release=None if on_release is None else self._on_release)
#             self.ipoints.append(ipoint)
#
#         self.lines = [self.canvas.create_line(-1, -1, -1, -1, fill="green", width=5) for i in range(4)]
#         self.update()
#
#     def _update_lines(self):
#         # draw lines
#         left = self.point_xy_list[0][0]
#         top = self.point_xy_list[0][1]
#         right = self.point_xy_list[1][0]
#         bottom = self.point_xy_list[1][1]
#
#         line_id = self.lines[0]
#         self.canvas.coords(line_id, left, top, right, top)
#         self.canvas.tag_raise(line_id)
#
#         line_id = self.lines[1]
#         self.canvas.coords(line_id, right, top, right, bottom)
#         self.canvas.tag_raise(line_id)
#
#         line_id = self.lines[2]
#         self.canvas.coords(line_id, right, bottom, left, bottom)
#         self.canvas.tag_raise(line_id)
#
#         line_id = self.lines[3]
#         self.canvas.coords(line_id, left, bottom, left, top)
#         self.canvas.tag_raise(line_id)
#
#     def _update_points(self):
#         for ipoint in self.ipoints:
#             ipoint.update()
#
#     def update(self):
#         self._update_lines()
#         self._update_points()
#
#     def _on_click(self, event):
#         if self.on_click is not None:
#             self.on_click(event, self.point_xy_list)
#
#     def _on_drag(self, i, event):
#         try:
#             self.point_xy_list[i] = (event.x, event.y)
#             self._update_lines()
#             if self.on_drag is not None:
#                 self.on_drag(event, self.point_xy_list)
#         except Exception as e:
#             print(f"ERROR: {self}: self._on_drag({event}) --->", e)
#             raise e
#
#     def _on_release(self, event):
#         if self.on_release is not None:
#             self.on_release(event, self.point_xy_list)

#
# class Pomme:
#     def __init__(self, m, n):
#         self.m = m
#         self.n = n
#
#     def printm(self):
#         print("il y a", self.m, "trognons")
#
#     def printn(self):
#         print("il y a", self.n, "pommes")
#
# class Poire:
#     def __new__(cls, m, n):
#         pm = Pomme(m, n)
#         pm.printn = lambda: cls.printn(pm)
#         return pm
#
#     @staticmethod
#     def printn(self):
#         print("il y a", self.n, "poires")
#
# def main():
#     pr = Poire(4, 5)
#
#     pr.printm()
#     pr.printn()
#     pr.n = 10
#     pr.printn()
#
# if __name__ == '__main__':
#     main()