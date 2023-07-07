
import dataclasses
import numpy as np
import cv2
import tk4cv2 as tcv2
from tk4cv2.typedef import Image_t

class DemoMVCAdvApp:
    @dataclasses.dataclass
    class Model:
        x: int = 0
        y: int = 0

    @dataclasses.dataclass
    class Result:
        img: Image_t = None

    def __init__(self, filename):
        self.img = cv2.imread(filename)
        self.winname = "demo app"
        tcv2.namedWindow(self.winname)
        tcv2.createInteractivePoint(self.winname, (100, 100), "point", on_drag=self.on_drag)

        point_xy_list  = [(300, 300), (300, 500), (500, 400), (400, 300)]
        tcv2.createInteractivePolygon(self.winname, point_xy_list, "polygon", on_drag=self.on_drag_poly)

        point0_xy  = (200, 200)
        point1_xy  = (300, 250)
        tcv2.createInteractiveRectangle(self.winname, point0_xy, point1_xy, "rectangle", on_drag=self.on_drag_rect)

        self.model = DemoMVCAdvApp.Model()
        self.result = DemoMVCAdvApp.Result()
        self.is_update_needed: bool = True

    def update(self):
        h, w = self.img.shape[:2]
        x = self.model.x/w
        y = self.model.y/h
        gain_b = max(0.5, min(2.0, 1.5*x + 0.5))
        gain_r = max(0.5, min(2.0, 1.5*y + 0.5))

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
        # print(event.x, event.y)
        self.is_update_needed = True

    def on_drag_poly(self, event, point_xy_list):
        # print(point_xy_list)
        self.point_xy_list = point_xy_list + []
        self.is_update_needed = True

    def on_drag_rect(self, event, point0_xy, point1_xy):
        # print(point_xy_list)
        self.rect_p0_xy = point0_xy
        self.rect_p1_xy = point1_xy
        self.is_update_needed = True

if __name__ == '__main__':
    mc = DemoMVCAdvApp("images/dog.jpg")
    mc.show()