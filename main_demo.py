import time
import cv2
from image_controller import ImageController as ic
import numpy as np

def on_trackbar(val):
    print("on_trackbar", val)

def demo_cv():
    img = cv2.imread("image.jpg")
    img = cv2.resize(img, dsize=None, fx=0.2, fy=0.2)

    k = 0
    while True:
        k += 1
        cv2.imshow("Demo OpenCV HighGUI", img*np.uint8(k))
        print(cv2.waitKeyEx(0), end=", ")

def print_hello():
    print("hello")

def demo_ic():
    img = cv2.imread("image.jpg")

    k = 0
    while True:
        k += 1
        ic.imshow("Demo Image Controller", img*np.uint8(k))
        print(ic.waitKeyEx(0), end=", ")


if __name__ == '__main__':
    demo_ic()
    # demo_cv()