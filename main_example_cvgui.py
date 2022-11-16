import cv2

import tkinter as tk
from PIL import Image, ImageTk
import pyautogui
import numpy as np


def on_trackbar(val):
    print("on_trackbar", val)

def main_cv():
    img = cv2.imread("image.jpg")
    img = cv2.resize(img, dsize=None, fx=0.2, fy=0.2)
    title = "yep"
    cv2.imshow(title, img)
    cv2.createTrackbar(trackbar_name, title, 0, 10, on_trackbar)

    print(cv2.waitKeyEx(0))

def print_hello():
    print("hello")

class ImageController():
    def __init__(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(master=self.root, bg="red")

        # Load an image in the script
        self.img_ratio = 4/4
        self.canvas_shape_hw = [720, int(720*self.img_ratio)]
        self.canvas = tk.Canvas(master=self.frame, height=self.canvas_shape_hw[0], width=self.canvas_shape_hw[1], bg="blue")
        self.imgtk = None
        self.zoom_factor = None
        img = np.zeros(shape=(100, 100, 3), dtype=np.uint8)
        self.imshow(img)


        self.ctrl_frame = tk.Frame(master=self.frame, bg="green")

        self.frame.pack()
        self.canvas.pack(side=tk.LEFT)
        self.ctrl_frame.pack()

    def addbutton(self, text='Button', command=None):
        tk.Button(self.ctrl_frame, text=text, command=command).pack(padx=10, pady=10, )

    def imshow(self, img):
        self.zoom_factor = min(self.canvas_shape_hw[0] / img.shape[0], self.canvas_shape_hw[1] / img.shape[1])
        img = cv2.resize(img, None, fx=self.zoom_factor, fy=self.zoom_factor, interpolation=cv2.INTER_LINEAR)

        self.imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
        self.canvas.create_image(self.canvas_shape_hw[1] // 2, self.canvas_shape_hw[0] // 2, anchor=tk.CENTER,
                                 image=self.imgtk)

    def show(self):
        # self.frame.master = win
        self.root.mainloop()

def main_image_controller():
    vcf = ImageController()
    vcf.addbutton("yo", print_hello)
    img = cv2.imread("image.jpg")
    vcf.imshow(img)
    vcf.show()

if __name__ == '__main__':
    # main_cv()
    main_image_controller()
