import tkinter as tk
from typing import Callable, Any, Sequence, List, Tuple
from guibbon.interactive_overlays import Point
from guibbon.typedef import Point2Di, tkEvent

CallbackMultiSlider = Callable[[List[Tuple[int, Any]]], None]

class MultiSliderWidget:
    colors = {
        "grey": "#%02x%02x%02x" % (191, 191, 191),
    }

    def __init__(self, tk_frame: tk.Frame, multislider_name: str, values: Sequence[Any], initial_indexes: Sequence[int], on_change: CallbackMultiSlider, widget_color):
        self.name = tk.StringVar()
        self.name.set(multislider_name)
        self.initial_indexes = initial_indexes  # should copy this
        N = len(self.initial_indexes)

        self.values = values
        self.on_change = on_change

        self.cursors_positions: List[Tuple[int, Any]] = [(ind, values[ind]) for ind in initial_indexes]

        tk.Label(tk_frame, textvariable=self.name, bg=widget_color).pack(padx=2, side=tk.TOP, anchor=tk.W)

        # create 1 label (with a string var) for each cursor
        self.cursors_strvar = []
        for i in range(N):
            var = tk.StringVar()
            var.set(self.cursors_positions[i][1])

            self.cursors_strvar.append(var)
            tk.Label(tk_frame, textvariable=var, bg=widget_color).pack(padx=2, side=tk.TOP, anchor=tk.W)

        self.canvas = tk.Canvas(master=tk_frame, height=21, borderwidth=0)
        self.canvas.pack(side=tk.TOP, fill=tk.X)

        self.line_ids = []
        self.line_ids.append(self.canvas.create_line(-1, -1, -1, -1, fill=MultiSliderWidget.colors["grey"], width=3))
        for i in range(len(values)):
            self.line_ids.append(self.canvas.create_line(-1, -1, -1, -1, fill=MultiSliderWidget.colors["grey"], width=3))

        self.cursors: List[Point] = []

        # create interactive points and their custom callbacks
        # k_=k to fix value of k
        on_change_lambdas = [lambda event, k_=k: self.callback(k_, event) for k in range(N)]
        for cursor_id in range(N):
            self.cursors.append(
                Point(
                    canvas=self.canvas,
                    point_xy=(-1, -1),
                    on_drag=on_change_lambdas[cursor_id],
                )
            )

        self.update_canvas()

    def update_canvas(self):
        self.canvas.update_idletasks()  # forces to compute rendered position and size of the canvas

        N = len(self.values)

        for i, line_id in enumerate(self.line_ids[:-1]):
            line_x, line_y = self.slider2canvas((i, 0))
            self.canvas.coords(line_id, line_x, line_y-2, line_x, line_y+3)
            self.canvas.itemconfig(line_id, state="normal")
            self.canvas.tag_raise(line_id)

        # horizontal_lines
        line_x0, line_y0 = self.slider2canvas((0, 0))
        line_x1, line_y1 = self.slider2canvas((N - 1, 0))
        self.canvas.coords(self.line_ids[-1], line_x0, line_y0, line_x1, line_y1)
        self.canvas.itemconfig(self.line_ids[-1], state="normal")
        self.canvas.tag_raise(self.line_ids[-1])

        for cursor_pos, cursor in zip(self.cursors_positions, self.cursors):
            x_slider = cursor_pos[0]
            point_xy_can = self.slider2canvas((x_slider, 0))
            cursor.set_can_point_xy(point_xy_can)
            cursor.update()

    def __setattr__(self, key, value):
        if key == "name" and key in self.__dict__.keys():
            self.name.set(value)
        else:
            return super().__setattr__(key, value)

    def slider2canvas(self, point_xy: Point2Di) -> Point2Di:
        w_can = self.canvas.winfo_width()
        h_can = self.canvas.winfo_height()
        margin = h_can // 2

        w_slider = max(1, len(self.values) - 1)
        w_slider_can = max(1, w_can - 2 * margin)
        scale = w_slider / w_slider_can

        x_slider, y_slider = point_xy

        x_can = int(round(x_slider / scale + margin))
        y_can = margin + 1
        return x_can, y_can

    def canvas2slider(self, point_xy: Point2Di) -> Point2Di:
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

    def callback(self, cursor_id, event: tkEvent):
        x_slider, y_slider = self.canvas2slider((event.x, event.y))
        x_can, y_can = self.slider2canvas((x_slider, y_slider))
        self.cursors[cursor_id].set_can_point_xy((x_can, y_can))
        self.cursors[cursor_id].update()

        old_ind = self.cursors_positions[cursor_id][0]
        new_ind = x_slider
        if old_ind == new_ind:
            return

        self.cursors_positions[cursor_id] = (x_slider, self.values[x_slider])

        for var, curs_pos in zip(self.cursors_strvar, self.cursors_positions):
            var.set(curs_pos[1])

        self.on_change(self.cursors_positions)

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
