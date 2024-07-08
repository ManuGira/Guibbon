import dataclasses
import enum
import math
import tkinter as tk
import types
from typing import List, Any, Optional

import cv2
import numpy as np
from PIL import Image, ImageTk

from . import interactive_overlays
from . import mouse_pan
from . import transform_matrix as tm
from . import wrapped_tk_widgets as wtk
from .transform_matrix import TransformMatrix
from .typedef import Image_t, CallbackPoint, CallbackPolygon, CallbackRect, Point2D, Point2DList, CallbackMouse


class ImageViewer:
    class BUTTONNUM(enum.IntEnum):
        LEFT = 1
        MID = 2
        RIGHT = 3

    class EVENTSTATE(enum.IntEnum):
        SHIFT = 0x0001
        CAPS_LOCK = 0x0002
        CONTROL = 0x0004
        LEFT_ALT = 0x20000  # 0x0008
        NUM_LOCK = 0x0010
        # RIGHT_ALT = 0x20000  # 0x0080
        MOUSE_BUTTON_1 = 0x0100
        MOUSE_BUTTON_2 = 0x0200
        MOUSE_BUTTON_3 = 0x0400

    @dataclasses.dataclass()
    class Modifier:
        SHIFT: bool = False
        CAPS_LOCK: bool = False
        CONTROL: bool = False
        LEFT_ALT: bool = False
        NUM_LOCK: bool = False
        RIGHT_ALT: bool = False
        MOUSE_BUTTON_1: bool = False
        MOUSE_BUTTON_2: bool = False
        MOUSE_BUTTON_3: bool = False

    def __init__(self, master, height: int, width: int):
        self.frame = tk.Frame(master=master)
        self.canvas = tk.Canvas(master=self.frame, height=height, width=width, bg="gray10")
        self.canvas_shape_hw = (height, width)

        self.imgtk = None
        self.onMouse: CallbackMouse = None
        self.modifier = ImageViewer.Modifier()
        self.interactive_overlay_instance_list: List[Any] = []

        self.mouse_pan_calculator = mouse_pan.MousePan(on_drag=self.on_mouse_pan_drag, on_release=self.on_mouse_pan_release)

        self.mat: Image_t
        self.cv2_interpolation: int
        self.pan_xy: Point2D = (0.0, 0.0)
        self.cumulative_pan_xy: Point2D = (0.0, 0.0)
        self.zoom_factor: float
        self.img2can_matrix: TransformMatrix
        self.can2img_matrix: TransformMatrix

        self.set_img2can_matrix(tm.identity_matrix())

        self.canvas.pack(side=tk.TOP)

        self.toolbar_frame = tk.Frame(master=self.frame)
        toolbar_cfg = {"side": tk.LEFT, "padx": 1, "pady": 2}
        tk.Button(master=self.toolbar_frame, text="home", command=self.onclick_zoom_home).pack(toolbar_cfg)
        tk.Button(master=self.toolbar_frame, text="fit", command=self.onclick_zoom_fit).pack(toolbar_cfg)
        tk.Button(master=self.toolbar_frame, text="fill", command=self.onclick_zoom_fill).pack(toolbar_cfg)
        tk.Button(master=self.toolbar_frame, text="100%", command=self.onclick_zoom_100).pack(toolbar_cfg)
        self.zoom_entry = wtk.Entry(master=self.toolbar_frame, on_change=self.on_change_zoom)
        self.zoom_entry.pack(toolbar_cfg)
        tk.Label(master=self.toolbar_frame, text="%").pack(toolbar_cfg)

        self.is_mouse_panzoom_enabled = tk.BooleanVar()
        chk1 = tk.Checkbutton(master=self.toolbar_frame, text="mouse pan/zoom", variable=self.is_mouse_panzoom_enabled, onvalue=True, offvalue=False)
        chk1.pack(toolbar_cfg)
        chk1.select()

        # self.mouse_panzoom_checkbutton.configure(state='selected')
        # self.mouse_panzoom_checkbutton.state(["selected"])

        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        # <MODIFIER-MODIFIER-TYPE-DETAIL>
        # see https://dafarry.github.io/tkinterbook/tkinter-events-and-bindings.htm
        self.canvas.bind("<Motion>", self.on_event)
        self.canvas.bind("<ButtonPress>", self.on_event)
        self.canvas.bind("<ButtonRelease>", self.on_event)
        self.canvas.bind("<MouseWheel>", self.on_event)

    def setMouseCallback(self, onMouse, userdata=None):
        if not isinstance(onMouse, types.FunctionType) and not isinstance(onMouse, types.MethodType):
            raise TypeError(f"onMouse must be a function, got {type(onMouse)} instead")
        if userdata is not None:
            raise NotImplementedError("userdata argument of function setMouseCallback is not handled in current version of guibbon")

        self.onMouse = onMouse

    def on_event(self, event):
        # event x y flag param
        # 0 32 375 0 None   (motion)    <Motion event state=Mod1 x=196 y=353>
        # 1 175 300 1 None  (l-down)    <ButtonPress event state=Mod1 num=1 x=196 y=353>
        # 4 175 300 0 None  (l-up)      <ButtonRelease event state=Mod1|Button1 num=1 x=196 y=353>
        # 0 175 300 0 None

        # 2 445 402 2 None  (r-down)    <ButtonPress event state=Mod1 num=3 x=196 y=353>
        # 5 445 402 0 None  (r-up)      <ButtonRelease event state=Mod1|Button3 num=3 x=196 y=353>
        # 0 445 402 0 None

        # 3 444 147 4 None (m-down)  <ButtonPress event state=Mod1 num=2 x=560 y=211>
        # 6 444 147 0 None (m-up)    <ButtonRelease event state=Mod1|Button2 num=2 x=560 y=211>

        # wheel down - up
        # 10 301 327 7864320 None  (wheel)  <MouseWheel event state=Mod1 delta=120 x=383 y=301>
        # 10 301 327 -7864320 None

        # The obvious information
        is_motion = event.type == tk.EventType.Motion
        is_buttonpress = event.type == tk.EventType.ButtonPress
        is_buttonrelease = event.type == tk.EventType.ButtonRelease
        is_mousewheel = event.type == tk.EventType.MouseWheel
        assert is_buttonpress or is_buttonrelease or is_motion or is_mousewheel

        is_left = event.num == ImageViewer.BUTTONNUM.LEFT
        is_mid = event.num == ImageViewer.BUTTONNUM.MID
        is_right = event.num == ImageViewer.BUTTONNUM.RIGHT

        # cv2.EVENT_LBUTTONDBLCLK = 7
        # cv2.EVENT_LBUTTONDOWN = 1
        # cv2.EVENT_LBUTTONUP = 4
        # cv2.EVENT_MBUTTONDBLCLK = 9
        # cv2.EVENT_MBUTTONDOWN = 3
        # cv2.EVENT_MBUTTONUP = 6
        # cv2.EVENT_MOUSEHWHEEL = 11
        # cv2.EVENT_MOUSEMOVE = 0
        # cv2.EVENT_MOUSEWHEEL = 10
        # cv2.EVENT_RBUTTONDBLCLK = 8
        # cv2.EVENT_RBUTTONDOWN = 2
        # cv2.EVENT_RBUTTONUP = 5

        # EVENT_FLAG_ALTKEY = 32
        # EVENT_FLAG_CTRLKEY = 8
        # EVENT_FLAG_LBUTTON = 1
        # EVENT_FLAG_MBUTTON = 4
        # EVENT_FLAG_RBUTTON = 2
        # EVENT_FLAG_SHIFTKEY = 16

        cvevent = 0
        flag = 0
        if is_motion:
            cvevent = cv2.EVENT_MOUSEMOVE
        elif is_buttonpress:
            if is_left:
                cvevent = cv2.EVENT_LBUTTONDOWN
                flag += cv2.EVENT_FLAG_LBUTTON
            elif is_mid:
                cvevent = cv2.EVENT_MBUTTONDOWN
                flag += cv2.EVENT_FLAG_MBUTTON
            elif is_right:
                cvevent = cv2.EVENT_RBUTTONDOWN
                flag += cv2.EVENT_FLAG_RBUTTON
        elif is_buttonrelease:
            if is_left:
                cvevent = cv2.EVENT_LBUTTONUP
            elif is_mid:
                cvevent = cv2.EVENT_MBUTTONUP
            elif is_right:
                cvevent = cv2.EVENT_RBUTTONUP
        elif is_mousewheel:
            cvevent = cv2.EVENT_MOUSEHWHEEL
            flag += int(math.copysign(0x780000, event.delta))  # 7864320

        self.modifier.LEFT_ALT = event.state & ImageViewer.EVENTSTATE.LEFT_ALT > 0
        self.modifier.CONTROL = event.state & ImageViewer.EVENTSTATE.CONTROL > 0
        self.modifier.SHIFT = event.state & ImageViewer.EVENTSTATE.SHIFT > 0

        flag += cv2.EVENT_FLAG_ALTKEY if self.modifier.LEFT_ALT else 0
        flag += cv2.EVENT_FLAG_CTRLKEY if self.modifier.CONTROL else 0
        flag += cv2.EVENT_FLAG_SHIFTKEY if self.modifier.SHIFT else 0

        x, y = tm.apply(self.can2img_matrix, (event.x, event.y))
        param = None

        if self.is_mouse_panzoom_enabled.get():
            if is_mousewheel:
                step = 0.2
                boost = 4 if self.modifier.CONTROL else 1
                self.zoom_factor *= 2 ** math.copysign(step * boost, event.delta)
                self.draw()
            else:
                can2img_scale_matrix = tm.identity_matrix()
                # remove translation component to avoid cumulating it
                can2img_scale_matrix[:2, :2] = self.can2img_matrix[:2, :2]
                self.mouse_pan_calculator.on_tk_event(event, can2img_scale_matrix)

        if self.onMouse is not None:
            self.onMouse(cvevent, x, y, flag, param)  # type: ignore

    def on_mouse_pan_drag(self, p0_xy, p1_xy):
        print("ON MOUSE PAN", self.pan_xy)
        self.pan_xy = (
            self.cumulative_pan_xy[0] + p1_xy[0] - p0_xy[0],
            self.cumulative_pan_xy[1] + p1_xy[1] - p0_xy[1],
        )
        self.draw()

    def on_mouse_pan_release(self, p0_xy, p1_xy):
        self.cumulative_pan_xy = self.pan_xy

    def on_mouse_zoom(self):
        pass

    def set_img2can_matrix(self, img2can_matrix: TransformMatrix):
        self.img2can_matrix = img2can_matrix.copy()
        self.can2img_matrix = np.linalg.inv(self.img2can_matrix)

    def createInteractivePoint(
            self,
            point_xy,
            label="",
            on_click: CallbackPoint = None,
            on_drag: CallbackPoint = None,
            on_release: CallbackPoint = None,
            magnet_points: Optional[Point2DList] = None,
    ):
        magnets = None
        if magnet_points is not None:
            magnets = interactive_overlays.Magnets(self.canvas, magnet_points)

        ipoint = interactive_overlays.Point(self.canvas, point_xy, label, on_click, on_drag, on_release, magnets=magnets)
        self.interactive_overlay_instance_list.append(ipoint)

    def createInteractivePolygon(
            self,
            point_xy_list,
            label="",
            on_click: CallbackPolygon = None,
            on_drag: CallbackPolygon = None,
            on_release: CallbackPolygon = None,
            magnet_points: Optional[Point2DList] = None,
    ) -> interactive_overlays.Polygon:
        magnets = None
        if magnet_points is not None:
            magnets = interactive_overlays.Magnets(self.canvas, magnet_points)

        ipolygon = interactive_overlays.Polygon(self.canvas, point_xy_list, label, on_click, on_drag, on_release, magnets=magnets)
        self.interactive_overlay_instance_list.append(ipolygon)
        return ipolygon

    def createInteractiveRectangle(
            self,
            point0_xy,
            point1_xy,
            label="",
            on_click: CallbackRect = None,
            on_drag: CallbackRect = None,
            on_release: CallbackRect = None,
            magnet_points: Optional[Point2DList] = None,
    ):
        magnets = None
        if magnet_points is not None:
            magnets = interactive_overlays.Magnets(self.canvas, magnet_points)

        irectangle = interactive_overlays.Rectangle(self.canvas, point0_xy, point1_xy, label, on_click, on_drag, on_release, magnets=magnets)
        self.interactive_overlay_instance_list.append(irectangle)
        return irectangle

    def draw(self):
        # if zoom_factor is not defined yet, define it
        try:
            self.zoom_factor
        except AttributeError:
            self.set_zoom_fit()
            self.zoom_entry.is_focus = False

        if not self.zoom_entry.is_focus:
            self.zoom_entry.set(f"{int(self.zoom_factor * 100 ** 2) / 100}")

        canh, canw = self.canvas_shape_hw
        imgh, imgw = self.mat.shape[:2]
        img_center_matrix: TransformMatrix = tm.T((imgw / 2, imgh / 2))
        can_center_matrix: TransformMatrix = tm.T((canw / 2, canh / 2))
        print("MY PAN VECTOR", self.pan_xy)
        pan_and_zoom_matrix: TransformMatrix = tm.S((self.zoom_factor, self.zoom_factor)) @ tm.T(self.pan_xy)
        self.set_img2can_matrix(can_center_matrix @ pan_and_zoom_matrix @ np.linalg.inv(img_center_matrix))
        mat = cv2.warpPerspective(self.mat, self.img2can_matrix, dsize=(canh, canw), flags=self.cv2_interpolation)  # type: ignore

        self.imgtk = ImageTk.PhotoImage(image=Image.fromarray(mat))
        self.canvas.create_image(canw // 2, canh // 2, anchor=tk.CENTER, image=self.imgtk)

        for overlay in self.interactive_overlay_instance_list:
            overlay.set_img2can_matrix(self.img2can_matrix)
            overlay.update()

    def set_zoom_fit(self):
        canh, canw = self.canvas_shape_hw
        imgh, imgw = self.mat.shape[:2]
        self.zoom_factor = min(canh / imgh, canw / imgw)

    def set_zoom_fill(self):
        canh, canw = self.canvas_shape_hw
        imgh, imgw = self.mat.shape[:2]
        self.zoom_factor = max(canh / imgh, canw / imgw)

    def on_change_zoom(self, text: str):
        try:
            zoom = float(text)
        except ValueError as e:
            return
        self.zoom_factor = zoom / 100
        self.draw()

    def onclick_zoom_fit(self):
        self.set_zoom_fit()
        self.zoom_entry.is_focus = False
        self.draw()

    def onclick_zoom_fill(self):
        self.set_zoom_fill()
        self.zoom_entry.is_focus = False
        self.draw()

    def onclick_zoom_100(self):
        self.zoom_factor = 1
        self.zoom_entry.is_focus = False
        self.draw()

    def onclick_zoom_home(self):
        self.set_zoom_fit()
        self.pan_xy = (0.0, 0.0)
        self.cumulative_pan_xy = (0.0, 0.0)

        self.zoom_entry.is_focus = False
        self.draw()

    def imshow(self, mat: Image_t, cv2_interpolation: Optional[int] = None):
        self.cv2_interpolation = cv2.INTER_LINEAR if cv2_interpolation is None else cv2_interpolation

        if mat.dtype == float:
            mat = (np.clip(mat, 0, 1) * 255).astype(np.uint8)

        self.mat = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)  # type: ignore

        self.draw()
