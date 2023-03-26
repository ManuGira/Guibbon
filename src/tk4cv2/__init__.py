from typing import Any, Dict
import time
import tkinter as tk
from tkinter.colorchooser import askcolor

import numpy as np
import cv2

from .image_viewer import ImageViewer
from .keyboard_event_handler import KeyboardEventHandler

__version__ = "0.0.0"
__version_info__ = tuple(int(i) for i in __version__.split(".") if i.isdigit())

def inject(cv2_package):
    cv2_package.imshow = imshow
    cv2_package.getWindowProperty = getWindowProperty
    cv2_package.waitKeyEx = waitKeyEx
    cv2_package.setMouseCallback = setMouseCallback
    cv2_package.createTrackbar = createTrackbar
    cv2_package.setTrackbarPos = setTrackbarPos
    cv2_package.getTrackbarPos = getTrackbarPos
    cv2_package.setTrackbarMin = setTrackbarMin
    cv2_package.getTrackbarMin = getTrackbarMin
    cv2_package.setTrackbarMax = setTrackbarMax
    cv2_package.getTrackbarMax = getTrackbarMax
    cv2_package.namedWindow = namedWindow


def imshow(winname, mat, mode=None):
    return Tk4Cv2.get_instance(winname)._imshow(mat, mode)


def getWindowProperty(winname: str, prop_id: int):
    return Tk4Cv2.get_active_instance()._getWindowProperty(prop_id)


def waitKeyEx(delay, track_keypress=True, track_keyrelease=False):
    return Tk4Cv2.get_active_instance()._waitKeyEx(delay, track_keypress, track_keyrelease)


def setMouseCallback(windowName, onMouse, param=None):
    return Tk4Cv2.get_active_instance()._setMouseCallback(onMouse, param=None)


def createButton(text='Button', command=None, winname=None):
    Tk4Cv2.get_instance(winname)._createButton(text, command)


def createTrackbar(trackbarName, windowName=None, value=0, count=10, onChange=None):
    Tk4Cv2.get_instance(windowName)._createTrackbar(trackbarName, value, count, onChange)


def setTrackbarPos(trackbarname, winname, pos):
    Tk4Cv2.get_instance(winname)._setTrackbarPos(trackbarname, pos)


def getTrackbarPos(trackbarname, winname):
    return Tk4Cv2.get_instance(winname)._getTrackbarPos(trackbarname)


def setTrackbarMin(trackbarname, winname, minval):
    Tk4Cv2.get_instance(winname)._setTrackbarMin(trackbarname, minval)


def getTrackbarMin(trackbarname, winname):
    return Tk4Cv2.get_instance(winname)._getTrackbarMin(trackbarname)


def setTrackbarMax(trackbarname, winname, maxval):
    Tk4Cv2.get_instance(winname)._setTrackbarMax(trackbarname, maxval)


def getTrackbarMax(trackbarname, winname):
    return Tk4Cv2.get_instance(winname)._getTrackbarMax(trackbarname)


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
        self.root = tk.Toplevel()
        self.root.master.withdraw()  # Make master root windows invisible
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # add callback when user closes the window
        self.winname = winname
        self.root.title(self.winname)

        self.frame = tk.Frame(master=self.root, bg="red")

        # Load an image in the script
        self.img_ratio = 4 / 4
        self.image_viewer = ImageViewer(self.frame, height=720, width=int(720 * self.img_ratio))

        # add dummy image to image_viewer
        img = np.zeros(shape=(100, 100, 3), dtype=np.uint8)
        self._imshow(img)

        self.ctrl_frame = tk.Frame(master=self.frame, width=300, bg="green")
        self.trackbars_by_names = {}

        self.frame.pack()
        self.image_viewer.pack(side=tk.LEFT)
        # self.ctrl_frame.pack_propagate(False)
        self.ctrl_frame.pack()

        self.keyboard = KeyboardEventHandler()

        self.observers = []  # todo: add trackbar handle and callback to this array. Then, on each loop, we must watch if the values has changed...
        self.reset()

    def on_closing(self):
        print("Destroy Root", self.winname)
        Tk4Cv2.instances.pop(self.winname)
        root_master = self.root.master
        if len(Tk4Cv2.instances) == 0:
            root_master.destroy()
        else:
            self.root.destroy()
            if Tk4Cv2.active_instance_name == self.winname:
                Tk4Cv2.active_instance_name = list(Tk4Cv2.instances.keys())[-1]

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
        self.trackbars_by_names[trackbarName] = trackbar
        frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)

    def _setTrackbarPos(self, trackbarname, pos):
        self.trackbars_by_names[trackbarname].set(pos)

    def _getTrackbarPos(self, trackbarname):
        return self.trackbars_by_names[trackbarname].get()

    def _setTrackbarMin(self, trackbarname, minval):
        self.trackbars_by_names[trackbarname]["from"] = minval

    def _getTrackbarMin(self, trackbarname):
        return self.trackbars_by_names[trackbarname]["from"]

    def _setTrackbarMax(self, trackbarname, maxval):
        self.trackbars_by_names[trackbarname]["to"] = maxval

    def _getTrackbarMax(self, trackbarname):
        return self.trackbars_by_names[trackbarname]["to"]

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

    def _getWindowProperty(self, prop_id: int):
        """
        # TODO: not all flags ar handled
            cv2.WND_PROP_FULLSCREEN:    fullscreen property (can be WINDOW_NORMAL or WINDOW_FULLSCREEN).
            cv2.WND_PROP_AUTOSIZE:      autosize property (can be WINDOW_NORMAL or WINDOW_AUTOSIZE).
            cv2.WND_PROP_ASPECT_RATIO:  window's aspect ration (can be set to WINDOW_FREERATIO or WINDOW_KEEPRATIO).
            cv2.WND_PROP_OPENGL:        opengl support.
            cv2.WND_PROP_VISIBLE:       checks whether the window exists and is visible
            cv2.WND_PROP_TOPMOST:       property to toggle normal window being topmost or not
            cv2.WND_PROP_VSYNC:         enable or disable VSYNC (in OpenGL mode)
        :return:
        """
        if prop_id == cv2.WND_PROP_VISIBLE:
            return 1 if self.root.state() == "normal" else 0
        else:
            raise NotImplementedError

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