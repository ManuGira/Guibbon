# type: ignore

import cv2
import guibbon as gbn
import numpy as np
from typing import Any


def rotate(img, theta_rad=0):
    """rotate an image by the given angle."""

    rotation_matrix = cv2.getRotationMatrix2D(
        angle=np.degrees(-theta_rad),
        center=(img.shape[1] // 2, img.shape[0] // 2),
        scale=1.0,
    )
    height, width = img.shape[:2]
    res = cv2.warpAffine(img, rotation_matrix, (width, height))

    return res.astype(np.uint8)


class SliderDemoOldAPI():
    def __init__(self):
        self.img = cv2.imread("ressources/dog.jpg")
        self.res = self.img.copy()

        self.winname = "Demo Guibbon Old API"
        gbn.namedWindow(self.winname)

        slider_values = [f"{val:.2f}" for val in np.linspace(-np.pi, np.pi, 101)]
        slider: gbn.SliderWidget = gbn.create_slider(
            self.winname,
            "slider",
            slider_values,
            initial_index=len(slider_values) // 2,
            on_change=self.on_change_slider,
        )


    def start(self):
        while gbn.Guibbon.is_instance(self.winname):  # cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) > 0.5:
            gbn.imshow(self.winname, self.res, mode=gbn.MODE.P100)
            gbn.waitKeyEx(1)

    def on_change_slider(self, position:int, value:Any):
        self.res = rotate(self.img, float(value))

class SliderDemo():
    def __init__(self):
        self.img = cv2.imread("ressources/dog.jpg")
        self.res = self.img.copy()
        self.gbn_window: gbn.Guibbon = gbn.create_window("Demo Guibbon New API")

        slider_values = [f"{val:.2f}" for val in np.linspace(-np.pi, np.pi, 101)]
        slider = gbn.SliderWidget(
            "slider",
            slider_values,
            initial_position=len(slider_values) // 2,
            on_change=self.on_change_slider,
        )
        self.gbn_window.add(slider)

    def start(self):
        while self.gbn_window:
            self.gbn_window.imshow(self.res, mode=gbn.MODE.P100)
            gbn.waitKeyEx(1)

    def on_change_slider(self, position:int, value:Any):
        self.res = rotate(self.img, float(value))


def main():
    # SliderDemoOldAPI().start()
    SliderDemo().start()


if __name__ == "__main__":
    main()
