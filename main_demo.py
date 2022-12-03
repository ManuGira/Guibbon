import time
import numpy as np
import cv2
from tk4cv2 import Tk4Cv2 as tcv2
tcv2.inject(cv2)

def on_trackbar(val):
    print("on_trackbar", val)

def on_mouse_event(event, x, y, flags, param):
    print(event, x, y, flags, param)

def demo_cv():
    img = cv2.imread("image.jpg")
    img = cv2.resize(img, dsize=None, fx=0.2, fy=0.2)

    k = 0
    title = "Demo OpenCV HighGUI"
    cv2.namedWindow(title)
    cv2.createTrackbar("trackbar_name", title, 0, 10, on_trackbar)
    cv2.setMouseCallback(title, on_mouse_event)
    while True:
        k += 1
        cv2.imshow(title, img*np.uint8(k))
        print(cv2.waitKeyEx(0), end=", ")

def print_hello():
    print("hello")

def demo_tcv():
    img = cv2.imread("image.jpg")

    k = 0
    title = "Demo Image Controller"
    tcv2.namedWindow(title)
    tcv2.createTrackbar("trackbar_name", title, 2, 10, on_trackbar)
    tcv2.setMouseCallback(title, on_mouse_event)

    tcv2.createButton("print hello", print_hello)
    while True:
        k += 1
        tcv2.imshow(title, img * np.uint8(k))
        print(tcv2.waitKeyEx(0), end=", ")


if __name__ == '__main__':
    # demo_tcv()
    demo_cv()

# move
# 0 32 375 0 None
# l down-up
# 1 175 300 1 None (l-down)
# 4 175 300 0 None (l-up)
# 0 175 300 0 None

# R DOWN-UP
# 2 445 402 2 None
# 5 445 402 0 None
# 0 445 402 0 None

# wheel down - up
# 10 301 327 7864320 None
# 10 301 327 -7864320 None