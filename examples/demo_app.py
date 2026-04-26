"""
Demo: end-to-end interactive image viewer.

Wires @guibbon.params → Controller → ImageViewer in a Tkinter window and
demonstrates the full event cycle:

  widget interaction
      → descriptor.triggered_callbacks filled
          → app.need_update = True
              → collect modified_descriptors
                  → on_change(params, modified_descriptors)
                      → compute image
                          → viewer.set_image(result)

The modified_descriptors pattern is used to show a cheap preview while the
user is dragging a slider, and the full result on release.

Run with:
    uv run python examples/demo_app.py
"""

import tkinter as tk

import cv2
import numpy as np

import guibbon
from guibbon import Controller, GetPath, ImageViewer, RadioDescriptor, SliderDescriptor
from guibbon.core.app import App


# ---------------------------------------------------------------------------
# Params definition
# ---------------------------------------------------------------------------


@guibbon.params
class Params:
    kernel_size: int = SliderDescriptor(
        values=list(range(1, 32, 2)),  # 1, 3, 5, ..., 31
        default=5,
        on_drag=True,
        on_release=True,
    )
    mode: str = RadioDescriptor(
        options=["original", "blur", "sharpen", "edges"],
        default="blur",
    )


# ---------------------------------------------------------------------------
# Synthetic test image (self-contained — no file required)
# ---------------------------------------------------------------------------


def _make_test_image(h: int = 400, w: int = 600) -> np.ndarray:
    """Return a colourful BGR uint8 image with visible structure."""
    y_idx, x_idx = np.mgrid[0:h, 0:w]
    checker = ((x_idx // 40 + y_idx // 40) % 2).astype(np.uint8) * 180
    r = (x_idx / w * 255).astype(np.uint8)
    g = (y_idx / h * 255).astype(np.uint8)
    b = checker
    return np.stack([b, g, r], axis=2)  # BGR


_BASE_IMAGE: np.ndarray = _make_test_image()


# ---------------------------------------------------------------------------
# Image computation
# ---------------------------------------------------------------------------


def compute_image(p: Params) -> np.ndarray:
    """Apply the selected filter to the base image and return a BGR array."""
    k = max(1, int(p.kernel_size))
    if k % 2 == 0:
        k += 1  # Gaussian kernel must be odd

    if p.mode == "original":
        return _BASE_IMAGE.copy()
    elif p.mode == "blur":
        return cv2.GaussianBlur(_BASE_IMAGE, (k, k), 0)
    elif p.mode == "sharpen":
        blurred = cv2.GaussianBlur(_BASE_IMAGE, (k, k), 0)
        return cv2.addWeighted(_BASE_IMAGE, 2.0, blurred, -1.0, 0)
    elif p.mode == "edges":
        gray = cv2.cvtColor(_BASE_IMAGE, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    return _BASE_IMAGE.copy()


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------


def run() -> None:
    params = Params()
    controller = Controller(params)
    viewer = ImageViewer(height=400, width=600, mode="fit")
    app = App(params)
    app.add_component(controller)

    # ── Tk layout ─────────────────────────────────────────────────────────
    root = tk.Tk()
    root.title("Guibbon — interactive demo")
    root.resizable(False, False)

    left_frame = tk.Frame(root, padx=8, pady=8)
    left_frame.pack(side=tk.LEFT, fill=tk.Y)

    right_frame = tk.Frame(root)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    controller.build(left_frame)
    viewer.build(right_frame)

    # ── Show initial image ────────────────────────────────────────────────
    viewer.set_image(compute_image(params))

    # ── Refresh loop (~60 fps) ────────────────────────────────────────────
    def _refresh() -> None:
        if app.need_update:
            modified = app.collect_modified_descriptors()
            app.clear_modified_descriptors()
            app.need_update = False

            # During drag: run compute anyway (lightweight enough for this demo).
            # In a heavier app, check `any("on_drag" in md for md in modified)`
            # to show a cheap preview instead.
            viewer.set_image(compute_image(params))

            # Update window title with live state (shows GetPath and modified_descriptors)
            k_path = GetPath(params.kernel_size)
            m_path = GetPath(params.mode)
            root.title(
                f"Guibbon demo  |  {k_path}={params.kernel_size}  "
                f"{m_path}={params.mode!r}  |  triggered: {modified}"
            )

        root.after(16, _refresh)

    root.after(16, _refresh)
    root.mainloop()


if __name__ == "__main__":
    run()
