import tkinter as tk
from typing import Callable, Optional

import numpy as np
import cv2

from .multi_slider_widget import MultiSliderOverlay, MultiSliderState

Vector3Di = tuple[int, int, int]
# A color space is a list of 3d vectors, the sum of which is 255 for each component
ColorSpace = list[Vector3Di]
CallbackColorSpace = Callable[[ColorSpace], None]


class ColorSpaceWidget:
    colors = {
        "grey": "#%02x%02x%02x" % (191, 191, 191),
    }

    @staticmethod
    def rgb_segments_to_color_space(red_segments: list[int], green_segments: list[int],
                                    blue_segements: list[int]) -> ColorSpace:
        red_segments = list(sorted(red_segments)) + [255]
        green_segments = list(sorted(green_segments)) + [255]
        blue_segements = list(sorted(blue_segements)) + [255]

        color_space = []
        color_prev = np.array([0, 0, 0], dtype=int)
        for k in range(len(red_segments)):
            rgb = np.array([
                red_segments[k],
                green_segments[k],
                blue_segements[k]
            ], dtype=int)
            color_k = rgb - color_prev
            color_space.append(tuple(color_k.tolist()))
            color_prev = rgb

        return color_space

    @staticmethod
    def color_space_to_rgb_segments(color_space: ColorSpace) -> tuple[list[int], list[int], list[int]]:
        """
        Convert a color space (list of RGB deltas) to RGB segment positions.
        This is the inverse operation of rgb_segments_to_color_space.

        Args:
            color_space: List of RGB delta vectors

        Returns:
            Tuple of (red_segments, green_segments, blue_segments)
        """
        red_segments = []
        green_segments = []
        blue_segments = []

        color_accumulated = np.array([0, 0, 0], dtype=int)
        for delta_r, delta_g, delta_b in color_space:
            delta = np.array([delta_r, delta_g, delta_b], dtype=int)
            color_accumulated = color_accumulated + delta
            red_segments.append(int(color_accumulated[0]))
            green_segments.append(int(color_accumulated[1]))
            blue_segments.append(int(color_accumulated[2]))

        # Get rid of last segment and ensure it is 255
        assert red_segments.pop(-1) == 255
        assert green_segments.pop(-1) == 255
        assert blue_segments.pop(-1) == 255

        return red_segments, green_segments, blue_segments

    def __init__(self,
                 tk_frame: tk.Frame,
                 color_space_name: str,
                 initial_color_space: ColorSpace,
                 on_drag: Optional[CallbackColorSpace] = None,
                 on_release: Optional[CallbackColorSpace] = None,
                 widget_color=None):
        """
        Widget made of 3 multi-sliders (one per channel) to represent a color space
        Creates 3 canvas for sliders, and 1 canvas to display the resulting color (overlaping circles)
        """
        self.on_drag = on_drag
        self.on_release = on_release

        self.color_space: ColorSpace = []
        for rgb_vector in initial_color_space:
            r, g, b = rgb_vector
            self.color_space.append((int(r), int(g), int(b)))

        self.M = len(initial_color_space)
        self.multi_slider_overlays: list[MultiSliderOverlay] = []

        initial_rgb_segments = ColorSpaceWidget.color_space_to_rgb_segments(self.color_space)

        frame_top = tk.Frame(tk_frame, bg=widget_color)
        self.name = tk.StringVar(value=color_space_name)
        tk.Label(master=frame_top, textvariable=self.name, bg=widget_color).pack(padx=2, side=tk.LEFT)
        self.label_txt = tk.StringVar()
        tk.Label(master=frame_top, textvariable=self.label_txt, bg=widget_color).pack(padx=2, side=tk.TOP)

        frame_top.pack(side=tk.TOP, fill=tk.X, expand=1)

        for channel in range(3):
            canvas = tk.Canvas(master=tk_frame, height=21, borderwidth=0, bg=widget_color)
            canvas.pack(side=tk.TOP, fill=tk.X)

            multi_slider_overlay = MultiSliderOverlay(
                canvas=canvas,
                values=range(256),
                initial_positions=initial_rgb_segments[channel],
                on_drag=lambda positions_values, channel_=channel: self.on_drag_callback(channel_, positions_values),  # type: ignore[misc]
                on_release=self.on_release_callback,
            )
            self.multi_slider_overlays.append(multi_slider_overlay)

        self.visual_canvas = tk.Canvas(master=tk_frame, height=200, borderwidth=0, bg=widget_color)
        self.visual_canvas.pack(side=tk.TOP, fill=tk.X, expand=1)
        self.update_visualization()

    def update_visualization(self) -> None:
        """
        Create and display an RGB image in the visual canvas.
        Currently displays a black image with a red circle.
        """
        # Get canvas dimensions
        self.visual_canvas.update_idletasks()
        height = self.visual_canvas.winfo_height()
        width = height
        radius = (height - 20) // 3

        def create_image(color: Vector3Di, theta: float) -> np.ndarray[tuple[int, int, int], np.dtype[np.uint8]]:
            # Create a black RGB image using numpy
            img = np.zeros((height, width, 3), dtype=np.uint8)

            # Draw a red circle using cv2
            center = np.array([width / 2, height / 2], dtype=float)
            off_center = radius / 2
            circle_center = center + off_center * np.array([np.cos(theta), np.sin(theta)])
            circle_center = np.round(circle_center).astype(int)

            thickness = -1  # Filled circle

            # Convert color tuple to proper format for cv2.circle
            color_tuple = (int(color[0]), int(color[1]), int(color[2]))
            cv2.circle(img, tuple(circle_center.tolist()), radius, color_tuple, thickness)

            return img

        img_rgb = create_image((0, 0, 0), 0.0)
        N = len(self.color_space)
        for i, color in enumerate(self.color_space):
            theta = 2.0 * np.pi * (i / N)
            img_rgb += create_image(color, theta)

        # Convert to PIL Image and then to PhotoImage for tkinter
        from PIL import Image, ImageTk
        pil_img = Image.fromarray(img_rgb)
        self.photo_img = ImageTk.PhotoImage(image=pil_img)

        # Clear canvas and display the image
        self.visual_canvas.delete("all")
        self.visual_canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_img)

    def update_color_space(self) -> None:
        red_position_list = self.multi_slider_overlays[0].get_positions()
        green_position_list = self.multi_slider_overlays[1].get_positions()
        blue_position_list = self.multi_slider_overlays[2].get_positions()

        self.color_space = ColorSpaceWidget.rgb_segments_to_color_space(red_position_list, green_position_list,
                                                                        blue_position_list)

    def get_color_space(self) -> ColorSpace:
        return self.color_space + []

    def on_drag_callback(self, channel: int, positions_values: MultiSliderState) -> None:
        """
        Wrapper for on_drag callback
        This wrapper is called by the MultiSlider instance
        This wrapper calls the user-defined on_drag callback
        """
        self.update_color_space()
        self.update_visualization()
        if self.on_drag is not None:
            self.on_drag(self.color_space)

    def on_release_callback(self, positions_values: MultiSliderState) -> None:
        """
        Wrapper for on_release callback
        This wrapper is called by the MultiSlider instance
        This wrapper calls the user-defined on_release callback
        """
        self.update_color_space()
        self.update_visualization()
        if self.on_release is not None:
            self.on_release(self.color_space)

