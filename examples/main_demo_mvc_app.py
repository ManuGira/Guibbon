from typing import Optional
import numpy as np
import numpy.typing as npt
import cv2
import tk4cv2 as tcv2

Image_t = Optional[npt.NDArray[np.uint8]]

class DemoMVCApp:
    def __init__(self, filename):
        self.img = cv2.imread(filename)
        self.winname = "demo app"
        tcv2.namedWindow(self.winname)
        tcv2.createInteractivePoint(self.winname, (100, 100), "point", on_drag=self.on_drag)

        slider = tcv2.create_slider(self.winname, "slider", [0, 10, 20, 30], 2, lambda index, val: print("slider", index, val))
        slider.set_index(1)

        tcv2.createTrackbar("trackbar", self.winname, 2, 4, lambda val: print("trackbar", val))
        tcv2.setTrackbarPos("trackbar", self.winname, 1)
        tcv2.setTrackbarPos("trackbar", self.winname, 2)

        tcv2.createButton("+2", self.add2, self.winname)

        self.x = 0
        self.y = 0

        self.res: Image_t = None
        self.is_update_needed: bool = True

    def update(self):
        w, h = self.img.shape[:2]
        x = self.x / w
        y = self.y / h
        gain_b = max(0.5, min(2.0, 1.5 * x + 0.5))
        gain_r = max(0.5, min(2.0, 1.5 * y + 0.5))

        res = self.img.copy()
        res = res.astype(np.uint16)
        res[:, :, 0:1] = res[:, :, 0:1]*gain_b
        res[:, :, 2:3] = res[:, :, 2:3]*gain_r
        res[res>255] = 255
        res = res.astype(np.uint8)
        self.res = res
        self.is_update_needed = False

    def show(self):
        while True:
            if self.is_update_needed:
                self.update()
                tcv2.imshow(self.winname, self.res)
                self.is_update_needed = False
            tcv2.waitKeyEx(20)

    def on_drag(self, event):
        self.x = event.x
        self.y = event.y
        self.is_update_needed = True

    def add2(self):
        slider = tcv2.get_slider_instance(self.winname, "slider")
        slider.set_values(slider.get_values() + [100])

        tcv2.setTrackbarMin("trackbar", self.winname, 2)

if __name__ == '__main__':
    mc = DemoMVCApp("images/dog.jpg")
    mc.show()