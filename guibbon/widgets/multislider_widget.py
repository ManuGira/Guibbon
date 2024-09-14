import tkinter as tk
from typing import Callable, Any, Sequence, List, Tuple, Optional
from guibbon.interactive_overlays import Point
from guibbon.typedef import Point2Di, tkEvent

CallbackMultiSlider = Callable[[List[Tuple[int, Any]]], None]


class MultiSliderWidget:
    colors = {
        "grey": "#%02x%02x%02x" % (191, 191, 191),
    }

    def __init__(self, tk_frame: tk.Frame, multislider_name: str, values: Sequence[Any], initial_positions: Sequence[int], on_drag: Optional[CallbackMultiSlider] = None,
                 on_release: Optional[CallbackMultiSlider] = None, widget_color=None):
        self.name = tk.StringVar(value=multislider_name)
        self.values = values
        N = len(initial_positions)
        self.positions_values: List[Tuple[int, Any]] = [(ind, self.values[ind]) for ind in initial_positions]
        self.on_drag = on_drag
        self.on_release = on_release

        tk.Label(tk_frame, textvariable=self.name, bg=widget_color).pack(padx=2, side=tk.LEFT)
        self.label_txt = tk.StringVar()
        tk.Label(tk_frame, textvariable=self.label_txt, bg=widget_color).pack(padx=2, side=tk.TOP)

        self.canvas = tk.Canvas(master=tk_frame, height=21, borderwidth=0, bg=widget_color)
        self.canvas.pack(side=tk.TOP, fill=tk.X)

        self.line_ids = []
        self.line_ids.append(self.canvas.create_line(-1, -1, -1, -1, fill=MultiSliderWidget.colors["grey"], width=3))
        for i in range(len(values)):
            self.line_ids.append(self.canvas.create_line(-1, -1, -1, -1, fill=MultiSliderWidget.colors["grey"], width=3))

        self.cursors: List[Point] = []

        # create interactive points and their custom callbacks
        # k_=k to fix value of k
        on_drag_lambdas = [lambda event, k_=k: self.on_drag_callback(k_, event) for k in range(N)]
        for cursor_id in range(N):
            self.cursors.append(
                Point(
                    canvas=self.canvas,
                    point_xy=(-1, -1),
                    on_drag=on_drag_lambdas[cursor_id],
                    on_release=None if self.on_release is None else self.on_release_callback,
                )
            )

        self.update_canvas()

    def update_canvas(self):
        self.canvas.update_idletasks()  # forces to compute rendered positions_values and size of the canvas

        N = len(self.values)

        # draw ticks
        for i, line_id in enumerate(self.line_ids[:-1]):
            line_x, line_y = self.slider2canvas((i, 0))
            self.canvas.coords(line_id, line_x, line_y - 2, line_x, line_y + 3)
            self.canvas.itemconfig(line_id, state="normal")
            self.canvas.tag_raise(line_id)

        # draw horizontal line
        line_x0, line_y0 = self.slider2canvas((0, 0))
        line_x1, line_y1 = self.slider2canvas((N - 1, 0))
        self.canvas.coords(self.line_ids[-1], line_x0, line_y0, line_x1, line_y1)
        self.canvas.itemconfig(self.line_ids[-1], state="normal")
        self.canvas.tag_raise(self.line_ids[-1])

        # draw cursors
        for cursor_pos, cursor in zip(self.positions_values, self.cursors):
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

    def on_drag_callback(self, cursor_id, event: tkEvent):
        x_slider, y_slider = self.canvas2slider((event.x, event.y))
        x_can, y_can = self.slider2canvas((x_slider, y_slider))
        self.cursors[cursor_id].set_can_point_xy((x_can, y_can))
        self.cursors[cursor_id].update()

        old_ind = self.positions_values[cursor_id][0]
        new_ind = x_slider
        if old_ind == new_ind:
            return

        self.positions_values[cursor_id] = (x_slider, self.values[x_slider])

        self.label_txt.set("[" + ", ".join([str(curs_pos[1]) for curs_pos in self.positions_values]) + "]")

        if self.on_drag is not None:
            self.on_drag(self.positions_values)

    def on_release_callback(self, event: tkEvent):
        if self.on_release is not None:
            self.on_release(self.positions_values)

    def set_positions(self, positions: Sequence[int], trigger_callback=True):
        self.positions_values = [(ind, self.values[ind]) for ind in positions]
        self.update_canvas()
        if trigger_callback:
            if self.on_drag is not None:
                self.on_drag(self.positions_values)
            if self.on_release is not None:
                self.on_release(self.positions_values)

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
