"""Pattern 1 demo: simple blocking image display.

Shows a synthetic test image in a stand-alone viewer window.
The window blocks until the user closes it (or after 10 s).

Run with:
    uv run python examples/demo_pattern1_wait.py
"""

import numpy as np
import cv2

import guibbon


def _make_image(h: int = 480, w: int = 640) -> np.ndarray:
    """Return a colourful BGR checkerboard with a centred white circle."""
    y, x = np.mgrid[0:h, 0:w]
    checker = ((x // 50 + y // 50) % 2).astype(np.uint8) * 200
    r = (x / w * 255).astype(np.uint8)
    g = (y / h * 255).astype(np.uint8)
    img = np.stack([checker, g, r], axis=2)
    # draw a white circle in the centre
    cv2.circle(img, (w // 2, h // 2), min(h, w) // 4, (255, 255, 255), 3)
    return img


if __name__ == "__main__":
    img = _make_image()

    viewer = guibbon.ImageViewer(height=480, width=640, mode="fit")
    viewer.set_image(img)

    print("Pattern 1: window will close automatically after 10 s, or close it manually.")
    viewer.wait(timeout_ms=10_000)
    print("Done.")
