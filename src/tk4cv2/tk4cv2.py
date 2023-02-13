import types
from typing import Any, Tuple, Dict
import dataclasses
import enum
import time
import math
import tkinter as tk
from tkinter.colorchooser import askcolor

import cv2
import numpy as np
from PIL import Image, ImageTk


class KeyboardEventHandler:
    class KEYCODE(enum.Enum):
        SHIFT = 16
        CTRL = 17
        ALT = 18

    @dataclasses.dataclass()
    class Modifier:
        SHIFT: bool = False
        CTRL: bool = False
        ALT: bool = False

    def __init__(self):
        self.modifier = KeyboardEventHandler.Modifier()
        self.keysdown = set()
        self.last_keypressed = -1
        self.last_keyreleased = -1
        self.is_keypress_updated = False
        self.is_keyrelease_updated = False

        cv_row1 = [   27, 7340032, 7405568, 7471104, 7536640, 7602176, 7667712, 7733248, 7798784, 7864320, 7929856, 7995392, 8060928]
        ic_row1 = [65307,   65470,   65471,   65472,   65473,   65474,   65475,   65476,   65477,   65478,   65479,   65480,   65481]
        cv_row2 = [167, 49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 39, 176, 43, 34, 42, 231, 37, 38, 47, 40, 41, 61, 63,     8]
        ic_row2 = [167, 49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 39, 176, 43, 34, 42, 231, 37, 38, 47, 40, 41, 61, 63, 65288]
        cv_numpad = [2949120, 3014656,    13, 2293760, 2621440, 2228224, 2424832, 2555904, 43, 2359296, 2490368, 2162688, 47, 42, 45]
        ic_numpad = [  65379,   65535, 65293,   65367,   65364,   65366,   65361,   65363, 43,   65360,   65362,   65365, 47, 42, 45]
        cv_tab = [    9]
        ic_tab = [65289]
        cv_spec = [232, 233, 224, 36, 60, 44, 46, 45, 32]
        ic_spec = [232, 233, 224, 36, 60, 44, 46, 45, 32]
        cv_spec_shift = [252,    33, 246, 228, 163, 62, 59, 58, 95]
        ic_spec_shift = [252, 65312, 246, 228, 163, 62, 59, 58, 95]
        cv_spec_altgr = [ 91,    93, 123, 125, 92]
        ic_spec_altgr = [232, 65312, 224,  36, 60]
        self.map_ic2cv = dict(zip(
            ic_row1 + ic_row2 + ic_numpad + ic_tab + ic_spec + ic_spec_shift + ic_spec_altgr,
            cv_row1 + cv_row2 + cv_numpad + cv_tab + cv_spec + cv_spec_shift + cv_spec_altgr
        ))

    def is_modifier_key(self, event):
        return any([event.keycode == kc.value for kc in self.KEYCODE])

    def update_modifier(self, event, is_down):
        if event.keycode == self.KEYCODE.SHIFT.value:
            self.modifier.SHIFT = is_down

        if event.keycode == self.KEYCODE.CTRL.value:
            self.modifier.CTRL = is_down

        if event.keycode == self.KEYCODE.ALT.value:
            self.modifier.ALT = is_down

    def on_event(self, event):
        # def printkey(event, keywords):
        #     print(", ".join([f"{kw}: {event.__getattribute__(kw)}".ljust(5) for kw in keywords]))
        #     print(", ".join([(kw + ": " + str(event.__getattribute__(kw))).ljust(5) for kw in keywords]))
        # printkey(event, "char delta keycode keysym keysym_num num state type".split())

        # The obvious information
        is_keypress = event.type == tk.EventType.KeyPress
        is_keyrelease = event.type == tk.EventType.KeyRelease
        assert(is_keypress or is_keyrelease)

        if self.is_modifier_key(event):
            self.update_modifier(event, is_keypress)
            return

        num = self.map_ic2cv[event.keysym_num] if event.keysym_num in self.map_ic2cv else event.keysym_num

        if num not in self.keysdown and is_keypress:
            self.is_keypress_updated = True
            self.last_keypressed = num
            self.keysdown.add(num)
        elif num in self.keysdown and is_keyrelease:
            self.is_keyrelease_updated = True
            self.last_keyreleased = num
            self.keysdown.remove(num)


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
        if not isinstance(onMouse, types.FunctionType):
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


