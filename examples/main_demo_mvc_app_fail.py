from typing import Optional
import numpy as np
import cv2
import tk4cv2 as tcv2

class DemoMVCAppFail:
    """
    This demonstrate a BAD architecture. This is just an example for you to see the difference compared to a correct architecture
    The difference here is that the on_drag callback is calling update() and show()
    TODO: try it with a full cv2 widget (mouse event, or trackbar). And make sure the bug also appear. Otherwise a fix must be done
    """
    def __init__(self, filename):
        self.img = cv2.imread(filename)
        self.winname = "demo app"
        tcv2.namedWindow(self.winname)
        tcv2.createInteractivePoint(self.winname, 100, 100, "point", on_drag=self.on_drag)

        self.x = 0
        self.y = 0

        self.res: Optional[np.ndarray] = None
        self.update()

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

    def show(self):
        tcv2.imshow(self.winname, self.res)
        tcv2.waitKeyEx(0)

    def on_drag(self, event):
        self.x = event.x
        self.y = event.y
        self.update()
        self.show()


if __name__ == '__main__':
    mc = DemoMVCAppFail("images/dog.jpg")
    mc.show()