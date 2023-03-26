import types
from typing import Any, Tuple
import dataclasses
import enum
import math
import tkinter as tk

import cv2
from PIL import Image, ImageTk


class ImageViewer:
    class BUTTONNUM(enum.Enum):
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
        self.canvas = tk.Canvas(master=master, height=height, width=width, bg="blue")
        self.canvas_shape_hw = (height, width)

        self.imgtk = None
        self.img_shape0_hw: Tuple[int, int]
        self.img_shape1_hw: Tuple[int, int]
        self.zoom_factor: float
        self.onMouse: Any = None
        self.modifier = ImageViewer.Modifier()

    def canvas2img_space(self, can_x, can_y):
        canh, canw = self.canvas_shape_hw
        img0h, img0w = self.img_shape0_hw
        img1h, img1w = self.img_shape1_hw
        corner_y, corner_x = (canh - img1h) / 2, (canw - img1w) / 2

        img_x = (can_x - corner_x) * img0w / img1w
        img_y = (can_y - corner_y) * img0h / img1h

        return int(img_x + 0.5), int(img_y + 0.5)

    def setMouseCallback(self, onMouse, param=None):
        if not isinstance(onMouse, types.FunctionType) and not isinstance(onMouse, types.MethodType):
            raise TypeError(f"onMouse must be a function, got {type(onMouse)} instead")
        if param is not None:
            raise TypeError("param argument of function setMouseCallback is not handled in current version of tk4cv2")

        if self.onMouse is None:
            # <MODIFIER-MODIFIER-TYPE-DETAIL>
            self.canvas.bind("<Motion>", self.on_event)
            self.canvas.bind("<ButtonPress>", self.on_event)
            self.canvas.bind("<ButtonRelease>", self.on_event)
            self.canvas.bind("<MouseWheel>", self.on_event)

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
        assert (is_buttonpress or is_buttonrelease or is_motion or is_mousewheel)

        is_left = event.num == ImageViewer.BUTTONNUM.LEFT
        is_mid = event.num == ImageViewer.BUTTONNUM.MID
        is_right = event.num == ImageViewer.BUTTONNUM.RIGHT

        # cv.EVENT_LBUTTONDBLCLK = 7
        # cv.EVENT_LBUTTONDOWN = 1
        # cv.EVENT_LBUTTONUP = 4
        # cv.EVENT_MBUTTONDBLCLK = 9
        # cv.EVENT_MBUTTONDOWN = 3
        # cv.EVENT_MBUTTONUP = 6
        # cv.EVENT_MOUSEHWHEEL = 11
        # cv.EVENT_MOUSEMOVE = 0
        # cv.EVENT_MOUSEWHEEL = 10
        # cv.EVENT_RBUTTONDBLCLK = 8
        # cv.EVENT_RBUTTONDOWN = 2
        # cv.EVENT_RBUTTONUP = 5

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

        x, y = self.canvas2img_space(event.x, event.y)
        param = None

        self.onMouse(cvevent, x, y, flag, param)

    def pack(self, *args, **kwargs):
        self.canvas.pack(*args, **kwargs)

    def bind(self, *args, **kwargs):
        self.canvas.bind(*args, **kwargs)

    def imshow(self, mat, mode=None):
        mode = "fit" if mode is None else mode

        canh, canw = self.canvas_shape_hw
        imgh, imgw = mat.shape[:2]

        self.zoom_factor = 1
        if mode == "fit":
            self.zoom_factor = min(canh / imgh, canw / imgw)
        elif mode == "fill":
            self.zoom_factor = max(canh / imgh, canw / imgw)

        self.img_shape0_hw = mat.shape[:2]
        mat = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
        mat = cv2.resize(mat, None, fx=self.zoom_factor, fy=self.zoom_factor, interpolation=cv2.INTER_LINEAR)
        self.img_shape1_hw = mat.shape[:2]

        self.imgtk = ImageTk.PhotoImage(image=Image.fromarray(mat))
        self.canvas.create_image(canw // 2, canh // 2, anchor=tk.CENTER, image=self.imgtk)