def inject(cv2_package):
    cv2_package.imshow = imshow
    cv2_package.waitKeyEx = waitKeyEx
    cv2_package.setMouseCallback = setMouseCallback
    cv2_package.createTrackbar = createTrackbar
    cv2_package.namedWindow = namedWindow


def imshow(winname, mat, mode=None):
    return Tk4Cv2.get_instance(winname)._imshow(mat, mode)


def waitKeyEx(delay, track_keypress=True, track_keyrelease=False):
    return Tk4Cv2.get_active_instance()._waitKeyEx(delay, track_keypress, track_keyrelease)


def setMouseCallback(windowName, onMouse, param=None):
    return Tk4Cv2.get_active_instance()._setMouseCallback(onMouse, param=None)


def createButton(text='Button', command=None, winname=None):
    Tk4Cv2.get_instance(winname)._createButton(text, command)


def createTrackbar(trackbarName, windowName=None, value=0, count=10, onChange=None):
    Tk4Cv2.get_instance(windowName)._createTrackbar(trackbarName, value, count, onChange)


def namedWindow(winname):  # TODO: add "flags" argument
    Tk4Cv2.get_instance(winname)


def createRadioButtons(name, options, windowName, value, onChange):
    Tk4Cv2.get_instance(windowName)._createRadioButtons(name, options, value, onChange)


def createCheckbutton(name, windowName=None, value=False, onChange=None):
    Tk4Cv2.get_instance(windowName)._createCheckbutton(name, value, onChange)


def createCheckbuttons(name, options, windowName, values, onChange):
    Tk4Cv2.get_instance(windowName)._createCheckbuttons(name, options, values, onChange)


def createColorPicker(name, windowName, values, onChange):
    Tk4Cv2.get_instance(windowName)._createColorPicker(name, values, onChange)


