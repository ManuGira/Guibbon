"""Pattern 3 demo: InteractiveImageAppBase — parameter panel + image viewer.

Subclasses InteractiveImageAppBase, defines a Params dataclass, and computes
an image from the current parameter values every time a widget changes.

Features demonstrated:
- Slider for kernel size (uses on_drag for cheap preview, on_release for full)
- Radio button for filter mode
- Modified-descriptors pattern for drag-vs-release differentiation

Run with:
    uv run python examples/demo_pattern3_image_app.py
"""

import cv2
import numpy as np

import guibbon
from guibbon import SliderDescriptor, RadioDescriptor
from guibbon.apps import InteractiveImageAppBase


# ---------------------------------------------------------------------------
# Synthetic test image (self-contained — no file required)
# ---------------------------------------------------------------------------


def _make_base_image(h: int = 400, w: int = 600) -> np.ndarray:
    y, x = np.mgrid[0:h, 0:w]
    checker = ((x // 40 + y // 40) % 2).astype(np.uint8) * 160
    r = (x / w * 255).astype(np.uint8)
    g = (y / h * 255).astype(np.uint8)
    img = np.stack([checker, g, r], axis=2)
    cv2.putText(img, "Guibbon demo", (20, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    return img


_BASE: np.ndarray = _make_base_image()


# ---------------------------------------------------------------------------
# App definition
# ---------------------------------------------------------------------------


class ImageFilterApp(InteractiveImageAppBase):
    """Interactive image filter demo using InteractiveImageAppBase (Pattern 3)."""

    @guibbon.params
    class Params:
        kernel_size: int = SliderDescriptor(
            values=list(range(1, 32, 2)),   # 1, 3, 5, …, 31
            default=5,
            on_drag=True,
            on_release=True,
        )
        filter: str = RadioDescriptor(
            options=["original", "blur", "sharpen", "edges", "emboss"],
            default="blur",
        )

    def on_change(self, params, modified_descriptors):
        k = max(1, int(params.kernel_size))
        if k % 2 == 0:
            k += 1

        # During a drag: show a cheap downsampled preview to feel responsive.
        is_drag = any("on_drag" in md for md in modified_descriptors)
        src = _BASE
        if is_drag:
            src = cv2.resize(src, (src.shape[1] // 2, src.shape[0] // 2))

        f = str(params.filter)
        if f == "original":
            result = src.copy()
        elif f == "blur":
            result = cv2.GaussianBlur(src, (k, k), 0)
        elif f == "sharpen":
            blurred = cv2.GaussianBlur(src, (k, k), 0)
            result = cv2.addWeighted(src, 2.0, blurred, -1.0, 0)
        elif f == "edges":
            gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            result = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        elif f == "emboss":
            kernel = np.array([[-2, -1, 0],
                                [-1,  1, 1],
                                [ 0,  1, 2]], dtype=np.float32)
            gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            embossed = cv2.filter2D(gray, -1, kernel) + 128
            result = cv2.cvtColor(embossed.astype(np.uint8), cv2.COLOR_GRAY2BGR)
        else:
            result = src.copy()

        # On drag: upscale preview back to original size so the viewer doesn't
        # change canvas dimensions between drag and release.
        if is_drag:
            result = cv2.resize(result, (_BASE.shape[1], _BASE.shape[0]))

        return result


if __name__ == "__main__":
    print("Pattern 3: InteractiveImageAppBase — slider and radio adjust the image filter.")
    print("Close the window to exit.\n")
    ImageFilterApp(
        refresh_rate=60,
        title="Guibbon — Pattern 3 image filter",
        viewer_height=480,
        viewer_width=640,
        viewer_mode="fit",
    ).run()
