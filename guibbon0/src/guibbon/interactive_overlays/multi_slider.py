import tkinter as tk
from typing import Callable, Any, Sequence, Optional

from guibbon.typedef import Point2Di
from .base import Point

MultiSliderState = list[tuple[int, Any]]
CallbackMultiSlider = Callable[[MultiSliderState], None]


class MultiSliderOverlay:
    colors = {
        "grey": "#%02x%02x%02x" % (191, 191, 191),
    }

    def __init__(
        self,
        canvas: tk.Canvas,
        values: Sequence[Any],
        initial_positions: Sequence[int],
        on_drag: Optional[CallbackMultiSlider] = None,
        on_release: Optional[CallbackMultiSlider] = None,
    ):
        self.canvas = canvas
        self.values: list[Any] = [v for v in values]

        self.on_drag = on_drag
        self.on_release = on_release

        self.line_ids = []
        self.line_ids.append(self.canvas.create_line(-1, -1, -1, -1, fill=MultiSliderOverlay.colors["grey"], width=3))
        for i in range(len(values)):
            self.line_ids.append(self.canvas.create_line(-1, -1, -1, -1, fill=MultiSliderOverlay.colors["grey"], width=3))

        # self.positions_values: MultiSliderState = []
        self.cursors: list[Point] = []

        self.cursor_positions: list[int] = []
        for k in range(len(initial_positions)):
            self.add_cursor(position=initial_positions[k])

        self.update_canvas()

    def add_cursor(self, position: int = 0):
        new_cursor_id = len(self.cursors)

        def on_drag_wrap(event: tk.Event) -> None:
            self.on_drag_callback(new_cursor_id, event)
            return None

        cursor = Point(
            canvas=self.canvas,
            point_xy=(-1, -1),
            on_drag=on_drag_wrap,
            on_release=None if self.on_release is None else self.on_release_callback,
        )
        self.cursors.append(cursor)
        self.cursor_positions.append(position)
        self.update_canvas()

    def remove_cursor(self):
        if len(self.cursors) <= 1:
            return
        cursor = self.cursors.pop()
        cursor.set_visible(False)
        cursor.delete()
        self.cursor_positions.pop()
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
        for cursor_pos, cursor in zip(self.cursor_positions, self.cursors):
            x_slider = cursor_pos
            point_xy_can = self.slider2canvas((x_slider, 0))
            cursor.set_can_point_xy(point_xy_can)
            cursor.update()

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

    def on_drag_callback(self, cursor_id, event: tk.Event):
        x_slider, y_slider = self.canvas2slider((event.x, event.y))
        x_can, y_can = self.slider2canvas((x_slider, y_slider))
        self.cursors[cursor_id].set_can_point_xy((x_can, y_can))
        self.cursors[cursor_id].update()

        old_ind = self.cursor_positions[cursor_id]
        new_ind = x_slider
        if old_ind == new_ind:
            return

        self.cursor_positions[cursor_id] = x_slider

        if self.on_drag is not None:
            positions_values = [(pos, self.values[pos]) for pos in self.cursor_positions]
            self.on_drag(positions_values)

    def on_release_callback(self, event: tk.Event):
        if self.on_release is not None:
            positions_values = [(pos, self.values[pos]) for pos in self.cursor_positions]
            self.on_release(positions_values)

    def get_positions(self) -> list[int]:
        return self.cursor_positions + []

    def set_positions(self, positions: Sequence[int], trigger_callback=True):
        delta = len(positions) - len(self.cursor_positions)
        if delta > 0:
            for _ in range(delta):
                self.add_cursor(position=0)
        elif delta < 0:
            for _ in range(-delta):
                self.remove_cursor()

        self.cursor_positions = [pos for pos in positions]
        self.update_canvas()
        if trigger_callback:
            positions_values = [(pos, self.values[pos]) for pos in self.cursor_positions]
            if self.on_drag is not None:
                self.on_drag(positions_values)
            if self.on_release is not None:
                self.on_release(positions_values)

    def get_values(self) -> list[Any]:
        return self.values + []

    def set_values(self, values: Sequence[Any], trigger_callback=True):
        self.values = [v for v in values]
        self.cursor_positions = [min(pos, len(self.values) - 1) for pos in self.cursor_positions]
        self.update_canvas()
        if trigger_callback:
            positions_values = [(pos, self.values[pos]) for pos in self.cursor_positions]
            if self.on_drag is not None:
                self.on_drag(positions_values)
            if self.on_release is not None:
                self.on_release(positions_values)
