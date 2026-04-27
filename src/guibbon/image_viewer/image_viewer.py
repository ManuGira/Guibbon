"""ImageViewer component: canvas with pan, zoom, and overlay support.

cv2.warpPerspective is used for high-quality image transformation (zoom,
interpolation).  PIL/Pillow is used only to convert numpy arrays to
Tk-compatible PhotoImage objects — it performs no image processing.

Usage::

    viewer = ImageViewer(height=480, width=640)
    viewer.set_image(bgr_array)   # HxWxC uint8 BGR (cv2 format)
    viewer.build(parent_frame)    # parent_frame is a tk.Frame

After ``build()``, the canvas is embedded inside *parent_frame* and the
viewer responds to mouse wheel zoom and right-click drag pan.
"""

from __future__ import annotations

import math
from typing import Any

import cv2
import numpy as np
import numpy.typing as npt
from PIL import Image, ImageTk


# ---------------------------------------------------------------------------
# Private: 3×3 homogeneous transform matrix helpers (pure, testable)
# ---------------------------------------------------------------------------

_Matrix = npt.NDArray[np.float64]


def _identity() -> _Matrix:
    """Return a 3×3 identity matrix."""
    return np.eye(3, dtype=np.float64)


def _translation(tx: float, ty: float) -> _Matrix:
    """Return a 3×3 homogeneous translation matrix."""
    m = np.eye(3, dtype=np.float64)
    m[0, 2] = tx
    m[1, 2] = ty
    return m


def _scale(sx: float, sy: float) -> _Matrix:
    """Return a 3×3 homogeneous scale matrix."""
    m = np.eye(3, dtype=np.float64)
    m[0, 0] = sx
    m[1, 1] = sy
    return m


def _apply(mat: _Matrix, x: float, y: float) -> tuple[float, float]:
    """Apply a homogeneous 3×3 matrix to a 2-D point."""
    p = mat @ np.array([x, y, 1.0], dtype=np.float64)
    p /= p[2]
    return float(p[0]), float(p[1])


def _inv(mat: _Matrix) -> _Matrix:
    """Invert a 3×3 homogeneous matrix."""
    return np.linalg.inv(mat).astype(np.float64)


# ---------------------------------------------------------------------------
# Private: mouse pan state machine (pure, testable)
# ---------------------------------------------------------------------------


class _MousePan:
    """Accumulates drag delta from mouse press / motion / release events.

    Args:
        button_num: Tkinter button number to listen to (e.g. 3 for right-click).
    """

    def __init__(self, button_num: int) -> None:
        self._button_num = button_num
        self._is_down = False
        self._p0: tuple[float, float] = (0.0, 0.0)
        self._p1: tuple[float, float] = (0.0, 0.0)

    @property
    def is_down(self) -> bool:
        """True while the tracked button is held down."""
        return self._is_down

    @property
    def delta_xy(self) -> tuple[float, float]:
        """Current drag delta (p1 − p0) in image space."""
        return self._p1[0] - self._p0[0], self._p1[1] - self._p0[1]

    def on_press(self, button: int, img_x: float, img_y: float) -> bool:
        """Record start of drag.  Returns True if this button is consumed."""
        if button == self._button_num:
            self._is_down = True
            self._p0 = (img_x, img_y)
            self._p1 = (img_x, img_y)
            return True
        return False

    def on_motion(self, img_x: float, img_y: float) -> None:
        """Update current drag position (only active while button is down)."""
        if self._is_down:
            self._p1 = (img_x, img_y)

    def on_release(self, button: int) -> bool:
        """End drag.  Returns True if this button is consumed."""
        if self._is_down and button == self._button_num:
            self._is_down = False
            return True
        return False


# ---------------------------------------------------------------------------
# Public: ImageViewer
# ---------------------------------------------------------------------------


