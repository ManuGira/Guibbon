import tkinter as tk
from typing import Callable


CallbackCheckButton = Callable[[bool], None]


class CheckButtonWidget:
    def __init__(self, tk_frame, name, value, on_change: CallbackCheckButton):
        self.name = name
        self.on_change: CallbackCheckButton = on_change

        self.frame = tk.Frame(tk_frame)
        self.label = tk.Label(self.frame, text=name).pack(padx=2, side=tk.LEFT, anchor=tk.W)

        self.var = tk.BooleanVar()
        self.var.set(value)
        cb = tk.Checkbutton(self.frame, text="", variable=self.var, onvalue=True, offvalue=False, command=self.callback)
        cb.pack(side=tk.TOP, anchor=tk.W)
        self.frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)

    def callback(self):
        self.on_change(self.var.get())

    def get_current_value(self) -> bool:
        return self.var.get()
