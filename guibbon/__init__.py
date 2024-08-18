import os
import re
import time
import tkinter as tk
from typing import Dict, Optional, Type, List, Sequence, Any, Tuple

import cv2

from .colors import COLORS
from .image_viewer import ImageViewer, MODE
from .keyboard_event_handler import KeyboardEventHandler
from .typedef import Image_t, CallbackPoint, CallbackPolygon, CallbackRect, Point2DList, InteractivePolygon, CallbackMouse
from .widgets.button_widget import ButtonWidget, CallbackButton
from .widgets.check_button_list_widget import CheckButtonListWidget, CallbackCheckButtonList
from .widgets.check_button_widget import CheckButtonWidget, CallbackCheckButton
from .widgets.color_picker_widget import ColorPickerWidget, CallbackColorPicker
from .widgets.radio_buttons_widget import RadioButtonsWidget, CallbackRadioButtons
from .widgets.slider_widget import SliderWidget, CallbackSlider
from .widgets.treeview_widget import TreeviewWidget, CallbackTreeview, TreeNode
from .widgets.widget import WidgetInterface

__version__ = "0.3.0"


def compute_version_info():
    mtch = re.match(r"(\d+).(\d+).(\d+)((-dev)?)$", __version__)

    if mtch is None:
        return [(0, 0, 0), ""]

    major = mtch.group(1)
    minor = mtch.group(2)
    build_nb = mtch.group(3)

    lastindex: int = 0 if mtch.lastindex is None else mtch.lastindex
    mode = "dev" if "dev" in mtch.group(lastindex) else None

    return [(major, minor, build_nb), mode]


__version_info__ = compute_version_info()


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
    raise NotImplementedError("Function not implemented in current version of Guibbon")


def imshow(winname: str, mat: Image_t, mode: MODE = MODE.FIT, cv2_interpolation: Optional[int] = None):
    Guibbon.get_instance(winname).imshow(mat, mode, cv2_interpolation)


def getWindowProperty(winname: str, prop_id: int) -> float:
    if not Guibbon.is_instance(winname):
        return 0.0
    return Guibbon.get_instance(winname).getWindowProperty(prop_id)


def waitKey(delay: int, track_keypress=True, track_keyrelease=False, SilentWarning=False) -> int:
    if not SilentWarning:
        print(
            "WARNING: waitKey function not implemented in Guibbon. The current version is similar to waitKeyEx function. (To suppress this warning, use "
            "SilentWarning=True)"
        )
    return waitKeyEx(delay, track_keypress, track_keyrelease)


def waitKeyEx(delay: int, track_keypress=True, track_keyrelease=False) -> int:
    return Guibbon.waitKeyEx(delay, track_keypress, track_keyrelease)


def setMouseCallback(winname: str, onMouse: CallbackMouse, userdata=None):
    Guibbon.get_instance(winname).setMouseCallback(onMouse, userdata=userdata)


def create_button(winname, text: str, on_click: CallbackButton) -> ButtonWidget:
    return Guibbon.get_instance(winname).create_button(text, on_click)


def get_button_instance(winname: str, text: str) -> ButtonWidget:
    return Guibbon.get_instance(winname).get_button_instance(text)


def create_custom_widget(winname, CustomWidgetClass: Type[WidgetInterface], *params) -> WidgetInterface:
    widget_instance = Guibbon.get_instance(winname).create_custom_widget(CustomWidgetClass, *params)
    return widget_instance


def create_slider(winname: str, slider_name: str, values: Sequence[Any], on_change: CallbackSlider, initial_index: int = 0) -> SliderWidget:
    slider_instance: SliderWidget = Guibbon.get_instance(winname).create_slider(slider_name, values, on_change, initial_index)
    return slider_instance


def get_slider_instance(winname: str, slider_name: str) -> SliderWidget:
    slider_instance: SliderWidget = Guibbon.get_instance(winname).get_slider_instance(slider_name)
    return slider_instance


def createTrackbar(trackbarName, windowName, value, count, onChange):
    """
    Same trackbar as in opencv. However, for a more pythonic signature, you may want to use create_slider(...) instead
    """
    values = list(range(count + 1))
    initial_index = value

    def on_change(index, val):
        return onChange(val)

    Guibbon.get_instance(windowName).create_slider(trackbarName, values, on_change, initial_index)


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


def namedWindow(winname):
    Guibbon.get_instance(winname)


def create_window(winname: str) -> "Guibbon":
    return Guibbon.get_instance(winname)


def create_radio_buttons(winname: str, name: str, options: List[str], on_change: CallbackRadioButtons) -> RadioButtonsWidget:
    return Guibbon.get_instance(winname).create_radio_buttons(name, options, on_change)


def get_radio_buttons(winname: str, name: str) -> RadioButtonsWidget:
    return Guibbon.get_instance(winname).get_radio_buttons_instance(name)


def create_check_button(winname: str, name: str, on_change: CallbackCheckButton, initial_value: bool = False) -> CheckButtonWidget:
    return Guibbon.get_instance(winname).create_check_button(name, on_change, initial_value)


