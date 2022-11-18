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



class ImageController():
    instances = {}
    active_instance_name = None

    @staticmethod
    def get_instance(winname):
        assert(isinstance(winname, str))
        if winname not in ImageController.instances.keys():
            ImageController.instances[winname] = ImageController(winname)
        ImageController.active_instance_name = winname
        return ImageController.instances[winname]

    @staticmethod
    def get_active_instance():
        return ImageController.get_instance(ImageController.active_instance_name)

    @staticmethod
    def imshow(winname, image):
        return ImageController.get_instance(winname)._imshow(image)

    @staticmethod
    def waitKeyEx(delay, track_keypress=True, track_keyrelease=False):
        # self.frame.master = win
        return ImageController.get_active_instance()._waitKeyEx(delay, track_keypress, track_keyrelease)

    def __init__(self, winname):
        self.root = tk.Tk()
        self.root.title(winname)

        self.frame = tk.Frame(master=self.root, bg="red")

        # Load an image in the script
        self.img_ratio = 4/4
        self.canvas_shape_hw = [720, int(720*self.img_ratio)]
        self.canvas = tk.Canvas(master=self.frame, height=self.canvas_shape_hw[0], width=self.canvas_shape_hw[1], bg="blue")
        self.imgtk = None
        self.zoom_factor = None
        img = np.zeros(shape=(100, 100, 3), dtype=np.uint8)
        self._imshow(img)

        self.ctrl_frame = tk.Frame(master=self.frame, bg="green")

        self.frame.pack()
        self.canvas.pack(side=tk.LEFT)
        self.ctrl_frame.pack()

        self.keyboard = KeyboardEventHandler()
        self.reset()

    def reset(self):
        # TODO: make threadsafe
        self.is_timeout = False

    def _addbutton(self, text='Button', command=None):
        tk.Button(self.ctrl_frame, text=text, command=command).pack(padx=10, pady=10, )

    def _imshow(self, img, mode="fit"):
        ch, cw = self.canvas_shape_hw[:2]
        ih, iw = img.shape[:2]
        if mode == "fit":
            self.zoom_factor = min(ch/ih, cw/iw)
        elif mode == "fill":
            self.zoom_factor = max(ch/ih, cw/iw)

        img = cv2.resize(img, None, fx=self.zoom_factor, fy=self.zoom_factor, interpolation=cv2.INTER_LINEAR)

        self.imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
        self.canvas.create_image(self.canvas_shape_hw[1] // 2, self.canvas_shape_hw[0] // 2, anchor=tk.CENTER,
                                 image=self.imgtk)


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
        # TODO: support ctrl, maj, alt etc...
        self.reset()

        # TODO: mimic cv2.waitLeyEx behavior
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
