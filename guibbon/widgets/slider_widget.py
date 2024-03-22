import tkinter as tk
from typing import Callable, Any, Sequence

CallbackSlider = Callable[[int, Any], None]
class SliderWidget:
    def __init__(self, tk_frame: tk.Frame, slider_name: str, values: Sequence[Any], initial_index: int, on_change: CallbackSlider, widget_color):
        self.name = slider_name
        self.values = values
        self.on_change = on_change
        self.value_var = tk.StringVar()

        tk.Label(tk_frame, text=self.name, bg=widget_color).pack(padx=2, side=tk.LEFT)
        self.value_var.set(self.values[initial_index])
        tk.Label(tk_frame, textvariable=self.value_var, bg=widget_color).pack(padx=2, side=tk.TOP)
        count = len(self.values)
        self.tk_scale = tk.Scale(tk_frame, from_=0, to=count - 1, orient=tk.HORIZONTAL, bg=widget_color, borderwidth=0, showvalue=False)
        self.tk_scale.set(initial_index)

        self.tk_scale["command"] = self.callback
        self.tk_scale.pack(padx=2, fill=tk.X, expand=1)

    def callback(self, index):
        val = self.values[int(index)]
        self.value_var.set(val)
        return self.on_change(index, val)

    def set_index(self, index, trigger_callback=True):
        self.tk_scale.set(index)
        if trigger_callback:
            self.callback(index)

    def get_index(self):
        return self.tk_scale.get()

    def get_values(self):
        return self.values

    def set_values(self, values, new_index=None):
        count = len(values)
        self.tk_scale["to"] = count - 1
        self.values = values
        if new_index is not None:
            self.set_index(new_index, trigger_callback=False)
            self.value_var.set(values[new_index])