class Tk4Cv2:
    instances: Dict[str, Any] = {}
    active_instance_name = None

    @staticmethod
    def get_instance(winname):
        assert(isinstance(winname, str))
        if winname not in Tk4Cv2.instances.keys():
            Tk4Cv2.instances[winname] = Tk4Cv2(winname)
        Tk4Cv2.active_instance_name = winname
        return Tk4Cv2.instances[winname]

    @staticmethod
    def get_active_instance():
        return Tk4Cv2.get_instance(Tk4Cv2.active_instance_name)

    def __init__(self, winname):
        self.root = tk.Tk()
        self.root.title(winname)

        self.frame = tk.Frame(master=self.root, bg="red")

        # Load an image in the script
        self.img_ratio = 4 / 4
        self.image_viewer = ImageViewer(self.frame, height=720, width=int(720 * self.img_ratio))

        # add dummy image to image_viewer
        img = np.zeros(shape=(100, 100, 3), dtype=np.uint8)
        self._imshow(img)

        self.ctrl_frame = tk.Frame(master=self.frame, width=300, bg="green")

        self.frame.pack()
        self.image_viewer.pack(side=tk.LEFT)
        # self.ctrl_frame.pack_propagate(False)
        self.ctrl_frame.pack()

        self.keyboard = KeyboardEventHandler()

        self.observers = []  # todo: add trackbar handle and callback to this array. Then, on each loop, we must watch if the values has changed...
        self.reset()

    def reset(self):
        # TODO: make threadsafe
        self.is_timeout = False

    def _createButton(self, text='Button', command=None):
        frame = tk.Frame(self.ctrl_frame, bg="yellow")
        frame.pack_propagate(True)

        tk.Button(frame, text=text, command=command).pack(side=tk.LEFT)
        frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.BOTH)

    def _createTrackbar(self, trackbarName, value, count, onChange):
        frame = tk.Frame(self.ctrl_frame)
        tk.Label(frame, text=trackbarName).pack(padx=2, side=tk.LEFT)
        # tk.Button(frame, text=f"{value} {count}", command=onChange).pack(padx=2, fill=tk.X, expand=1)
        trackbar = tk.Scale(frame, from_=0, to=count, orient=tk.HORIZONTAL)
        trackbar.set(value)
        trackbar["command"] = onChange
        trackbar.pack(padx=2, fill=tk.X, expand=1)
        frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)

        # self.observers.append(ObjectObserver(getter, on_change, is_equal))

    def _createRadioButtons(self, name, options, value, onChange):
        frame = tk.Frame(self.ctrl_frame)
        tk.Label(frame, text=name).pack(padx=2, side=tk.TOP, anchor=tk.W)
        radioframeborder = tk.Frame(frame, bg="grey")
        borderwidth = 1
        radioframe = tk.Frame(radioframeborder)

        def callback():
            i = var.get()
            opt = options[i]
            onChange(i, opt)

        var = tk.IntVar()
        for i, opt in enumerate(options):
            rb = tk.Radiobutton(radioframe, text=str(opt), variable=var, value=i, command=callback)
            if i == value:
                rb.select()
                onChange(i, opt)
            rb.pack(side=tk.TOP, anchor=tk.W)

        radioframe.pack(padx=borderwidth, pady=borderwidth, side=tk.TOP, fill=tk.X)
        radioframeborder.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X)
        frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)

    def _createCheckbutton(self, name, value, onChange):
        frame = tk.Frame(self.ctrl_frame)
        tk.Label(frame, text=name).pack(padx=2, side=tk.LEFT, anchor=tk.W)

        def callback():
            onChange(var.get())

        var = tk.BooleanVar()
        cb = tk.Checkbutton(frame, text="", variable=var, onvalue=True, offvalue=False,
                            command=callback)
        if value:
            cb.select()
        cb.pack(side=tk.TOP, anchor=tk.W)
        frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)

    def _createCheckbuttons(self, name, options, values, onChange):
        frame = tk.Frame(self.ctrl_frame)
        tk.Label(frame, text=name).pack(padx=2, side=tk.TOP, anchor=tk.W)
        checkframeborder = tk.Frame(frame, bg="grey")
        borderwidth = 1
        checkframe = tk.Frame(checkframeborder)

        vars = [tk.BooleanVar() for opt in options]

        def callback():
            res = [var.get() for var in vars]
            onChange(res)

        for i, opt in enumerate(options):
            checkvar = vars[i]
            cb = tk.Checkbutton(checkframe, text=str(opt), variable=checkvar, onvalue=True, offvalue=False, command=callback)
            if values[i]:
                cb.select()
            cb.pack(side=tk.TOP, anchor=tk.W)

        checkframe.pack(padx=borderwidth, pady=borderwidth, side=tk.TOP, fill=tk.X)
        checkframeborder.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X)
        frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)

    def _createColorPicker(self, name, values, onChange):
        frame = tk.Frame(self.ctrl_frame)
        label = tk.Label(frame, text=name)
        label.pack(padx=2, side=tk.LEFT, anchor=tk.W)

        def callback_canvas_click(event):
            colors = askcolor(title="Tkinter Color Chooser")
            canvas["bg"] = colors[1]
            onChange(colors)

        canvas = tk.Canvas(frame, bg="yellow", bd=2, height=10)
        canvas.bind("<Button-1>", callback_canvas_click)

        canvas.pack(side=tk.LEFT, anchor=tk.W)
        frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)

    def _imshow(self, mat, mode=None):
        self.image_viewer.imshow(mat, mode)

    # def keydown(self, event):
    #     def printkey(event, keywords):
    #         print(", ".join([f"{kw}: {event.__getattribute__(kw)}".ljust(5) for kw in keywords]))
    #
    #     printkey(event, "char delta keycode keysym keysym_num num state type".split())
    #     self.is_keypressed = True
    #     self.keypressed = event.keycode  # TODO: make threadsafe

    def on_timeout(self):
        self.is_timeout = True

    def _waitKeyEx(self, delay, track_keypress=True, track_keyrelease=False):
        self.reset()

        self.root.bind("<KeyPress>", self.keyboard.on_event)
        self.root.bind("<KeyRelease>", self.keyboard.on_event)

        if delay > 0:
            self.root.after(delay, self.on_timeout)  # TODO: make threadsafe

        while True:
            self.root.update()
            self.root.update_idletasks()
            if track_keypress and self.keyboard.is_keypress_updated:
                self.keyboard.is_keypress_updated = False
                return self.keyboard.last_keypressed
            if track_keyrelease and self.keyboard.is_keyrelease_updated:
                self.keyboard.is_keyrelease_updated = False
                return self.keyboard.last_keyreleased
            if self.is_timeout:
                return -1

            time.sleep(0.01)

    def _setMouseCallback(self, onMouse, param=None):
        self.image_viewer.setMouseCallback(onMouse, param)
