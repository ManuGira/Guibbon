from typing import Sequence, Optional

import numpy as np

from guibbon.typedef import Point2D, Point2DList, CallbackPoint, CallbackPolygon, CallbackRect, InteractivePolygon, InteractivePoint

import enum
import tkinter as tk
from guibbon import transform_matrix as tmat
from guibbon.transform_matrix import TransformMatrix


class State(enum.IntEnum):
    NORMAL = 0
    HOVERED = 1
    DRAGGED = 2


class Magnets:
    DISTANCE_THERSHOLD = 20  # distance on img space
    COLOR = "#%02x%02x%02x" % (255, 0, 255)

    def __init__(self, canvas: tk.Canvas, point_xy_list: Point2DList, dist_threshold=DISTANCE_THERSHOLD):
        self.canvas = canvas
        self.point_xy_list = point_xy_list

        self.dist_threshold = dist_threshold
        self.visible = False
        self.circle_id_list = [self.canvas.create_oval(0, 0, 1, 1, fill=Magnets.COLOR, width=0) for _ in point_xy_list]

        self.img2can_matrix: TransformMatrix = tmat.identity_matrix()

    def update(self):
        radius = Point.radius[State.NORMAL] // 2
        item_state = "normal" if self.visible else "hidden"
        for circle_id, point_xy in zip(self.circle_id_list, self.point_xy_list):
            point_xy = tmat.apply(self.img2can_matrix, point_xy)
            point_xy = (int(round(point_xy[0])), int(round(point_xy[1])))
            x1 = point_xy[0] - radius
            y1 = point_xy[1] - radius
            x2 = point_xy[0] + radius
            y2 = point_xy[1] + radius
            self.canvas.coords(circle_id, x1, y1, x2, y2)
            self.canvas.itemconfig(circle_id, fill=Magnets.COLOR, state=item_state)
            self.canvas.tag_raise(circle_id)

    def snap_to_nearest_magnet(self, point_xy_img: Point2D) -> Point2D:
        if len(self.point_xy_list) == 0:
            return point_xy_img

        dists2 = np.array(point_xy_img) - np.array(self.point_xy_list)
        dists2 = np.sum(dists2**2, axis=1)
        ind = np.argmin(dists2)
        if dists2[ind] < self.dist_threshold**2:
            return self.point_xy_list[ind]
        else:
            return point_xy_img

    def set_img2can_matrix(self, img2can_matrix: TransformMatrix):
        self.img2can_matrix = img2can_matrix.copy()


class Point(InteractivePoint):
    colors = {
        State.NORMAL: "#%02x%02x%02x" % (0, 0, 255),
        State.HOVERED: "#%02x%02x%02x" % (0, 255, 255),
        State.DRAGGED: "#%02x%02x%02x" % (255, 255, 0),
    }

    radius = {
        State.NORMAL: 5,
        State.HOVERED: 7,
        State.DRAGGED: 7,
    }

    def __init__(
        self,
        canvas: tk.Canvas,
        point_xy: Point2D,
        label: str = "",
        on_click: CallbackPoint = None,
        on_drag: CallbackPoint = None,
        on_release: CallbackPoint = None,
        img2can_matrix: Optional[TransformMatrix] = None,
        magnets: Optional[Magnets] = None,
    ):
        if img2can_matrix is None:
            img2can_matrix = tmat.identity_matrix()

        self.canvas = canvas
        self.state: State = State.NORMAL
        self.point_xy = point_xy  # coordinates are expressed in img space
        self.label = label
        self.img2can_matrix: TransformMatrix
        self.can2img_matrix: TransformMatrix
        self.set_img2can_matrix(img2can_matrix)
        self.magnets = magnets

        self.visible: bool = True

        self.circle_id = self.canvas.create_oval(0, 0, 1, 1, fill=Point.colors[self.state], outline="#FFFFFF", width=2)

        self.on_click = on_click
        self.canvas.tag_bind(self.circle_id, "<Button-1>", lambda event: self._on_click(event))

        self.on_drag = on_drag
        self.canvas.tag_bind(self.circle_id, "<B1-Motion>", lambda event: self._on_drag(event))

        self.on_release = on_release
        self.canvas.tag_bind(self.circle_id, "<ButtonRelease-1>", lambda event: self._on_release(event))

        self.canvas.tag_bind(self.circle_id, "<Enter>", self._on_enter)
        self.canvas.tag_bind(self.circle_id, "<Leave>", self._on_leave)

    def delete(self):
        self.canvas.delete(self.circle_id)

    def update(self):
        self.update_magnets()
        radius = Point.radius[self.state]
        can_x, can_y = tmat.apply(self.img2can_matrix, self.point_xy)
        x1 = can_x - radius
        y1 = can_y - radius
        x2 = can_x + radius
        y2 = can_y + radius
        self.canvas.coords(self.circle_id, x1, y1, x2, y2)
        item_state = "normal" if self.visible else "hidden"
        self.canvas.itemconfig(self.circle_id, fill=Point.colors[self.state], state=item_state)
        self.canvas.tag_raise(self.circle_id)

    def set_img2can_matrix(self, img2can_matrix: TransformMatrix):
        self.img2can_matrix = img2can_matrix.copy()
        self.can2img_matrix = np.linalg.inv(self.img2can_matrix).astype(float)

    def get_img_point_xy(self) -> Point2D:
        return self.point_xy

    def set_img_point_xy(self, img_point_xy: Point2D):
        self.point_xy = img_point_xy

    def get_can_point_xy(self) -> Point2D:
        return tmat.apply(self.img2can_matrix, self.point_xy)

    def set_can_point_xy(self, can_point_xy: Point2D):
        self.point_xy = tmat.apply(self.can2img_matrix, can_point_xy)

    def update_magnets(self):
        if self.magnets is not None:
            self.magnets.visible = self.state in [State.HOVERED, State.DRAGGED]
            self.magnets.set_img2can_matrix(self.img2can_matrix)
            self.magnets.update()

    def _on_click(self, event):
        self.state = State.DRAGGED
        self.update()
        if self.on_click is not None:
            p_xy = event.x, event.y
            p_xy = tmat.apply(self.can2img_matrix, p_xy)
            if self.magnets is not None:
                p_xy = self.magnets.snap_to_nearest_magnet(p_xy)
            event.x, event.y = p_xy
            self.on_click(event)

    def _on_drag(self, event):
        try:
            can_xy = event.x, event.y
            img_xy = tmat.apply(self.can2img_matrix, can_xy)
            if self.magnets is not None:
                img_xy = self.magnets.snap_to_nearest_magnet(img_xy)
            self.set_img_point_xy(img_xy)

            self.state = State.DRAGGED
            self.update()
            if self.on_drag is not None:
                event.x, event.y = img_xy
                self.on_drag(event)
        except Exception as e:
            print(f"ERROR: {self}: self._on_drag({event}) --->", e)
            raise e

    def _on_release(self, event):
        self.state = State.HOVERED
        self.update()
        if self.on_release is not None:
            can_xy = event.x, event.y
            img_xy = tmat.apply(self.can2img_matrix, can_xy)
            if self.magnets is not None:
                img_xy = self.magnets.snap_to_nearest_magnet(img_xy)
            event.x, event.y = img_xy
            self.on_release(event)

    def _on_enter(self, event):
        if self.state is not State.DRAGGED:
            self.state = State.HOVERED
            self.update()

    def _on_leave(self, event):
        if self.state is not State.DRAGGED:
            self.state = State.NORMAL
        self.update()

    def set_visible(self, value: bool):
        if value == self.visible:
            return
        self.visible = value

