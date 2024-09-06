import tkinter as tk
from typing import Callable, Any, Sequence, List, Tuple
from guibbon.image_viewer import ImageViewer, MODE
from guibbon.interactive_overlays import Point
from guibbon.typedef import Point2D

CallbackMultiSlider = Callable[[List[Tuple[int, Any]]], None]


class MultiSliderWidget:
    def __init__(self, tk_frame: tk.Frame, multislider_name: str, values: Sequence[Any], initial_indexes: Sequence[int], on_change: CallbackMultiSlider, widget_color):
        self.name = tk.StringVar()
        self.name.set(multislider_name)
        self.initial_indexes = initial_indexes + []

        self.values = values
        self.on_change = on_change

        self.value_var = tk.StringVar()
        self.value_var.set(self.values[0])

        top_frame = tk.Frame(tk_frame)
        top_frame.pack(side=tk.TOP)
        tk.Label(top_frame, textvariable=self.name, bg=widget_color).pack(padx=2, side=tk.LEFT)
        tk.Label(top_frame, textvariable=self.value_var, bg=widget_color).pack(padx=2, side=tk.LEFT)

        self.canvas = tk.Canvas(master=tk_frame, height=21, bg="gray10", borderwidth=0)
        self.canvas.pack(side=tk.TOP, fill=tk.X)

        # forces to compute rendered position and size of the canvas
        tk_frame.pack()
        self.canvas.update_idletasks()  # forces to compute rendered position and size of the canvas

        self.cursors_positions: List[Tuple[int, Any]] = [(ind, values[ind]) for ind in initial_indexes]
        self.cursors: List[Point] = []
        N = len(self.initial_indexes)

        # k_=k to fix value of k
        on_change_lambdas = [lambda event, k_=k: self.callback(k_, event) for k in range(N)]

        for cursor_id in range(N):
            x_slider = self.cursors_positions[cursor_id][0]
            point_xy_can = self.slider2canvas((x_slider, 0))
            cursor = Point(
                canvas=self.canvas,
                point_xy=point_xy_can,
                on_drag=on_change_lambdas[cursor_id],
            )
            cursor.update()
            self.cursors.append(cursor)


    def __setattr__(self, key, value):
        if key == "name" and key in self.__dict__.keys():
            self.name.set(value)
        else:
            return super().__setattr__(key, value)

    def slider2canvas(self, point_xy: Point2D) -> Point2D:
        w_can = self.canvas.winfo_width()
        h_can = self.canvas.winfo_height()
        margin = h_can // 2

        w_slider = max(1, len(self.values) - 1)
        w_slider_can = max(1, w_can - 2 * margin)
        scale = w_slider / w_slider_can

        x_slider, y_slider = point_xy

        x_can = x_slider / scale + margin
        y_can = margin + 1
        return x_can, y_can

    def canvas2slider(self, point_xy: Point2D) -> Point2D:
        w_can = self.canvas.winfo_width()
        h_can = self.canvas.winfo_height()
        margin = h_can // 2

        w_slider = max(1, len(self.values) - 1)
        w_slider_can = max(1, w_can - 2 * margin)
        scale = w_slider / w_slider_can

        x_can, y_can = point_xy
        x_can_min = margin
        x_slider = (x_can - x_can_min) * scale
        x_slider = min(max(0.0, x_slider), w_slider)
        x_slider = int(round(x_slider))

        y_slider = 0
        return x_slider, y_slider

    def callback(self, cursor_id, event: tk.Event):
        x_slider, y_slider = self.canvas2slider((event.x, event.y))
        x_can, y_can = self.slider2canvas((x_slider, y_slider))
        self.cursors[cursor_id].set_can_point_xy((x_can, y_can))
        self.cursors[cursor_id].update()

        old_ind = self.cursors_positions[cursor_id][0]
        new_ind = x_slider
        if old_ind == new_ind:
            return

        self.cursors_positions[cursor_id] = (x_slider, self.values[x_slider])
        self.on_change(self.cursors_positions)

        # return self.on_change(x_slider, val)

    def update(self):
        """
        Refreshes cursor position according to canvas size
        """


    # def set_index(self, index, trigger_callback=True):
    #     self.tk_scale.set(index)
    #     if trigger_callback:
    #         self.callback(index)
    #
    # def get_index(self):
    #     return self.tk_scale.get()
    #
    # def get_values(self):
    #     return self.values
    #
    # def set_values(self, values, new_index=None):
    #     count = len(values)
    #     self.tk_scale["to"] = count - 1
    #     self.values = values
    #     if new_index is not None:
    #         self.set_index(new_index, trigger_callback=False)
    #         self.value_var.set(values[new_index])
