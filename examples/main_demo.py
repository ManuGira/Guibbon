# type: ignore

import sys
import numpy as np
import cv2
import tk4cv2 as tcv2

if 'tk4cv2' in sys.modules:
    tcv2.inject(cv2)


def on_trackbar(val):
    print("on_trackbar", val)


def on_button_click():
    print("on_button_click")


def on_mouse_event(event, x, y, flags, param):
    print(event, x, y, flags, param)


def on_radio_button(i, opt):
    print("on_radio_button", i, opt)


def on_check_buttons(checks):
    print("on_check_buttons", checks)


def on_check_button(check):
    print("on_check_button", check)


def on_color_pick(colors):
    print("on_color_pick", colors)

def on_point_click(event):
    print("on_point_click", event)

def on_point_drag(event):
    print("on_point_drag", event)

def on_point_release(event):
    print("on_point_release", event)

def demo_cv():
    img = cv2.imread("images/dog.jpg")

    k = 0
    winname = "Demo Tk4Cv2"
    cv2.namedWindow(winname)
    cv2.createTrackbar("trackbar_name", winname, 0, 10, on_trackbar)
    cv2.setTrackbarMin("trackbar_name", winname, 2)
    cv2.setTrackbarMax("trackbar_name", winname, 12)
    cv2.setTrackbarPos("trackbar_name", winname, 6)
    cv2.setMouseCallback(winname, on_mouse_event)

    if 'tk4cv2' in sys.modules:
        # type: ignore
        tcv2.createButton("the button", on_button_click, winname)
        tcv2.createRadioButtons("radio", ["pomme", "poire"], winname, 1, on_radio_button)
        tcv2.createCheckbuttons("check multi", ["roue", "volant"], winname, [False, True], on_check_buttons)
        tcv2.createCheckbutton("check single", winname, False, on_check_button)
        tcv2.createColorPicker("Color picker", winname, "yellow", on_color_pick)
        tcv2.createInteractivePoint(winname, (100, 100), "point",
                on_click=on_point_click,
                on_drag=on_point_drag,
                on_release=on_point_release)

    cv2.namedWindow("ok")

    while True: # cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) > 0.5:
        k += 1
        cv2.imshow(winname, img * np.uint8(k))
        # tcv2.imshow("ok", img * np.uint8(k))
        print(cv2.waitKeyEx(0), end=", ")


def print_hello():
    print("hello")


if __name__ == '__main__':
    demo_cv()
