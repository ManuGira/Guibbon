import dataclasses
from typing import Optional
import numpy as np
import cv2
import tk4cv2 as tcv2

class DemoMVCApp:
    @dataclasses.dataclass
    class Model:
        x: int = 0
        y: int = 0

    @dataclasses.dataclass
    class Result:
        img: Optional[np.ndarray] = None

    def __init__(self, filename):
        self.img = cv2.imread(filename)
        self.winname = "demo app"
        tcv2.namedWindow(self.winname)
        tcv2.createInteractivePoint(self.winname, 100, 100, "point", on_drag=self.on_drag)

        self.model = DemoMVCApp.Model()
        self.result = DemoMVCApp.Result()
        self.is_update_needed: bool = True

    def update(self):
        x = self.model.x
        y = self.model.y

        w, h = self.img.shape[:2]
        gain_b = 2*x/w
        gain_r = 2*y/h
        res = self.img.copy()
        res = res.astype(np.uint16)
        res[:, :, 0:1] = res[:, :, 0:1]*gain_b
        res[:, :, 2:3] = res[:, :, 2:3]*gain_r
        res[res>255] = 255
        res = res.astype(np.uint8)
        self.result.img = res
        self.is_update_needed = False

    def show(self):
        while True:
            if self.is_update_needed:
                self.update()
                tcv2.imshow(self.winname, self.result.img)
                self.is_update_needed = False
            tcv2.waitKeyEx(10)

    def on_drag(self, event):
        self.model.x = event.x
        self.model.y = event.y
        self.is_update_needed = True

if __name__ == '__main__':
    mc = DemoMVCApp("images/dog.jpg")
    mc.show()