

import tkinter as tk
from typing import Sequence, Optional

from guibbon.transform_matrix import TransformMatrix
from guibbon.typedef import Point2D, Point2DList, CallbackPoint, CallbackPolygon, CallbackRect, InteractivePolygon
from .base import State, Point, Magnets


class Polygon(InteractivePolygon):
    colors = {
        State.NORMAL: "#%02x%02x%02x" % (0, 255, 0),
        State.HOVERED: "#%02x%02x%02x" % (127, 255, 127),
        State.DRAGGED: "#%02x%02x%02x" % (255, 255, 0),
    }

    def __init__(
        self,
        canvas: tk.Canvas,
        point_xy_list: Point2DList,
        label: str = "",
        on_click: CallbackPolygon = None,
        on_drag: CallbackPolygon = None,
        on_release: CallbackPolygon = None,
        img2can_matrix: Optional[TransformMatrix] = None,
        magnets: Optional[Magnets] = None,
    ):
        self.canvas = canvas
        self.label = label
        self.visible: bool = True
        self.state: State = State.NORMAL

        self.on_click = on_click
        self.on_drag = on_drag
        self.on_release = on_release
        N = len(point_xy_list)

        # create on_drag lambdas to pass point index and fix value of k
        def make_on_drag(self, k: int):
            return lambda event: self._on_drag(k, event)

        on_drag_lambdas: Sequence[CallbackPoint] = [make_on_drag(self, k) for k in range(N)]

        self.ipoints = []
        for k, point_xy in enumerate(point_xy_list):
            # subscribe to on_click only if needed.
            # subscribe to on_drag in any cases (to update points coordinates). Use lambda to pass point position.
            # subscribe to on_release only if needed.
            ipoint = Point(
                canvas,
                point_xy,
                label="",
                on_click=None if on_click is None else self._on_click,
                on_drag=on_drag_lambdas[k],
                on_release=None if on_release is None else self._on_release,
                img2can_matrix=img2can_matrix,
                magnets=magnets,
            )
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
        item_state = "normal" if self.visible else "hidden"
        point_xy_list = [ipoint.get_can_point_xy() for ipoint in self.ipoints]
        point_xy_list = [(int(round(x)), int(round(y))) for x, y in point_xy_list]
        for i1, i2, line_id in self.lines:
            x1, y1 = point_xy_list[i1]
            x2, y2 = point_xy_list[i2]
            self.canvas.coords(line_id, x1, y1, x2, y2)
            self.canvas.itemconfig(line_id, state=item_state)
            self.canvas.tag_raise(line_id)

    def _update_points(self):
        for ipoint in self.ipoints:
            ipoint.update()

    def update(self):
        self._update_lines()
        self._update_points()

    def _on_click(self, event):
        if self.on_click is not None:
            point_xy_list = [ipoint.get_img_point_xy() for ipoint in self.ipoints]
            self.on_click(event, point_xy_list)

    def _on_drag(self, i, event):
        try:
            self._update_lines()
            if self.on_drag is not None:
                point_xy_list = [ipoint.get_img_point_xy() for ipoint in self.ipoints]
                self.on_drag(event, point_xy_list)
        except Exception as e:
            print(f"ERROR: {self}: self._on_drag({event}) --->", e)
            raise e

    def _on_release(self, event):
        if self.on_release is not None:
            point_xy_list = [ipoint.get_img_point_xy() for ipoint in self.ipoints]
            self.on_release(event, point_xy_list)

    def set_img2can_matrix(self, img2can_matrix: TransformMatrix):
        for ipoint in self.ipoints:
            ipoint.set_img2can_matrix(img2can_matrix)

    def set_point_xy_list(self, point_xy_list: Point2DList):
        assert len(point_xy_list) == len(self.ipoints)
        for ipoint, point_xy in zip(self.ipoints, point_xy_list):
            ipoint.set_img_point_xy(point_xy)
            self.update()

    def set_visible(self, value: bool):
        if value == self.visible:
            return
        self.visible = value
        for ipoint in self.ipoints:
            ipoint.set_visible(value)


class Rectangle(Polygon):
    def __init__(
        self,
        canvas: tk.Canvas,
        point0_xy: Point2D,
        point1_xy: Point2D,
        label: str = "",
        on_click: CallbackRect = None,
        on_drag: CallbackRect = None,
        on_release: CallbackRect = None,
        img2can_matrix: Optional[TransformMatrix] = None,
        magnets: Optional[Magnets] = None,
    ):
        # wrap user callback to convert signature from CallbackRect to CallbackPolygon
        lambda0 = None if on_click is None else lambda event, point_list_xy: on_click(event, point_list_xy[0], point_list_xy[1])
        on_click_rect: CallbackPolygon = lambda0

        lambda1 = None if on_drag is None else lambda event, point_list_xy: on_drag(event, point_list_xy[0], point_list_xy[1])
        on_drag_rect: CallbackPolygon = lambda1

        lambda2 = None if on_release is None else lambda event, point_list_xy: on_release(event, point_list_xy[0], point_list_xy[1])
        on_release_rect: CallbackPolygon = lambda2

        # Create a Point2DList from the 2 Point2D
        point_list_xy = [point0_xy, point1_xy]

        # create an instance of Polygon using wrapped callbacks
        super().__init__(
            canvas,
            point_list_xy,
            label,
            on_click=None if on_click is None else on_click_rect,
            on_drag=None if on_drag is None else on_drag_rect,
            on_release=None if on_release is None else on_release_rect,
            img2can_matrix=img2can_matrix,
            magnets=magnets,
        )

    def _create_lines(self):
        return [(-1, -1, self.canvas.create_line(-1, -1, -1, -1, fill=Polygon.colors[self.state], width=5)) for i in range(4)]

    def _update_lines(self):
        item_state = "normal" if self.visible else "hidden"

        point_xy_list = [ipoint.get_can_point_xy() for ipoint in self.ipoints]
        point_xy_list = [(int(round(x)), int(round(y))) for x, y in point_xy_list]

        left = point_xy_list[0][0]
        top = point_xy_list[0][1]
        right = point_xy_list[1][0]
        bottom = point_xy_list[1][1]

        line_id = self.lines[0][2]
        self.canvas.coords(line_id, left, top, right, top)
        self.canvas.itemconfig(line_id, state=item_state)
        self.canvas.tag_raise(line_id)

        line_id = self.lines[1][2]
        self.canvas.coords(line_id, right, top, right, bottom)
        self.canvas.itemconfig(line_id, state=item_state)
        self.canvas.tag_raise(line_id)

        line_id = self.lines[2][2]
        self.canvas.coords(line_id, right, bottom, left, bottom)
        self.canvas.itemconfig(line_id, state=item_state)
        self.canvas.tag_raise(line_id)

        line_id = self.lines[3][2]
        self.canvas.coords(line_id, left, bottom, left, top)
        self.canvas.itemconfig(line_id, state=item_state)
        self.canvas.tag_raise(line_id)
