import tkinter as tk
from tkinter.colorchooser import askcolor
from typing import Callable, Tuple, Optional

CallbackColorPicker = Callable[[Tuple[int, int, int]], None]


def convert_color_tuple3i_to_hexastr(color_rgb: Tuple[int, int, int]) -> str:
    """
    >>> convert_color_tuple3i_to_hexastr((0, 0, 0))
    '#000000'
    >>> convert_color_tuple3i_to_hexastr((255, 0, 10))
    '#ff000a'
    """
    assert isinstance(color_rgb, tuple)
    assert len(color_rgb) == 3
    for c in color_rgb:
        assert isinstance(c, int)
    assert min(color_rgb) >= 0
    assert max(color_rgb) <= 255
    r, g, b = color_rgb
    return f"#{r:02x}{g:02x}{b:02x}"


class ColorPickerWidget:
    def __init__(self, tk_frame, name: str, on_change: CallbackColorPicker, initial_color_rgb: Optional[Tuple[int, int, int]] = None):
        self.frame = tk.Frame(tk_frame)
        label = tk.Label(self.frame, text=name)
        label.pack(padx=2, side=tk.LEFT, anchor=tk.W)
        self.on_change = on_change

        if initial_color_rgb is None:
            initial_color_rgb = (0, 0, 0)
        assert isinstance(initial_color_rgb, tuple)
        assert len(initial_color_rgb) == 3
        for c in initial_color_rgb:
            assert isinstance(c, int)
        assert min(initial_color_rgb) >= 0
        assert max(initial_color_rgb) <= 255
        self.color_rgb: Tuple[int, int, int] = initial_color_rgb

        color_hex = convert_color_tuple3i_to_hexastr(self.color_rgb)
        self.canvas = tk.Canvas(self.frame, bg=color_hex, bd=2, height=10)
        self.canvas.bind("<Button-1>", self.callback)

        self.canvas.pack(side=tk.LEFT, anchor=tk.W)
        self.frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)

    def callback(self, event):
        colors = askcolor(title="Color Chooser")
        if colors[0] is not None:
            r, g, b = colors[0]
            self.color_rgb = (r, g, b)
        self.canvas["bg"] = convert_color_tuple3i_to_hexastr(self.color_rgb)
        self.on_change(self.color_rgb)

    def get_current_value(self) -> Tuple[int, int, int]:
        return self.color_rgb
