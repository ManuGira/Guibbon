# type: ignore

import sys
import cv2
import guibbon as gbn
import numpy as np
from typing import Any

def remap_contrast(img, bound_min=0, bound_max=255):
    """Adjust contrast and brightness of an image."""
    gain = 255.0/(bound_max - bound_min)
    res = (img.astype(float)-bound_min)*gain
    res = np.clip(res, 0, 255).astype(np.uint8)
    return res.astype(np.uint8)


class MiniDemoOldAPI():
    def __init__(self):
        self.img = cv2.imread("ressources/dog.jpg")
        self.res = self.img.copy()

        self.winname = "Demo Guibbon Old API"
        gbn.namedWindow(self.winname)

        multislider_values = range(256)
        multislider: gbn.MultiSliderWidget = gbn.create_multislider(
            self.winname,
            "multi slider",
            multislider_values,
            initial_indexes=[0, 255],
            on_drag=self.on_drag_multislider,
        )

    def start(self):
        while gbn.Guibbon.is_instance(self.winname):  # cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) > 0.5:
            gbn.imshow(self.winname, self.res, mode=gbn.MODE.P100)
            gbn.waitKeyEx(1)

    def on_drag_multislider(self, multislider_state:list[tuple[int, Any]]):
        bound_min = int(multislider_state[0][1])
        bound_max = int(multislider_state[1][1])
        self.res = remap_contrast(self.img, bound_min, bound_max)

class MiniDemoNewAPI():
    def __init__(self):
        self.img = cv2.imread("ressources/dog.jpg")
        self.res = self.img.copy()

        self.gbn_window: gbn.Guibbon = gbn.create_window("Demo Guibbon New API")

        multislider_values = range(256)
        multislider: gbn.MultiSliderWidget = gbn.MultiSliderWidget(
            "multi slider",
            multislider_values,
            initial_indexes=[0, 255],
            on_drag=self.on_drag_multislider,
        )
        self.gbn_window.add(multislider)

    def start(self):
        while self.gbn_window:  # cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) > 0.5:
            self.gbn_window.imshow(self.winname, self.res, mode=gbn.MODE.P100)
            gbn.waitKeyEx(1)

    def on_drag_multislider(self, multislider_state:list[tuple[int, Any]]):
        bound_min = int(multislider_state[0][1])
        bound_max = int(multislider_state[1][1])
        self.res = remap_contrast(self.img, bound_min, bound_max)


def main():
    # MiniDemoOldAPI().start()
    MiniDemoNewAPI().start()

if __name__ == "__main__":
    main()
