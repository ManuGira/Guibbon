import tkinter as tk
from typing import Any, Sequence, Optional

from guibbon.interactive_overlays import MultiSliderOverlay, MultiSliderState, CallbackMultiSlider


class MultiSliderWidget:


    def __init__(self,
                 tk_frame: tk.Frame,
                 multi_slider_name: str,
                 values: Sequence[Any],
                 initial_positions: Sequence[int],
                 on_drag: Optional[CallbackMultiSlider] = None,
                 on_release: Optional[CallbackMultiSlider] = None,
                 widget_color=None):

        frame_top = tk.Frame(tk_frame, bg=widget_color)
        self.name = tk.StringVar(value=multi_slider_name)
        tk.Label(master=frame_top, textvariable=self.name, bg=widget_color).pack(padx=2, side=tk.LEFT)
        self.label_txt = tk.StringVar()
        tk.Label(master=frame_top, textvariable=self.label_txt, bg=widget_color).pack(padx=2, side=tk.TOP)

        frame_top.pack(side=tk.TOP, fill=tk.X, expand=1)

        canvas = tk.Canvas(master=tk_frame, height=21, borderwidth=0, bg=widget_color)
        canvas.pack(side=tk.TOP, fill=tk.X)

        self.multi_slider_overlay = MultiSliderOverlay(
            canvas,
            values,
            initial_positions,
            on_drag=self.on_drag_callback,
            on_release=self.on_release_callback,
        )

        self.on_drag = on_drag
        self.on_release = on_release

        self.update_label()


    def update_label(self) -> None:
        values = self.multi_slider_overlay.get_values()
        positions = self.multi_slider_overlay.get_positions()
        pvalues = [str(values[pos]) for pos in positions]
        self.label_txt.set("[" + ", ".join(pvalues) + "]")


    def on_drag_callback(self, positions_values: MultiSliderState) -> None:
        """
        Wrapper for on_drag callback
        This wrapper is called by the MultiSlider instance
        This wrapper calls the user-defined on_drag callback
        """
        self.update_label()
        if self.on_drag is not None:
            self.on_drag(positions_values)

    def on_release_callback(self, positions_values: MultiSliderState) -> None:
        """
        Wrapper for on_release callback
        This wrapper is called by the MultiSlider instance
        This wrapper calls the user-defined on_release callback
        """
        self.update_label()
        if self.on_release is not None:
            self.on_release(positions_values)

    def add_cursor(self, position: int = 0) -> None:
        self.multi_slider_overlay.add_cursor(position)
        self.update_label()

    def remove_cursor(self) -> None:
        self.multi_slider_overlay.remove_cursor()
        self.update_label()

    def get_positions(self):
        return self.multi_slider_overlay.get_positions()

    def set_positions(self, positions: Sequence[int], trigger_callback=True):
        self.multi_slider_overlay.set_positions(positions, trigger_callback)
        self.update_label()

    def get_values(self):
        return self.multi_slider_overlay.get_values()

    def set_values(self, values: Sequence[Any], new_position=None, trigger_callback=True):
        # MultiSliderOverlay.set_values doesn't accept new_position parameter
        self.multi_slider_overlay.set_values(values, trigger_callback)
        self.update_label()


