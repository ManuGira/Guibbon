import time
import enum
import dataclasses
import numpy as np
import cv2
from PIL import Image, ImageTk
import tkinter as tk

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


class ImageViewer():
    def __init__(self, master, height: int, width: int):
        self.height = height
        self.width = width
        self.canvas = tk.Canvas(master=master, height=self.height, width=self.width, bg="blue")
        self.imgtk = None
        self.zoom_factor = None

    def imshow(self, mat, mode=None):
        mode = "fit" if mode is None else mode

        ch, cw = self.height, self.width
        ih, iw = mat.shape[:2]

        self.zoom_factor = 1
        if mode == "fit":
            self.zoom_factor = min(ch/ih, cw/iw)
        elif mode == "fill":
            self.zoom_factor = max(ch/ih, cw/iw)

        mat = cv2.resize(mat, None, fx=self.zoom_factor, fy=self.zoom_factor, interpolation=cv2.INTER_LINEAR)

        self.imgtk = ImageTk.PhotoImage(image=Image.fromarray(mat))
        self.canvas.create_image(cw // 2, ch // 2, anchor=tk.CENTER, image=self.imgtk)

class Tk4Cv2:
    instances = {}
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

    @staticmethod
    def imshow(winname, mat, mode=None):
        return Tk4Cv2.get_instance(winname)._imshow(mat, mode)

    @staticmethod
    def waitKeyEx(delay, track_keypress=True, track_keyrelease=False):
        return Tk4Cv2.get_active_instance()._waitKeyEx(delay, track_keypress, track_keyrelease)

    @staticmethod
    def setMouseCallback(windowName, onMouse, param=None):
        return Tk4Cv2.get_active_instance()._setMouseCallback(onMouse, param=None)

    @staticmethod
    def createButton(text='Button', command=None, winname=None):
        if winname is None:
            return Tk4Cv2.get_active_instance()._createButton(text, command)
        else:
            return Tk4Cv2.get_instance(winname)._createButton(text, command)

    @staticmethod
    def createTrackbar(trackbarName, windowName, value, count, onChange):
        Tk4Cv2.get_instance(windowName)._createTrackbar(trackbarName, value, count, onChange)


    @staticmethod
    def namedWindow(winname):  # TODO: add "flags" argument
        Tk4Cv2.get_instance(winname)

    def __init__(self, winname):
        self.root = tk.Tk()
        self.root.title(winname)

        self.frame = tk.Frame(master=self.root, bg="red")

        # Load an image in the script
        self.img_ratio = 4/4
        self.image_viewer = ImageViewer(self.frame, height=720, width=int(720*self.img_ratio))

        # add dummy image to image_viewer
        img = np.zeros(shape=(100, 100, 3), dtype=np.uint8)
        self._imshow(img)

        self.ctrl_frame = tk.Frame(master=self.frame, width=300, bg="green")

        self.frame.pack()
        self.image_viewer.canvas.pack(side=tk.LEFT)
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
        tk.Button(frame, text=text, command=command).pack(fill=tk.BOTH)
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
        # callback must have params: event, x, y, flags, param
        def on_motion(event):
            x = event.x
            y = event.y
            flags = 0
            param = 0
            onMouse(event, x, y, flags, param)

        # <MODIFIER-MODIFIER-TYPE-DETAIL>
        self.image_viewer.canvas.bind("<Motion>", on_motion)
