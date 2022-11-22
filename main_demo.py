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
    title = "Demo OpenCV HighGUI"
    cv2.namedWindow(title)
    cv2.createTrackbar(trackbar_name, winname, 0, 10, on_trackbar)
    while True:
        k += 1
        cv2.imshow(title, img*np.uint8(k))
        print(cv2.waitKeyEx(0), end=", ")

def print_hello():
    print("hello")

def demo_ic():
    img = cv2.imread("image.jpg")

    k = 0
    title = "Demo Image Controller"
    ic.namedWindow(title)
    ic.createButton("print hello", print_hello)
    ic.createTrackbar("trackbar_name", title, 2, 10, on_trackbar)
    while True:
        k += 1
        ic.imshow(title, img*np.uint8(k))
        print(ic.waitKeyEx(0), end=", ")


if __name__ == '__main__':
    demo_ic()
    # demo_cv()