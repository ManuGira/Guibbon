import numpy as np
import cv2
import tk4cv2 as tcv2

class DemoApp:
    def __init__(self, filename):
        self.img = cv2.imread(filename)
        self.winname = "demo app"
        tcv2.namedWindow(self.winname)
        tcv2.createInteractivePoint(self.winname, 100, 100, "point", on_drag=self.on_drag)

        self.x = 0
        self.y = 0

        self.res: Optional[np.ndarray] = None
        self.is_update_needed: bool = True

    def update(self):
        w, h = self.img.shape[:2]
        gain_b = 2*self.x/w
        gain_r = 2*self.y/h
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
        print("MyClass.on_drag", event)
        self.x = event.x
        self.y = event.y
        self.is_update_needed = True
        # TODO: demonstrate the problem of having compute() and show() in this function.
        #  (leeds to TkInter callback error (maximum recursion etc)
        #  verify if the same bugs appear with cv2 gui


if __name__ == '__main__':
    mc = DemoApp("images/dog.jpg")
    mc.show()