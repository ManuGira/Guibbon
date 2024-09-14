import tkinter as tk
from typing import Callable, Any, Sequence

CallbackSlider = Callable[[int, Any], None]


class SliderWidget:
    def __init__(self, tk_frame: tk.Frame, slider_name: str, values: Sequence[Any], initial_position: int, on_change: CallbackSlider, widget_color):
        self.name = tk.StringVar()
        self.name.set(slider_name)

        self.values = values
        self.on_change = on_change
        self.value_var = tk.StringVar()

        tk.Label(tk_frame, textvariable=self.name, bg=widget_color).pack(padx=2, side=tk.LEFT)
        self.value_var.set(self.values[initial_position])
        tk.Label(tk_frame, textvariable=self.value_var, bg=widget_color).pack(padx=2, side=tk.TOP)
        count = len(self.values)
        self.tk_scale = tk.Scale(tk_frame, from_=0, to=count - 1, orient=tk.HORIZONTAL, bg=widget_color, borderwidth=0, showvalue=False)
        self.tk_scale.set(initial_position)

        self.tk_scale["command"] = self.callback
        self.tk_scale.pack(padx=2, fill=tk.X, expand=1)

    def __setattr__(self, key, value):
        if key == "name" and key in self.__dict__.keys():
            self.name.set(value)
        else:
            return super().__setattr__(key, value)

    def callback(self, position):
        val = self.values[int(position)]
        self.value_var.set(val)
        return self.on_change(position, val)

    def set_position(self, position, trigger_callback=True):
        self.tk_scale.set(position)
        if trigger_callback:
            self.callback(position)

    def get_position(self):
        return self.tk_scale.get()

    def get_values(self):
        return self.values

    def set_values(self, values, new_position=None):
        count = len(values)
        self.tk_scale["to"] = count - 1
        self.values = values
        if new_position is not None:
            self.set_position(new_position, trigger_callback=False)
            self.value_var.set(values[new_position])
