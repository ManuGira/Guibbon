import time
import cv2
from image_controller import ImageController as ic

def on_trackbar(val):
    print("on_trackbar", val)

def demo_cv():
    img = cv2.imread("image.jpg")
    img = cv2.resize(img, dsize=None, fx=0.2, fy=0.2)
    title = "yep"
    cv2.imshow(title, img)
    cv2.createTrackbar("trackbar name", title, 0, 10, on_trackbar)

    while True:
        print(cv2.waitKeyEx(0))
        print(cv2.waitKey(0))

def print_hello():
    print("hello")

def demo_ic():
    # ic.ImageController("Demo Image Controller")
    # ic.addbutton("yo", print_hello)
    img = cv2.imread("image.jpg")
    # for k in range(1, 10):

    for k in range(10):
        ic.imshow("Demo Image Controller", img*k)
        print(ic.waitKey(0))


if __name__ == '__main__':
    demo_ic()
    # demo_cv()