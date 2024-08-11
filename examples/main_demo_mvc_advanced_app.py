import dataclasses
import numpy as np
import cv2
import guibbon as gbn
from guibbon.typedef import Image_t
import threading

def on_click_treeview(*args):
    print(args)
class DemoMVCAdvApp:
    @dataclasses.dataclass
    class Model:
        x: int = 0
        y: int = 0
        cross_xy = (0, 0)

    @dataclasses.dataclass
    class Result:
        img: Image_t = np.array([])

    def __init__(self, filename):
        self.img: Image_t = cv2.imread(filename).astype(np.uint8)
        self.winname = "demo app"
        self.lock = threading.Lock()
        gbn.namedWindow(self.winname)
        gbn.createInteractivePoint(self.winname, (100, 100), "point", on_drag=self.on_drag, magnet_points=[(200, 220), (30, 30)])

        point_xy_list = [(300, 300), (300, 500), (500, 400), (400, 300)]
        gbn.createInteractivePolygon(self.winname, point_xy_list, "polygon", on_drag=self.on_drag_poly, magnet_points=[(100, 300), (170, 300)])

        point0_xy = (200, 200)
        point1_xy = (300, 250)
        gbn.createInteractiveRectangle(self.winname, point0_xy, point1_xy, "rectangle", on_drag=self.on_drag_rect, magnet_points=[(100, 300), (150, 300)])

        tree = gbn.TreeNode(name="root", value="r")
        tree.set(["branch0"], value="0")
        tree.set(["branch0", "branch00"], value="00")
        tree.set(["branch0", "branch01"], value="01")
        tree.set(["branch1", "branch10"], value="10")
        gbn.create_treeview(self.winname, "TreeView", tree=tree, on_click=on_click_treeview)

        self.model = DemoMVCAdvApp.Model()
        self.result = DemoMVCAdvApp.Result()
        self.is_update_needed: bool = True

    def update(self):
        h, w = self.img.shape[:2]
        with self.lock:
            x = self.model.x / w
            y = self.model.y / h
            cross_x, cross_y = self.model.cross_xy

        gain_b = max(0.5, min(2.0, 1.5 * x + 0.5))
        gain_r = max(0.5, min(2.0, 1.5 * y + 0.5))

        res = self.img.copy()
        res = res.astype(np.uint16)
        res[:, :, 0:1] = res[:, :, 0:1] * gain_b
        res[:, :, 2:3] = res[:, :, 2:3] * gain_r
        res[res > 255] = 255

        res[int(round(cross_y)), :, 2] = 255
        res[:, int(round(cross_x)), 2] = 255
        res = res.astype(np.uint8)
        self.result.img = res
        self.is_update_needed = False

    def show(self):
        while True:
            if self.is_update_needed:
                self.update()
                gbn.imshow(self.winname, self.result.img, mode=gbn.MODE.FIT)
                self.is_update_needed = False
            gbn.waitKeyEx(10)

    def on_drag(self, event):
        print(f"user.on_drag: ({event.x}, {event.y})")
        with self.lock:
            self.model.x = event.x
            self.model.y = event.y
            self.model.cross_xy = (event.x, event.y)
            # print(event.x, event.y)
            self.is_update_needed = True

    def on_drag_poly(self, event, point_xy_list):
        # print(point_xy_list)
        with self.lock:
            self.point_xy_list = point_xy_list + []
            self.model.cross_xy = (event.x, event.y)
            self.is_update_needed = True

    def on_drag_rect(self, event, point0_xy, point1_xy):
        print(point0_xy, point1_xy)
        with self.lock:
            self.rect_p0_xy = point0_xy
            self.rect_p1_xy = point1_xy
            self.model.cross_xy = (event.x, event.y)
            self.is_update_needed = True


if __name__ == "__main__":
    mc = DemoMVCAdvApp("ressources/dog.jpg")
    mc.show()
