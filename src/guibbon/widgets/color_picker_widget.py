import tkinter as tk
from tkinter.colorchooser import askcolor
from typing import Callable, Optional

CallbackColorPicker = Callable[[tuple[int, int, int]], None]


def convert_color_tuple3i_to_hexastr(color_rgb: tuple[int, int, int]) -> str:
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
    def __init__(self, tk_frame, name: str, on_change: CallbackColorPicker, initial_color_rgb: Optional[tuple[int, int, int]] = None):
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
        self.color_rgb: tuple[int, int, int] = initial_color_rgb

        color_hex = convert_color_tuple3i_to_hexastr(self.color_rgb)
        self.canvas = tk.Canvas(self.frame, bg=color_hex, bd=3, height=10)
        self.button = tk.Button(self.frame, text="Edit", command=self.callback)

        self.canvas.pack(padx=2, side=tk.LEFT, anchor=tk.W)
        self.button.pack(padx=2, side=tk.LEFT, anchor=tk.W)
        self.frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)

    def callback(self):
        # askcolor expects hex string, not RGB tuple
        hex_color = convert_color_tuple3i_to_hexastr(self.get_current_value())
        colors = askcolor(title="Color Chooser", color=hex_color)
        if colors[0] is not None:
            r, g, b = colors[0]
            self.color_rgb = (r, g, b)
        self.canvas["bg"] = convert_color_tuple3i_to_hexastr(self.color_rgb)
        self.on_change(self.color_rgb)

    def get_current_value(self) -> tuple[int, int, int]:
        return self.color_rgb