class ImageViewer:
    """Image display component with pan, zoom, and overlay support.

    Implements the ``build(parent)`` contract (compatible with
    :class:`~guibbon.core.buildable.BuildableWidget`): call ``build(parent)``
    to embed the canvas and toolbar inside an existing ``tk.Frame``.

    Image processing is performed by **cv2**:

    - :func:`cv2.warpPerspective` applies the pan+zoom transform with the
      specified interpolation method.
    - :func:`cv2.cvtColor` converts between colour spaces.

    **Pillow** is used only as a bridge from numpy to ``ImageTk.PhotoImage``;
    it performs no image processing.

    Args:
        height: Canvas height in pixels (default 480).
        width:  Canvas width  in pixels (default 640).
        mode:   Initial zoom mode — ``"fit"`` (default), ``"fill"``, or
                ``"100"`` (1:1 pixels).
        interpolation: cv2 interpolation flag for warpPerspective
                       (default :data:`cv2.INTER_LINEAR`).

    Example::

        viewer = ImageViewer(height=480, width=640)
        viewer.set_image(bgr_array)
        viewer.build(parent_frame)
    """

    _RIGHT_BUTTON = 3  # Tkinter right-click button number

    def __init__(
        self,
        height: int = 720,
        width: int = 720,
        mode: str = "fit",
        interpolation: int | None = None,
    ) -> None:
        if mode not in ("fit", "fill", "100"):
            raise ValueError(f"mode must be 'fit', 'fill', or '100'; got {mode!r}")
        self._canvas_h = height
        self._canvas_w = width
        self._mode = mode
        self._interpolation: int = cv2.INTER_LINEAR if interpolation is None else interpolation

        # Image state (populated by set_image)
        self._img_rgb: np.ndarray | None = None

        # Pan / zoom state
        self._zoom_factor: float = 1.0
        self._pan_xy: tuple[float, float] = (0.0, 0.0)
        self._cumulative_pan_xy: tuple[float, float] = (0.0, 0.0)
        self._img2can: _Matrix = _identity()
        self._can2img: _Matrix = _identity()

        self._mouse_pan = _MousePan(self._RIGHT_BUTTON)

        # need_update flag (set by overlay interactions in future phases)
        self._need_update: bool = False

        # Tk widgets — populated in build()
        self._canvas: Any = None
        self._imgtk: Any = None
        self._zoom_var: Any = None
        self._zoom_entry: Any = None
        self._panzoom_var: Any = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def need_update(self) -> bool:
        """True if an overlay interaction requires an app refresh."""
        return self._need_update

    @need_update.setter
    def need_update(self, value: bool) -> None:
        self._need_update = value

    def set_image(self, img: np.ndarray) -> None:
        """Set the image to display.

        Can be called before or after :meth:`build`.  When called after build,
        the canvas is refreshed immediately.

        Args:
            img: Numpy array in one of the following formats:

                - HxWx3 uint8 BGR (cv2 default)
                - HxWx4 uint8 BGRA
                - HxW   uint8 grayscale
                - Any of the above as float32/float64 in the range [0, 1]
        """
        if img.dtype in (np.float32, np.float64):
            img = (np.clip(img, 0.0, 1.0) * 255).astype(np.uint8)

        if img.ndim == 2:
            # Grayscale → RGB
            self._img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[2] == 4:
            # BGRA → RGB
            self._img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        else:
            # BGR → RGB
            self._img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if self._canvas is not None:
            self._init_panzoom()
            self._draw()

    def add_descriptor(self, descriptor: Any) -> None:
        """Register an overlay descriptor.

        Interactive overlay descriptor support (InteractivePointDescriptor,
        etc.) is reserved for a future phase.  This method is a no-op until
        those descriptors are implemented.
        """
        pass  # reserved for Phase 2+ interactive overlays

    def build(self, parent: Any) -> None:
        """Embed the canvas and toolbar inside *parent*.

        Args:
            parent: A ``tk.Frame`` (or any Tk container widget).
        """
        import tkinter as tk

        frame = tk.Frame(master=parent)
        frame.pack(fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(
            master=frame,
            height=self._canvas_h,
            width=self._canvas_w,
            bg="gray10",
        )
        self._canvas.pack(side=tk.TOP)

        # Toolbar
        toolbar = tk.Frame(master=frame)
        btn_cfg: dict[str, Any] = {"side": tk.LEFT, "padx": 1, "pady": 2}
        tk.Button(master=toolbar, text="home", command=self._onclick_home).pack(**btn_cfg)
        tk.Button(master=toolbar, text="fit", command=self._onclick_fit).pack(**btn_cfg)
        tk.Button(master=toolbar, text="fill", command=self._onclick_fill).pack(**btn_cfg)
        tk.Button(master=toolbar, text="100%", command=self._onclick_100).pack(**btn_cfg)

        self._zoom_var = tk.StringVar()
        vcmd = toolbar.register(self._on_zoom_entry_change)
        self._zoom_entry = tk.Entry(
            master=toolbar,
            textvariable=self._zoom_var,
            width=8,
            validate="all",
            validatecommand=(vcmd, "%P"),
        )
        self._zoom_entry.pack(**btn_cfg)
        self._zoom_entry.bind("<FocusOut>", self._on_zoom_entry_focus_out)
        tk.Label(master=toolbar, text="%").pack(**btn_cfg)

        self._panzoom_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            master=toolbar,
            text="mouse pan/zoom",
            variable=self._panzoom_var,
            onvalue=True,
            offvalue=False,
        ).pack(**btn_cfg)

        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Bind canvas mouse events
        self._canvas.bind("<Motion>", self._on_tk_event)
        self._canvas.bind("<ButtonPress>", self._on_tk_event)
        self._canvas.bind("<ButtonRelease>", self._on_tk_event)
        self._canvas.bind("<MouseWheel>", self._on_tk_event)

        if self._img_rgb is not None:
            self._init_panzoom()
            self._draw()

    def wait(self, timeout_ms: int = 0) -> None:
        """Stand-alone blocking display (Pattern 1 — simple show/wait).

        Creates a Tk root window, builds the viewer into it, and blocks until
        the window is closed (``timeout_ms=0``) or the timeout elapses.

        Call :meth:`set_image` before or after :meth:`wait`; the image is
        rendered as soon as the canvas is ready.

        Must **not** be called after :meth:`build`.

        Args:
            timeout_ms: Milliseconds to keep the window open.  ``0`` (default)
                        means block indefinitely until the user closes it.

        Raises:
            RuntimeError: If the viewer has already been embedded via
                          :meth:`build`.

        Example::

            viewer = ImageViewer()
            viewer.set_image(bgr_array)
            viewer.wait(0)  # blocks until window is closed
        """
        import tkinter as tk

        if self._canvas is not None:
            raise RuntimeError(
                "wait() cannot be called after build(); "
                "use build() to embed the viewer in an existing window."
            )
        root = tk.Tk()
        root.title("Guibbon — image viewer")
        root.resizable(False, False)
        self.build(root)
        if timeout_ms > 0:
            root.after(timeout_ms, root.destroy)
        root.mainloop()

    # ------------------------------------------------------------------
    # Private: pan / zoom logic (testable without Tk)
    # ------------------------------------------------------------------

    def _init_panzoom(self) -> None:
        """Reset pan and compute initial zoom factor from the chosen mode."""
        if self._img_rgb is None:
            return
        imgh, imgw = self._img_rgb.shape[:2]
        canh, canw = self._canvas_h, self._canvas_w
        if self._mode == "fit":
            self._zoom_factor = min(canh / imgh, canw / imgw)
        elif self._mode == "fill":
            self._zoom_factor = max(canh / imgh, canw / imgw)
        else:  # "100"
            self._zoom_factor = 1.0
        self._pan_xy = (0.0, 0.0)
        self._cumulative_pan_xy = (0.0, 0.0)

    def _update_transform(self) -> None:
        """Recompute img→canvas and canvas→img matrices from current state."""
        if self._img_rgb is None:
            return
        imgh, imgw = self._img_rgb.shape[:2]
        canh, canw = self._canvas_h, self._canvas_w
        # Map image centre → apply pan → apply zoom → map to canvas centre
        self._img2can = (
            _translation(canw / 2, canh / 2)
            @ _scale(self._zoom_factor, self._zoom_factor)
            @ _translation(self._pan_xy[0], self._pan_xy[1])
            @ _translation(-imgw / 2, -imgh / 2)
        )
        self._can2img = _inv(self._img2can)

    def _draw(self) -> None:
        """Warp image and display on the Tk canvas."""
        if self._img_rgb is None or self._canvas is None:
            return
        self._update_transform()

        canh, canw = self._canvas_h, self._canvas_w
        # cv2.warpPerspective dsize is (width, height)
        warped = cv2.warpPerspective(
            self._img_rgb,
            self._img2can,
            dsize=(canw, canh),
            flags=self._interpolation,
        )

        # PIL used only as numpy → Tk PhotoImage bridge (no image processing)
        pil_img = Image.fromarray(warped)
        self._imgtk = ImageTk.PhotoImage(image=pil_img, master=self._canvas)
        self._canvas.create_image(canw // 2, canh // 2, anchor="center", image=self._imgtk)

        # Update zoom entry (skip if user is currently typing)
        if self._zoom_var is not None:
            self._zoom_var.set(f"{self._zoom_factor * 100:.2f}")

    def _handle_zoom(self, event: Any, img_x: float, img_y: float) -> None:
        """Apply mouse-wheel zoom centred on the cursor position.

        The image pixel under the cursor stays fixed after zoom.
        """
        step = 0.2
        ctrl_held = bool(event.state & 0x0004)
        boost = 4 if ctrl_held else 1
        zoom_gain = 2.0 ** math.copysign(step * boost, event.delta)

        if self._img_rgb is None:
            return

        imgh, imgw = self._img_rgb.shape[:2]
        # Image-space coordinate that appears at canvas centre before zoom
        canvas_center_x = imgw / 2 - self._pan_xy[0]
        canvas_center_y = imgh / 2 - self._pan_xy[1]
        # Vector from cursor to canvas centre (image space)
        c2m_x = canvas_center_x - img_x
        c2m_y = canvas_center_y - img_y

        self._pan_xy = (
            self._pan_xy[0] - c2m_x * (1 - zoom_gain),
            self._pan_xy[1] - c2m_y * (1 - zoom_gain),
        )
        self._cumulative_pan_xy = self._pan_xy
        self._zoom_factor *= zoom_gain
        self._draw()

    def _on_zoom_entry_change(self, text: str) -> bool:
        """Tk validate-command callback — fires on every keystroke in zoom entry."""
        try:
            zoom_pct = float(text)
        except ValueError:
            return True
        self._zoom_factor = zoom_pct / 100.0
        self._draw()
        return True

    def _on_zoom_entry_focus_out(self, event: Any) -> None:
        pass  # zoom_var is refreshed on next draw

    # ------------------------------------------------------------------
    # Private: Tk event dispatcher
    # ------------------------------------------------------------------

    def _on_tk_event(self, event: Any) -> None:
        """Route Tkinter canvas events to pan/zoom handlers."""
        import tkinter as tk

        is_wheel = event.type == tk.EventType.MouseWheel
        is_press = event.type == tk.EventType.ButtonPress
        is_release = event.type == tk.EventType.ButtonRelease
        is_motion = event.type == tk.EventType.Motion

        can_x, can_y = float(event.x), float(event.y)
        img_x, img_y = _apply(self._can2img, can_x, can_y)

        panzoom_on = self._panzoom_var is not None and self._panzoom_var.get()
        if not panzoom_on:
            return

        if is_wheel:
            self._handle_zoom(event, img_x, img_y)
        elif is_press:
            self._mouse_pan.on_press(event.num, img_x, img_y)
        elif is_motion:
            prev_pan = self._pan_xy
            self._mouse_pan.on_motion(img_x, img_y)
            if self._mouse_pan.is_down:
                dx, dy = self._mouse_pan.delta_xy
                self._pan_xy = (
                    self._cumulative_pan_xy[0] + dx,
                    self._cumulative_pan_xy[1] + dy,
                )
                if self._pan_xy != prev_pan:
                    self._draw()
        elif is_release:
            if self._mouse_pan.on_release(event.num):
                self._cumulative_pan_xy = self._pan_xy

    # ------------------------------------------------------------------
    # Private: toolbar button callbacks
    # ------------------------------------------------------------------

    def _onclick_fit(self) -> None:
        if self._img_rgb is None:
            return
        imgh, imgw = self._img_rgb.shape[:2]
        canh, canw = self._canvas_h, self._canvas_w
        self._zoom_factor = min(canh / imgh, canw / imgw)
        self._pan_xy = (0.0, 0.0)
        self._cumulative_pan_xy = (0.0, 0.0)
        self._draw()

    def _onclick_fill(self) -> None:
        if self._img_rgb is None:
            return
        imgh, imgw = self._img_rgb.shape[:2]
        canh, canw = self._canvas_h, self._canvas_w
        self._zoom_factor = max(canh / imgh, canw / imgw)
        self._pan_xy = (0.0, 0.0)
        self._cumulative_pan_xy = (0.0, 0.0)
        self._draw()

    def _onclick_100(self) -> None:
        self._zoom_factor = 1.0
        self._pan_xy = (0.0, 0.0)
        self._cumulative_pan_xy = (0.0, 0.0)
        self._draw()

    def _onclick_home(self) -> None:
        self._init_panzoom()
        self._draw()
