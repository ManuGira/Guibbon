from .typedef import Point2D
from . import transform_matrix as tmat
import tkinter as tk


class MousePan:
    def __init__(self, button_num, on_click=None, on_drag=None, on_release=None):
        self.button_num = button_num
        self.on_click = on_click
        self.on_drag = on_drag
        self.on_release = on_release

        self.is_down = False
        self.p1_xy: Point2D = (0, 0)
        self.p0_xy: Point2D = (0, 0)

    def on_tk_event(self, event, can2img_matrix: tmat.TransformMatrix):
        can_xy = event.x, event.y
        img_xy = tmat.apply(can2img_matrix, can_xy)

        if event.type == tk.EventType.ButtonPress and event.num == self.button_num:
            self.is_down = True
            self.p0_xy = img_xy
            self.p1_xy = img_xy
            if self.on_click is not None:
                self.on_click(self.p0_xy)

        if event.type == tk.EventType.Motion and self.is_down:
            self.p1_xy = img_xy
            if self.on_drag is not None:
                self.on_drag(self.p0_xy, self.p1_xy)

        if event.type == tk.EventType.ButtonRelease and self.is_down and event.num == self.button_num:
            if self.on_release is not None:
                self.on_release(self.p0_xy, self.p1_xy)
            self.is_down = False
