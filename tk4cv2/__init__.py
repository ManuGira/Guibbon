from typing import Dict, Optional, Type
from .typedef import CallbackPoint, CallbackPolygon, CallbackRect, Point2DList, InteractivePolygon

import time

import tkinter as tk
from tkinter.colorchooser import askcolor

import numpy as np
import cv2

from .image_viewer import ImageViewer
from .keyboard_event_handler import KeyboardEventHandler
from .widgets.slider_widget import SliderWidget
from .widgets.radio_button_widget import RadioButtonWidget
from .widgets.button_widget import ButtonWidget
from .widgets.widget import WidgetInterface
from .colors import COLORS

__version__ = "0.0.0"
__version_info__ = tuple(int(i) for i in __version__.split(".") if i.isdigit())


def inject(cv2_package):
    cv2_package.createTrackbar = createTrackbar
    cv2_package.destroyAllWindows = not_implemented_error
    cv2_package.destroyWindow = not_implemented_error
    cv2_package.getMouseWheelDelta = not_implemented_error
    cv2_package.getTrackbarPos = getTrackbarPos
    cv2_package.getWindowImageRect = not_implemented_error
    cv2_package.getWindowProperty = getWindowProperty
    cv2_package.imshow = imshow
    cv2_package.moveWindow = not_implemented_error
    cv2_package.namedWindow = namedWindow
    cv2_package.pollKey = not_implemented_error
    cv2_package.resizeWindow = not_implemented_error
    cv2_package.selectROI = not_implemented_error
    cv2_package.selectROIs = not_implemented_error
    cv2_package.setMouseCallback = setMouseCallback
    cv2_package.setTrackbarMax = setTrackbarMax
    cv2_package.setTrackbarMin = setTrackbarMin
    cv2_package.setTrackbarPos = setTrackbarPos
    cv2_package.setWindowProperty = not_implemented_error
    cv2_package.setWindowTitle = not_implemented_error
    cv2_package.startWindowThread = not_implemented_error
    cv2_package.waitKey = waitKey
    cv2_package.waitKeyEx = waitKeyEx


def not_implemented_error():
    raise NotImplementedError("Function not implemented in current version of Tk4Cv2")


def imshow(winname, mat, mode=None):
    Tk4Cv2.get_instance(winname)._imshow(mat, mode)


def getWindowProperty(winname: str, prop_id: int):
    if not Tk4Cv2.is_instance(winname):
        return 0.0
    return Tk4Cv2.get_instance(winname)._getWindowProperty(prop_id)


def waitKey(delay, track_keypress=True, track_keyrelease=False, SilentWarning=False):
    if not SilentWarning:
        print(
            "WARNING: waitKey function not implemented in Tk4Cv2. The current version is similar to waitKeyEx function. (To suppress this warning, use "
            "SilentWarning=True)"
        )
    return waitKeyEx(delay, track_keypress, track_keyrelease)


def waitKeyEx(delay, track_keypress=True, track_keyrelease=False):
    return Tk4Cv2._waitKeyEx(delay, track_keypress, track_keyrelease)


def setMouseCallback(winname, onMouse, param=None):
    return Tk4Cv2.get_instance(winname)._setMouseCallback(onMouse, param=param)


def create_button(winname, text="Button", command=None):
    return Tk4Cv2.get_instance(winname).create_button(text, command)


def get_button_instance(winname, text):
    return Tk4Cv2.get_instance(winname).get_button_instance(text)


def create_custom_widget(winname, CustomWidgetClass: Type[WidgetInterface], *params) -> WidgetInterface:
    widget_instance = Tk4Cv2.get_instance(winname).create_custom_widget(CustomWidgetClass, *params)
    return widget_instance


def create_slider(winname, slider_name, values, initial_index, on_change=None) -> SliderWidget:
    slider_instance: SliderWidget = Tk4Cv2.get_instance(winname).create_slider(slider_name, values, initial_index, on_change)
    return slider_instance


