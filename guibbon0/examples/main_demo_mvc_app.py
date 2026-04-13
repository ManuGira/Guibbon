import numpy as np
import numpy.typing as npt
import cv2
import guibbon as gbn
import tkinter as tk

Image_t = npt.NDArray[np.uint8]


class MyCustomWidget(gbn.WidgetInterface):
    def __init__(self, master: tk.Frame, text: str, on_click_no, on_clik_yes):
        tk.Label(master, text=text).pack(padx=2, side=tk.TOP)

        frame = tk.Frame(master)
        tk.Button(frame, text="No", command=on_click_no).pack(side=tk.LEFT)
        tk.Button(frame, text="Yes", command=on_clik_yes).pack(side=tk.LEFT)
        frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.BOTH)


class DemoMVCApp:
    def __init__(self, filename):
        img = cv2.imread(filename)
        if img is None:
            raise FileNotFoundError(f"Image file not found: {filename}")
        self.img: Image_t = img.astype(np.uint8)
        self.winname = "demo app"
        gbn.namedWindow(self.winname)
        gbn.createInteractivePoint(self.winname, (100, 100), "point", on_drag=self.on_drag)

        slider = gbn.create_slider(self.winname, "slider", [0, 10, 20, 30], lambda index, val: print("slider", index, val), 2)
        my_widget = gbn.create_custom_widget(self.winname, MyCustomWidget, "Are you all right?", lambda: print("no"), lambda: print("yes"))
        print(my_widget)
        slider.set_position(1)

        gbn.createTrackbar("trackbar", self.winname, 2, 4, lambda val: print("trackbar", val))
        gbn.setTrackbarPos("trackbar", self.winname, 1)
        gbn.setTrackbarPos("trackbar", self.winname, 2)

        gbn.create_button(self.winname, "+2", self.add2)

        self.x = 0
        self.y = 0

        self.res: Image_t
        self.is_update_needed: bool = True

    def update(self):
        w, h = self.img.shape[:2]
        x = self.x / w
        y = self.y / h
        gain_b = max(0.5, min(2.0, 1.5 * x + 0.5))
        gain_r = max(0.5, min(2.0, 1.5 * y + 0.5))

        res = self.img.copy()
        res = res.astype(np.uint16)
        res[:, :, 0:1] = res[:, :, 0:1] * gain_b
        res[:, :, 2:3] = res[:, :, 2:3] * gain_r
        res[res > 255] = 255
        res = res.astype(np.uint8)
        self.res = res
        self.is_update_needed = False

    def show(self):
        while True:
            if self.is_update_needed:
                self.update()
                gbn.imshow(self.winname, self.res)
                self.is_update_needed = False
            gbn.waitKeyEx(20)

    def on_drag(self, event):
        self.x = event.x
        self.y = event.y
        self.is_update_needed = True

    def add2(self):
        slider = gbn.get_slider_instance(self.winname, "slider")
        slider.set_values(slider.get_values() + [100])

        gbn.setTrackbarMin("trackbar", self.winname, 2)


if __name__ == "__main__":
    mc = DemoMVCApp("ressources/dog.jpg")
    mc.show()