def create_check_button_list(winname: str, name: str, options: List[str], on_change: CallbackCheckButtonList, initial_values: Optional[List[bool]] = None) -> CheckButtonListWidget:
    return Guibbon.get_instance(winname).create_check_button_list(name, options, on_change, initial_values)


def create_color_picker(winname: str, name: str, on_change: CallbackColorPicker, initial_color_rgb: Optional[Tuple[int, int, int]] = None) -> ColorPickerWidget:
    return Guibbon.get_instance(winname).create_color_picker(name, on_change, initial_color_rgb)


def create_treeview(winname: str, name: str, tree: TreeNode, on_click: CallbackTreeview) -> TreeviewWidget:
    return Guibbon.get_instance(winname).create_treeview(name, tree, on_click)


def createInteractivePoint(
        windowName,
        point_xy,
        label="",
        on_click: CallbackPoint = None,
        on_drag: CallbackPoint = None,
        on_release: CallbackPoint = None,
        magnet_points: Optional[Point2DList] = None,
):
    Guibbon.get_instance(windowName).image_viewer.createInteractivePoint(point_xy, label, on_click, on_drag, on_release, magnet_points)


def createInteractivePolygon(
        windowName,
        point_xy_list,
        label="",
        on_click: CallbackPolygon = None,
        on_drag: CallbackPolygon = None,
        on_release: CallbackPolygon = None,
        magnet_points: Optional[Point2DList] = None,
) -> InteractivePolygon:
    """
    Draws a polygon over the displayed image. The corners of the polygon can be dragged by the user, triggering a callback.
    """
    ipolygon: InteractivePolygon
    ipolygon = Guibbon.get_instance(windowName).image_viewer.createInteractivePolygon(point_xy_list, label, on_click, on_drag, on_release, magnet_points)
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
    """Create and returns object of type createInteractiveRectangle windows named windowName."""
    irect: InteractivePolygon
    irect = Guibbon.get_instance(windowName).image_viewer.createInteractiveRectangle(point0_xy, point1_xy, label, on_click, on_drag, on_release, magnet_points)
    return irect