def get_slider_instance(winname, slider_name) -> SliderWidget:
    slider_instance: SliderWidget = Tk4Cv2.get_instance(winname).get_slider_instance(slider_name)
    return slider_instance


def createTrackbar(trackbarName, windowName, value, count, onChange):
    values = list(range(count + 1))
    initial_index = value

    def on_change(index, val):
        return onChange(val)

    Tk4Cv2.get_instance(windowName).create_slider(trackbarName, values, initial_index, on_change)


def setTrackbarPos(trackbarname, winname, pos):
    trackbar_instance = get_slider_instance(winname, trackbarname)
    trackbar_instance.set_index(pos)


def getTrackbarPos(trackbarname, winname):
    trackbar_instance = get_slider_instance(winname, trackbarname)
    return trackbar_instance.get_index()


def setTrackbarMin(trackbarname, winname, minval):
    trackbar_instance = get_slider_instance(winname, trackbarname)
    current_minval = trackbar_instance.get_values()[0]
    maxval = trackbar_instance.get_values()[-1]
    values = list(range(minval, maxval + 1))
    new_index = max(trackbar_instance.get_index() + current_minval - minval, 0)
    trackbar_instance.set_values(values, new_index)


def getTrackbarMin(trackbarname, winname):
    trackbar_instance = get_slider_instance(winname, trackbarname)
    return trackbar_instance.get_values()[0]


def setTrackbarMax(trackbarname, winname, maxval):
    trackbar_instance = get_slider_instance(winname, trackbarname)
    minval = trackbar_instance.get_values()[0]
    values = list(range(minval, maxval + 1))
    trackbar_instance.set_values(values)


def getTrackbarMax(trackbarname, winname):
    trackbar_instance = get_slider_instance(winname, trackbarname)
    return trackbar_instance.get_values()[-1]


def namedWindow(winname):  # TODO: add "flags" argument
    Tk4Cv2.get_instance(winname)


def create_radio_buttons(winname, name, options, on_change) -> RadioButtonWidget:
    return Tk4Cv2.get_instance(winname).create_radio_buttons(name, options, on_change)


def get_radio_buttons(winname, name):
    return Tk4Cv2.get_instance(winname)._get_radio_buttons_instance(name)


def createCheckbutton(name, windowName=None, value=False, onChange=None):
    Tk4Cv2.get_instance(windowName)._createCheckbutton(name, value, onChange)


def createCheckbuttons(name, options, windowName, values, onChange):
    Tk4Cv2.get_instance(windowName)._createCheckbuttons(name, options, values, onChange)


def createColorPicker(name, windowName, values, onChange):
    Tk4Cv2.get_instance(windowName)._createColorPicker(name, values, onChange)


def createInteractivePoint(
        windowName,
        point_xy,
        label="",
        on_click: CallbackPoint = None,
        on_drag: CallbackPoint = None,
        on_release: CallbackPoint = None,
        magnet_points: Optional[Point2DList] = None,
):
    Tk4Cv2.get_instance(windowName).image_viewer.createInteractivePoint(point_xy, label, on_click, on_drag, on_release, magnet_points)


def createInteractivePolygon(
        windowName,
        point_xy_list,
        label="",
        on_click: CallbackPolygon = None,
        on_drag: CallbackPolygon = None,
        on_release: CallbackPolygon = None,
        magnet_points: Optional[Point2DList] = None,
) -> InteractivePolygon:
    ipolygon: InteractivePolygon
    ipolygon = Tk4Cv2.get_instance(windowName).image_viewer.createInteractivePolygon(point_xy_list, label, on_click, on_drag, on_release, magnet_points)
    return ipolygon


def createInteractiveRectangle(
        windowName,
        point0_xy,
        point1_xy,
        label="",
        on_click: CallbackRect = None,
        on_drag: CallbackRect = None,
        on_release: CallbackRect = None,
        magnet_points: Optional[Point2DList] = None,
) -> InteractivePolygon:
    irect: InteractivePolygon
    irect = Tk4Cv2.get_instance(windowName).image_viewer.createInteractiveRectangle(point0_xy, point1_xy, label, on_click, on_drag, on_release, magnet_points)
    return irect


