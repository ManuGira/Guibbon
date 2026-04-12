import tkinter as tk
from typing import Callable, Any, Sequence

CallbackSlider = Callable[[int, Any], None]
from .base import BuildableWidget, BaseWidget
import dataclasses


@dataclasses.dataclass
class SliderWidget(BuildableWidget, BaseWidget):
    name: str
    values: Sequence[Any]
    initial_position: int
    on_change: CallbackSlider
    widget_color: Any = None

    def __post_init__(self, ):
        self.name_var = tk.StringVar()
        self.name_var.set(self.name)

        # ensure we hold lists (copy input sequences) like the original implementation
        self.values = list(self.values)
        self.value_var = tk.StringVar()

    def build(self, master: tk.Frame) -> None:
        frame_top = tk.Frame(master, bg=self.widget_color)
        tk.Label(master=frame_top, textvariable=self.name_var, bg=self.widget_color).pack(padx=2, side=tk.LEFT)
        self.value_var.set(self.values[self.initial_position])
        tk.Label(master=frame_top, textvariable=self.value_var, bg=self.widget_color).pack(padx=2, side=tk.TOP)
        frame_top.pack(side=tk.TOP, fill=tk.X, expand=1)

        count = len(self.values)
        self.tk_scale = tk.Scale(master, from_=0, to=count - 1, orient=tk.HORIZONTAL, bg=self.widget_color,
                                 borderwidth=0, showvalue=False)
        self.tk_scale.set(self.initial_position)

        self.tk_scale["command"] = self.callback
        self.tk_scale.pack(padx=2, fill=tk.X, expand=1)

    def __setattr__(self, key, value):
        if key == "name" and key in self.__dict__.keys():
            self.name_var.set(value)
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
