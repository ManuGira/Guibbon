import time
import numpy as np
import cv2
import tk4cv2 as tcv2
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

def demo_cv():
    img = cv2.imread("images/dog.jpg")

    k = 0
    title = "Demo Tk4Cv2"
    cv2.namedWindow(title)
    cv2.createTrackbar("trackbar_name", title, 0, 10, on_trackbar)
    tcv2.createButton("the button", on_button_click, title)
    tcv2.createRadioButtons("radio", ["pomme", "poire"], title, 1, on_radio_button)
    tcv2.createCheckbuttons("check multi", ["roue", "volant"], title, [False, True], on_check_buttons)
    tcv2.createCheckbutton("check single", title, False, on_check_button)
    tcv2.createColorPicker("Color picker", title, "yellow", on_color_pick)
    cv2.setMouseCallback(title, on_mouse_event)

    while True:
        k += 1
        cv2.imshow(title, img*np.uint8(k))
        print(cv2.waitKeyEx(0), end=", ")

def print_hello():
    print("hello")


if __name__ == '__main__':
    demo_cv()