class Tk4Cv2:
    root: tk.Tk
    is_alive: bool = False
    instances: Dict[str, "Tk4Cv2"] = {}
    active_instance_name: Optional[str]
    is_timeout: bool
    keyboard: KeyboardEventHandler

    @staticmethod
    def init():
        Tk4Cv2.root = tk.Tk()
        Tk4Cv2.is_alive = True
        Tk4Cv2.keyboard = KeyboardEventHandler()
        Tk4Cv2.root.withdraw()
        Tk4Cv2.reset()

    @staticmethod
    def reset():
        Tk4Cv2.is_timeout = False

    @staticmethod
    def on_timeout():
        Tk4Cv2.is_timeout = True

    @staticmethod
    def is_instance(winname: str) -> bool:
        assert isinstance(winname, str)
        return winname in Tk4Cv2.instances.keys()

    @staticmethod
    def get_instance(winname) -> "Tk4Cv2":
        assert isinstance(winname, str)
        if winname not in Tk4Cv2.instances.keys():
            Tk4Cv2.instances[winname] = Tk4Cv2(winname)
        Tk4Cv2.active_instance_name = winname
        return Tk4Cv2.instances[winname]

    @staticmethod
    def get_active_instance() -> "Tk4Cv2":
        return Tk4Cv2.get_instance(Tk4Cv2.active_instance_name)

    @staticmethod
    def _waitKeyEx(delay, track_keypress=True, track_keyrelease=False):
        Tk4Cv2.reset()

        if delay > 0:
            Tk4Cv2.get_active_instance().window.after(delay, Tk4Cv2.on_timeout)  # TODO: make threadsafe

        tic = time.time()
        while True:
            Tk4Cv2.root.update_idletasks()
            Tk4Cv2.root.update()  # root can be destroyed at this line

            if not Tk4Cv2.is_alive:
                return -1

            if track_keypress and Tk4Cv2.keyboard.is_keypress_updated:
                Tk4Cv2.keyboard.is_keypress_updated = False
                return Tk4Cv2.keyboard.last_keypressed
            if track_keyrelease and Tk4Cv2.keyboard.is_keyrelease_updated:
                Tk4Cv2.keyboard.is_keyrelease_updated = False
                return Tk4Cv2.keyboard.last_keyreleased
            if Tk4Cv2.is_timeout:
                return -1

            dt = time.time() - tic
            sleep_time = max(0.0, 1 / 20 - dt)
            time.sleep(sleep_time)
            tic = time.time()

    def __init__(self, winname):
        if not Tk4Cv2.is_alive:
            Tk4Cv2.init()

        # Make master root windows invisible
        self.window = tk.Toplevel(Tk4Cv2.root)  # type: ignore
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)  # add callback when user closes the window
        self.winname = winname
        self.window.title(self.winname)

        self.window.bind("<KeyPress>", Tk4Cv2.keyboard.on_event)
        self.window.bind("<KeyRelease>", Tk4Cv2.keyboard.on_event)

        self.frame = tk.Frame(master=self.window, bg=COLORS.background)

        # Load an image in the script
        self.img_ratio = 4 / 4
        self.image_viewer = ImageViewer(self.frame, height=720, width=int(720 * self.img_ratio))

        # add dummy image to image_viewer
        img = np.zeros(shape=(100, 100, 3), dtype=np.uint8)
        self._imshow(img)

        self.ctrl_frame = tk.Frame(master=self.frame, bg=COLORS.ctrl_panel)
        dummy_canvas = tk.Canvas(master=self.ctrl_frame, height=0, width=300)
        dummy_canvas.pack()

        self.sliders_by_names = {}
        self.custom_widtgets_by_names = {}
        self.radio_buttons_by_names = {}
        self.buttons_by_names = {}

        self.frame.pack()
        self.image_viewer.pack(side=tk.LEFT)
        # self.ctrl_frame.pack_propagate(False)
        self.ctrl_frame.pack(fill=tk.X)

    def on_closing(self):
        print("Destroy Root", self.winname)
        Tk4Cv2.instances.pop(self.winname)
        self.window.destroy()

        if len(Tk4Cv2.instances) == 0:
            print("destroy root master")
            Tk4Cv2.root.destroy()
            Tk4Cv2.is_alive = False
        elif Tk4Cv2.active_instance_name == self.winname:
            Tk4Cv2.active_instance_name = list(Tk4Cv2.instances.keys())[-1]

    def create_button(self, text="Button", command=None):
        tk_frame = tk.Frame(self.ctrl_frame, bg=COLORS.ctrl_panel)
        tk_frame.pack_propagate(True)
        button = ButtonWidget(tk_frame, text, command)
        self.buttons_by_names[text] = button
        tk_frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.BOTH)
        return button

    def get_button_instance(self, text):
        return self.buttons_by_names[text]

    def create_slider(self, slider_name, values, initial_index, onChange):
        tk_frame = tk.Frame(self.ctrl_frame, bg=COLORS.widget)
        slider = SliderWidget(tk_frame, slider_name, values, initial_index, onChange, COLORS.widget)
        self.sliders_by_names[slider_name] = slider
        tk_frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)
        return slider

    def get_slider_instance(self, slider_name):
        return self.sliders_by_names[slider_name]

    def create_custom_widget(self, CustomWidgetClass: Type[WidgetInterface], *params) -> WidgetInterface:
        tk_frame = tk.Frame(self.ctrl_frame, bg=COLORS.widget)
        widget_instance = CustomWidgetClass(tk_frame, *params)
        tk_frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)
        return widget_instance

    def create_radio_buttons(self, name, options, on_change) -> RadioButtonWidget:
        tk_frame = tk.Frame(self.ctrl_frame, bg=COLORS.widget)
        radio_buttons = RadioButtonWidget(tk_frame, name, options, on_change)
        self.radio_buttons_by_names[name] = radio_buttons
        tk_frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)
        return radio_buttons

    def _get_radio_buttons_instance(self, name):
        return self.radio_buttons_by_names[name]

    def _createCheckbutton(self, name, value, onChange):
        frame = tk.Frame(self.ctrl_frame)
        tk.Label(frame, text=name).pack(padx=2, side=tk.LEFT, anchor=tk.W)

        def callback():
            onChange(var.get())

        var = tk.BooleanVar()
        cb = tk.Checkbutton(frame, text="", variable=var, onvalue=True, offvalue=False, command=callback)
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

        canvas = tk.Canvas(frame, bg=COLORS.widget, bd=2, height=10)
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

    def _getWindowProperty(self, prop_id: int):
        """
        TODO: not all flags ar handled
            cv2.WND_PROP_FULLSCREEN:    fullscreen property (can be WINDOW_NORMAL or WINDOW_FULLSCREEN).
            cv2.WND_PROP_AUTOSIZE:      autosize property (can be WINDOW_NORMAL or WINDOW_AUTOSIZE).
            cv2.WND_PROP_ASPECT_RATIO:  window's aspect ration (can be set to WINDOW_FREERATIO or WINDOW_KEEPRATIO).
            cv2.WND_PROP_OPENGL:        opengl support.
            cv2.WND_PROP_VISIBLE:       checks whether the window exists and is visible
            cv2.WND_PROP_TOPMOST:       property to toggle normal window being topmost or not
            cv2.WND_PROP_VSYNC:         enable or disable VSYNC (in OpenGL mode)
        """
        if prop_id == cv2.WND_PROP_VISIBLE:
            return 1.0 if self.window.state() == "normal" else 0.0
        else:
            raise NotImplementedError(
                f"Function getWindowProperty is not fully implemented in current version of Tk4Cv2 and does not support the provided "
                f"flag: prop_id={prop_id}"
            )

    def _setMouseCallback(self, onMouse, param=None):
        self.image_viewer.setMouseCallback(onMouse, param)
