# type: ignore

import sys
import numpy as np
import cv2
import guibbon as tcv2

if "guibbon" in sys.modules:
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
    winname = "Demo Guibbon"
    cv2.namedWindow(winname)
    cv2.createTrackbar("trackbar_name", winname, 0, 10, on_trackbar)
    cv2.setTrackbarMin("trackbar_name", winname, 2)
    cv2.setTrackbarMax("trackbar_name", winname, 12)
    cv2.setTrackbarPos("trackbar_name", winname, 6)
    cv2.setMouseCallback(winname, on_mouse_event)

    if "guibbon" in sys.modules:
        # type: ignore
        radio_buttons = tcv2.create_radio_buttons(winname, "radio2", ["peche", "prune"], on_radio_button)
        # tcv2.createButton("more fruit", lambda : radio_buttons.set_options_list(["oups", "ok", "voilà"]), winname)
        button = tcv2.create_button(winname, "more fruit", lambda: radio_buttons.set_options_list(["oups", "ok", "voilà"]))
        tcv2.create_button(winname, "hide", lambda: button.set_visible(False))
        tcv2.create_button(winname, "show", lambda: tcv2.get_button_instance(winname, "more fruit").set_visible(True))

        tcv2.create_check_button_list(winname, "check multi", ["roue", "volant"], on_check_buttons, [False, True])
        tcv2.create_check_button(winname, "check single", on_check_button, initial_value=True)
        tcv2.create_color_picker(winname, "Color picker", on_color_pick, (255, 0, 0))
        tcv2.createInteractivePoint(winname, (100, 100), "point", on_click=on_point_click, on_drag=on_point_drag, on_release=on_point_release)

    cv2.namedWindow("ok")

    while tcv2.Guibbon.is_instance(winname):  # cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) > 0.5:
        k += 1
        cv2.imshow(winname, img * np.uint8(k))
        # tcv2.imshow("ok", img * np.uint8(k))
        print(cv2.waitKeyEx(0), end=", ")


def print_hello():
    print("hello")


if __name__ == "__main__":
    demo_cv()
