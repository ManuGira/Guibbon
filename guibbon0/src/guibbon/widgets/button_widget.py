import tkinter as tk
from typing import Callable

CallbackButton = Callable[[], None]


class ButtonWidget:
    def __init__(self, tk_frame, text, on_click: CallbackButton):
        self.tk_frame = tk_frame
        self.button = tk.Button(tk_frame, text=text, command=on_click)
        self._is_visible = False
        self.set_visible(True)

    def set_visible(self, val):
        if val == self._is_visible:
            return
        self._is_visible = val

        if val:
            self.button.pack(side=tk.LEFT)
        else:
            self.button.pack_forget()