class Guibbon:
    """The Guibbon object contains the list of open windows"""

    root: tk.Tk
    is_alive: bool = False
    instances: Dict[str, "Guibbon"] = {}
    active_instance_name: Optional[str]
    is_timeout: bool
    keyboard: KeyboardEventHandler

    @staticmethod
    def init():
        Guibbon.root = tk.Tk()
        Guibbon.is_alive = True
        Guibbon.keyboard = KeyboardEventHandler()
        Guibbon.root.withdraw()
        Guibbon.reset()

    @staticmethod
    def reset():
        Guibbon.is_timeout = False

    @staticmethod
    def on_timeout():
        Guibbon.is_timeout = True

    @staticmethod
    def is_instance(winname: str) -> bool:
        assert isinstance(winname, str)
        return winname in Guibbon.instances.keys()

    @staticmethod
    def get_instance(winname) -> "Guibbon":
        assert isinstance(winname, str)
        if winname not in Guibbon.instances.keys():
            Guibbon.instances[winname] = Guibbon(winname)
        Guibbon.active_instance_name = winname
        return Guibbon.instances[winname]

    @staticmethod
    def get_active_instance() -> "Guibbon":
        return Guibbon.get_instance(Guibbon.active_instance_name)

    @staticmethod
    def waitKeyEx(delay, track_keypress=True, track_keyrelease=False) -> int:
        Guibbon.reset()

        if delay > 0:
            Guibbon.get_active_instance().window.after(delay, Guibbon.on_timeout)  # TODO: make threadsafe

        tic = time.time()
        while True:
            Guibbon.root.update_idletasks()
            Guibbon.root.update()  # root can be destroyed at this line

            if not Guibbon.is_alive:
                return -1

            if track_keypress and Guibbon.keyboard.is_keypress_updated:
                Guibbon.keyboard.is_keypress_updated = False
                return Guibbon.keyboard.last_keypressed
            if track_keyrelease and Guibbon.keyboard.is_keyrelease_updated:
                Guibbon.keyboard.is_keyrelease_updated = False
                return Guibbon.keyboard.last_keyreleased
            if Guibbon.is_timeout:
                return -1

            dt = time.time() - tic
            sleep_time = max(0.0, 1 / 20 - dt)
            time.sleep(sleep_time)
            tic = time.time()

    def __init__(self, winname):
        if not Guibbon.is_alive:
            Guibbon.init()

        # Make master root windows invisible
        self.window = tk.Toplevel(Guibbon.root)  # type: ignore
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)  # add callback when user closes the window
        self.winname = winname
        self.window.title(self.winname)
        icon = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__), "icons", "icon32.png"))
        self.window.iconphoto(False, icon)

        self.window.bind("<KeyPress>", Guibbon.keyboard.on_event)
        self.window.bind("<KeyRelease>", Guibbon.keyboard.on_event)

        self.frame = tk.Frame(master=self.window, bg=COLORS.background)

        # Load an image in the script
        self.img_ratio = 4 / 4
        self.image_viewer = ImageViewer(self.frame, height=720, width=int(720 * self.img_ratio))

        # add dummy image to image_viewer
        # img = np.zeros(shape=(100, 100, 3), dtype=np.uint8)
        # self.imshow(img)

        self.ctrl_frame = tk.Frame(master=self.frame, bg=COLORS.ctrl_panel)
        dummy_canvas = tk.Canvas(master=self.ctrl_frame, height=0, width=300)
        dummy_canvas.pack()

        self.sliders_by_names: Dict[str, SliderWidget] = {}
        self.custom_widtgets_by_names: Dict[str, WidgetInterface] = {}
        self.radio_buttons_by_names: Dict[str, RadioButtonsWidget] = {}
        self.buttons_by_names: Dict[str, ButtonWidget] = {}

        self.frame.pack()
        self.image_viewer.frame.pack(side=tk.LEFT)
        # self.ctrl_frame.pack_propagate(False)
        self.ctrl_frame.pack(fill=tk.X)

    def on_closing(self):
        print("Destroy Root", self.winname)
        Guibbon.instances.pop(self.winname)
        self.window.destroy()

        if len(Guibbon.instances) == 0:
            print("destroy root master")
            Guibbon.root.destroy()
            Guibbon.is_alive = False
        elif Guibbon.active_instance_name == self.winname:
            Guibbon.active_instance_name = list(Guibbon.instances.keys())[-1]

    def create_button(self, text: str, on_click: CallbackButton) -> ButtonWidget:
        tk_frame = tk.Frame(self.ctrl_frame, bg=COLORS.ctrl_panel)
        tk_frame.pack_propagate(True)
        button = ButtonWidget(tk_frame, text, on_click)
        self.buttons_by_names[text] = button
        tk_frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.BOTH)
        return button

    def get_button_instance(self, text: str) -> ButtonWidget:
        return self.buttons_by_names[text]

    def create_slider(self, slider_name: str, values: Sequence[Any], on_change: CallbackSlider, initial_index: int = 0):
        tk_frame = tk.Frame(self.ctrl_frame, bg=COLORS.widget)
        slider = SliderWidget(tk_frame, slider_name, values, initial_index, on_change, COLORS.widget)
        self.sliders_by_names[slider_name] = slider
        tk_frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)
        return slider

    def get_slider_instance(self, slider_name: str):
        return self.sliders_by_names[slider_name]

    def create_custom_widget(self, CustomWidgetClass: Type[WidgetInterface], *params) -> WidgetInterface:
        tk_frame = tk.Frame(self.ctrl_frame, bg=COLORS.widget)
        widget_instance = CustomWidgetClass(tk_frame, *params)
        tk_frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)
        return widget_instance

    def create_radio_buttons(self, name: str, options: List[str], on_change: CallbackRadioButtons) -> RadioButtonsWidget:
        tk_frame = tk.Frame(self.ctrl_frame, bg=COLORS.widget)
        radio_buttons = RadioButtonsWidget(tk_frame, name, options, on_change)
        self.radio_buttons_by_names[name] = radio_buttons
        tk_frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)
        return radio_buttons

    def get_radio_buttons_instance(self, name: str) -> RadioButtonsWidget:
        return self.radio_buttons_by_names[name]

    def create_check_button(self, name: str, on_change: CallbackCheckButton, initial_value: bool = False) -> CheckButtonWidget:
        tk_frame = tk.Frame(self.ctrl_frame, bg=COLORS.widget)
        cb = CheckButtonWidget(tk_frame, name, on_change, initial_value)
        tk_frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)
        return cb

    def create_check_button_list(self, name: str, options: List[str], on_change: CallbackCheckButtonList, initial_values: Optional[List[bool]] = None) -> CheckButtonListWidget:
        tk_frame = tk.Frame(self.ctrl_frame)
        cb = CheckButtonListWidget(tk_frame, name, options, on_change, initial_values)
        tk_frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)
        return cb

    def create_color_picker(self, name: str, on_change: CallbackColorPicker, initial_color_rgb: Optional[Tuple[int, int, int]] = None) -> ColorPickerWidget:
        tk_frame = tk.Frame(self.ctrl_frame)
        cpw = ColorPickerWidget(tk_frame, name, on_change, initial_color_rgb)
        tk_frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)
        return cpw

    def create_treeview(self, name: str, tree: TreeNode, on_click: CallbackTreeview) -> TreeviewWidget:
        tk_frame = tk.Frame(self.ctrl_frame)
        widget = TreeviewWidget(tk_frame, name, tree, on_click)
        tk_frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)
        return widget

    def imshow(self, mat: Image_t, mode: MODE = MODE.FIT, cv2_interpolation: Optional[int] = None):
        self.image_viewer.imshow(mat, mode, cv2_interpolation)

    def getWindowProperty(self, prop_id: int) -> float:
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
                f"Function getWindowProperty is not fully implemented in current version of Guibbon and does not support the provided "
                f"flag: prop_id={prop_id}"
            )

    def setMouseCallback(self, onMouse: CallbackMouse, userdata=None):
        self.image_viewer.setMouseCallback(onMouse, userdata)
