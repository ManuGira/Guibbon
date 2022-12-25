import time
import numpy as np
import cv2
import tk4cv2 as tcv2
tcv2.inject(cv2)

def on_trackbar(val):
    print("on_trackbar", val)

def on_mouse_event(event, x, y, flags, param):
    print(event, x, y, flags, param)

def demo_cv():
    img = cv2.imread("images/dog.jpg")

    k = 0
    title = "Demo Tk4Cv2"
    cv2.namedWindow(title)
    cv2.createTrackbar("trackbar_name", title, 0, 10, on_trackbar)
    cv2.setMouseCallback(title, on_mouse_event)
    while True:
        k += 1
        cv2.imshow(title, img*np.uint8(k))
        print(cv2.waitKeyEx(0), end=", ")

def print_hello():
    print("hello")


if __name__ == '__main__':
    demo_cv()
