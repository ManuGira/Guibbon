"""Tests for image_viewer.py — non-GUI logic only.

All tests exercise pure functions and the non-rendering parts of ImageViewer.
The build() / draw() / _on_tk_event() code paths require Tkinter and are
explicitly excluded from this test suite (they are integration-tested manually
via examples/).
"""

from __future__ import annotations


import cv2
import numpy as np
import pytest

from guibbon.image_viewer.image_viewer import (
    ImageViewer,
    _MousePan,
    _apply,
    _identity,
    _inv,
    _scale,
    _translation,
)


# ===========================================================================
# Transform matrix helpers
# ===========================================================================


class TestIdentity:
    def test_shape(self):
        m = _identity()
        assert m.shape == (3, 3)

    def test_dtype(self):
        assert _identity().dtype == np.float64

    def test_is_identity(self):
        np.testing.assert_array_equal(_identity(), np.eye(3, dtype=np.float64))


class TestTranslation:
    def test_moves_point(self):
        m = _translation(5.0, 3.0)
        x, y = _apply(m, 0.0, 0.0)
        assert x == pytest.approx(5.0)
        assert y == pytest.approx(3.0)

    def test_zero_translation_is_identity(self):
        m = _translation(0.0, 0.0)
        np.testing.assert_array_almost_equal(m, _identity())


class TestScale:
    def test_scales_point(self):
        m = _scale(2.0, 3.0)
        x, y = _apply(m, 1.0, 1.0)
        assert x == pytest.approx(2.0)
        assert y == pytest.approx(3.0)

    def test_unit_scale_is_identity(self):
        m = _scale(1.0, 1.0)
        np.testing.assert_array_almost_equal(m, _identity())


class TestApply:
    def test_identity_returns_same_point(self):
        x, y = _apply(_identity(), 7.5, -3.2)
        assert x == pytest.approx(7.5)
        assert y == pytest.approx(-3.2)

    def test_composed_translate_and_scale(self):
        # T(1, 2) @ S(2, 2) maps (1, 1) → scale → (2, 2) → translate → (3, 4)
        m = _translation(1.0, 2.0) @ _scale(2.0, 2.0)
        x, y = _apply(m, 1.0, 1.0)
        assert x == pytest.approx(3.0)
        assert y == pytest.approx(4.0)


class TestInv:
    def test_inv_of_translation(self):
        m = _translation(10.0, -5.0)
        m_inv = _inv(m)
        x, y = _apply(m_inv @ m, 3.0, 7.0)
        assert x == pytest.approx(3.0)
        assert y == pytest.approx(7.0)

    def test_inv_of_scale(self):
        m = _scale(4.0, 2.0)
        m_inv = _inv(m)
        composed = m_inv @ m
        np.testing.assert_array_almost_equal(composed, _identity())


# ===========================================================================
# _MousePan state machine
# ===========================================================================


class TestMousePan:
    def test_initial_state(self):
        mp = _MousePan(button_num=3)
        assert mp.is_down is False
        assert mp.delta_xy == (0.0, 0.0)

    def test_press_correct_button_activates(self):
        mp = _MousePan(3)
        consumed = mp.on_press(3, 10.0, 20.0)
        assert consumed is True
        assert mp.is_down is True
        assert mp.delta_xy == (0.0, 0.0)

    def test_press_wrong_button_ignored(self):
        mp = _MousePan(3)
        consumed = mp.on_press(1, 10.0, 20.0)
        assert consumed is False
        assert mp.is_down is False

    def test_motion_updates_delta(self):
        mp = _MousePan(3)
        mp.on_press(3, 10.0, 20.0)
        mp.on_motion(15.0, 25.0)
        assert mp.delta_xy == pytest.approx((5.0, 5.0))

    def test_motion_ignored_when_not_down(self):
        mp = _MousePan(3)
        mp.on_motion(15.0, 25.0)
        assert mp.delta_xy == (0.0, 0.0)

    def test_release_deactivates(self):
        mp = _MousePan(3)
        mp.on_press(3, 10.0, 20.0)
        consumed = mp.on_release(3)
        assert consumed is True
        assert mp.is_down is False

    def test_release_wrong_button_ignored(self):
        mp = _MousePan(3)
        mp.on_press(3, 10.0, 20.0)
        consumed = mp.on_release(1)
        assert consumed is False
        assert mp.is_down is True

    def test_release_when_not_down(self):
        mp = _MousePan(3)
        consumed = mp.on_release(3)
        assert consumed is False

    def test_delta_after_release(self):
        """delta_xy keeps last p1 after release (reset only on next press)."""
        mp = _MousePan(3)
        mp.on_press(3, 0.0, 0.0)
        mp.on_motion(5.0, 5.0)
        mp.on_release(3)
        assert mp.delta_xy == pytest.approx((5.0, 5.0))

    def test_new_press_resets_delta(self):
        mp = _MousePan(3)
        mp.on_press(3, 0.0, 0.0)
        mp.on_motion(5.0, 5.0)
        mp.on_release(3)
        mp.on_press(3, 5.0, 5.0)
        assert mp.delta_xy == (0.0, 0.0)


# ===========================================================================
# ImageViewer.__init__
# ===========================================================================


class TestImageViewerInit:
    def test_valid_modes(self):
        for mode in ("fit", "fill", "100"):
            v = ImageViewer(mode=mode)
            assert v._mode == mode

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError, match="mode must be"):
            ImageViewer(mode="zoom")

    def test_default_mode_is_fit(self):
        v = ImageViewer()
        assert v._mode == "fit"

    def test_default_dimensions(self):
        v = ImageViewer()
        assert v._canvas_h == 480
        assert v._canvas_w == 640

    def test_custom_dimensions(self):
        v = ImageViewer(height=200, width=300)
        assert v._canvas_h == 200
        assert v._canvas_w == 300

    def test_default_interpolation_is_linear(self):
        v = ImageViewer()
        assert v._interpolation == cv2.INTER_LINEAR

    def test_custom_interpolation(self):
        v = ImageViewer(interpolation=cv2.INTER_NEAREST)
        assert v._interpolation == cv2.INTER_NEAREST

    def test_no_image_initially(self):
        v = ImageViewer()
        assert v._img_rgb is None

    def test_need_update_initially_false(self):
        v = ImageViewer()
        assert v.need_update is False

    def test_canvas_is_none_before_build(self):
        v = ImageViewer()
        assert v._canvas is None


# ===========================================================================
# ImageViewer.need_update property
# ===========================================================================


class TestNeedUpdate:
    def test_set_and_get(self):
        v = ImageViewer()
        v.need_update = True
        assert v.need_update is True

    def test_reset(self):
        v = ImageViewer()
        v.need_update = True
        v.need_update = False
        assert v.need_update is False


# ===========================================================================
# ImageViewer.set_image
# ===========================================================================


class TestSetImage:
    def _bgr(self, h: int = 10, w: int = 10) -> np.ndarray:
        return np.zeros((h, w, 3), dtype=np.uint8)

    def test_bgr_uint8_stored_as_rgb(self):
        v = ImageViewer()
        bgr = np.zeros((4, 4, 3), dtype=np.uint8)
        bgr[0, 0] = (255, 0, 0)  # blue in BGR
        v.set_image(bgr)
        assert v._img_rgb is not None
        # Blue pixel in BGR → [0, 0, 255] in RGB
        np.testing.assert_array_equal(v._img_rgb[0, 0], [0, 0, 255])

    def test_float32_normalized(self):
        v = ImageViewer()
        img = np.ones((4, 4, 3), dtype=np.float32)
        v.set_image(img)
        assert v._img_rgb is not None
        assert v._img_rgb.dtype == np.uint8
        # All-ones float BGR → all channels 255 after clamp*255
        assert v._img_rgb[0, 0, 0] == 255

    def test_float64_normalized(self):
        v = ImageViewer()
        img = np.full((4, 4, 3), 0.5, dtype=np.float64)
        v.set_image(img)
        assert v._img_rgb is not None
        assert v._img_rgb.dtype == np.uint8
        assert v._img_rgb[0, 0, 0] == 127

    def test_grayscale_converted_to_rgb(self):
        v = ImageViewer()
        gray = np.full((4, 4), 128, dtype=np.uint8)
        v.set_image(gray)
        assert v._img_rgb is not None
        assert v._img_rgb.shape == (4, 4, 3)
        np.testing.assert_array_equal(v._img_rgb[0, 0], [128, 128, 128])

    def test_bgra_alpha_stripped(self):
        v = ImageViewer()
        bgra = np.zeros((4, 4, 4), dtype=np.uint8)
        bgra[:, :, 0] = 255  # blue channel
        v.set_image(bgra)
        assert v._img_rgb is not None
        assert v._img_rgb.shape[2] == 3

    def test_image_shape_preserved(self):
        v = ImageViewer()
        img = self._bgr(20, 30)
        v.set_image(img)
        assert v._img_rgb is not None
        assert v._img_rgb.shape[:2] == (20, 30)

    def test_no_draw_before_build(self):
        """set_image should not crash when canvas is None."""
        v = ImageViewer()
        v.set_image(self._bgr())  # canvas is None — must not raise


# ===========================================================================
# ImageViewer.add_descriptor
# ===========================================================================


class TestAddDescriptor:
    def test_does_not_raise(self):
        v = ImageViewer()
        v.add_descriptor(object())  # currently a no-op

    def test_returns_none(self):
        v = ImageViewer()
        result = v.add_descriptor(object())
        assert result is None


# ===========================================================================
# ImageViewer._init_panzoom
# ===========================================================================


class TestInitPanzoom:
    def _viewer_with_image(self, imgh: int, imgw: int, canh: int, canw: int, mode: str) -> ImageViewer:
        v = ImageViewer(height=canh, width=canw, mode=mode)
        v._img_rgb = np.zeros((imgh, imgw, 3), dtype=np.uint8)
        return v

    def test_fit_limits_by_shorter_axis(self):
        # 100×200 image in 50×50 canvas → zoom = min(50/100, 50/200) = 0.25
        v = self._viewer_with_image(100, 200, 50, 50, "fit")
        v._init_panzoom()
        assert v._zoom_factor == pytest.approx(0.25)

    def test_fill_uses_larger_axis(self):
        # 100×200 image in 50×50 canvas → zoom = max(50/100, 50/200) = 0.5
        v = self._viewer_with_image(100, 200, 50, 50, "fill")
        v._init_panzoom()
        assert v._zoom_factor == pytest.approx(0.5)

    def test_100_sets_zoom_to_one(self):
        v = self._viewer_with_image(100, 200, 50, 50, "100")
        v._init_panzoom()
        assert v._zoom_factor == pytest.approx(1.0)

    def test_pan_reset_to_zero(self):
        v = self._viewer_with_image(100, 100, 50, 50, "fit")
        v._pan_xy = (5.0, 5.0)
        v._init_panzoom()
        assert v._pan_xy == (0.0, 0.0)

    def test_cumulative_pan_reset(self):
        v = self._viewer_with_image(100, 100, 50, 50, "fit")
        v._cumulative_pan_xy = (5.0, 5.0)
        v._init_panzoom()
        assert v._cumulative_pan_xy == (0.0, 0.0)

    def test_no_image_no_crash(self):
        v = ImageViewer()
        v._init_panzoom()  # img_rgb is None — must not raise


# ===========================================================================
# ImageViewer._update_transform
# ===========================================================================


class TestUpdateTransform:
    def _setup(self, imgh: int, imgw: int, canh: int, canw: int) -> ImageViewer:
        v = ImageViewer(height=canh, width=canw)
        v._img_rgb = np.zeros((imgh, imgw, 3), dtype=np.uint8)
        return v

    def test_image_centre_maps_to_canvas_centre_at_zoom1_pan0(self):
        imgh, imgw = 100, 200
        canh, canw = 80, 160
        v = self._setup(imgh, imgw, canh, canw)
        v._zoom_factor = 1.0
        v._pan_xy = (0.0, 0.0)
        v._update_transform()

        cx, cy = _apply(v._img2can, imgw / 2, imgh / 2)
        assert cx == pytest.approx(canw / 2)
        assert cy == pytest.approx(canh / 2)

    def test_can2img_is_inverse_of_img2can(self):
        v = self._setup(100, 100, 80, 80)
        v._zoom_factor = 2.0
        v._pan_xy = (5.0, -3.0)
        v._update_transform()

        composed = v._img2can @ v._can2img
        np.testing.assert_array_almost_equal(composed, _identity())

    def test_zoom_affects_scale(self):
        v = self._setup(100, 100, 100, 100)
        v._zoom_factor = 2.0
        v._pan_xy = (0.0, 0.0)
        v._update_transform()

        # Point one pixel right of image centre should map two canvas-pixels right
        cx0, _ = _apply(v._img2can, 50.0, 50.0)
        cx1, _ = _apply(v._img2can, 51.0, 50.0)
        assert cx1 - cx0 == pytest.approx(2.0)

    def test_no_image_no_crash(self):
        v = ImageViewer()
        v._update_transform()  # img_rgb is None — must not raise


# ===========================================================================
# ImageViewer._on_zoom_entry_change
# ===========================================================================


class TestOnZoomEntryChange:
    def test_valid_percentage_updates_zoom(self):
        v = ImageViewer()
        v._on_zoom_entry_change("200")
        assert v._zoom_factor == pytest.approx(2.0)

    def test_invalid_text_ignored(self):
        v = ImageViewer()
        v._zoom_factor = 1.5
        result = v._on_zoom_entry_change("abc")
        assert result is True
        assert v._zoom_factor == pytest.approx(1.5)

    def test_returns_true_always(self):
        v = ImageViewer()
        assert v._on_zoom_entry_change("50") is True
        assert v._on_zoom_entry_change("xyz") is True

    def test_zero_percentage(self):
        v = ImageViewer()
        v._on_zoom_entry_change("0")
        assert v._zoom_factor == pytest.approx(0.0)


# ===========================================================================
# ImageViewer._handle_zoom
# ===========================================================================


class _FakeWheelEvent:
    """Fake Tkinter MouseWheel event."""

    def __init__(self, delta: int, state: int = 0) -> None:
        self.delta = delta
        self.state = state


class TestHandleZoom:
    def _viewer(self) -> ImageViewer:
        v = ImageViewer(height=100, width=100)
        v._img_rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        v._zoom_factor = 1.0
        v._pan_xy = (0.0, 0.0)
        v._cumulative_pan_xy = (0.0, 0.0)
        v._update_transform()
        return v

    def test_scroll_up_increases_zoom(self):
        v = self._viewer()
        initial_zoom = v._zoom_factor
        event = _FakeWheelEvent(delta=120)
        v._handle_zoom(event, 50.0, 50.0)
        assert v._zoom_factor > initial_zoom

    def test_scroll_down_decreases_zoom(self):
        v = self._viewer()
        initial_zoom = v._zoom_factor
        event = _FakeWheelEvent(delta=-120)
        v._handle_zoom(event, 50.0, 50.0)
        assert v._zoom_factor < initial_zoom

    def test_ctrl_boosts_zoom_by_4x(self):
        v1 = self._viewer()
        v2 = self._viewer()
        no_ctrl = _FakeWheelEvent(delta=120, state=0x0000)
        with_ctrl = _FakeWheelEvent(delta=120, state=0x0004)
        v1._handle_zoom(no_ctrl, 50.0, 50.0)
        v2._handle_zoom(with_ctrl, 50.0, 50.0)
        # With ctrl the zoom exponent is 4× larger → more zoom change
        assert v2._zoom_factor > v1._zoom_factor

    def test_zoom_centred_on_canvas_centre_does_not_pan(self):
        """Zooming on the image/canvas centre should keep pan at (0, 0)."""
        v = self._viewer()
        # When pan=(0,0) and zoom=1 on a 100×100 image/canvas, the canvas centre
        # corresponds to image point (50, 50)
        event = _FakeWheelEvent(delta=120)
        v._handle_zoom(event, 50.0, 50.0)
        assert v._pan_xy == pytest.approx((0.0, 0.0))

    def test_cumulative_pan_updated(self):
        v = self._viewer()
        event = _FakeWheelEvent(delta=120)
        v._handle_zoom(event, 20.0, 30.0)
        assert v._cumulative_pan_xy == v._pan_xy

    def test_no_image_no_crash(self):
        v = ImageViewer()
        event = _FakeWheelEvent(delta=120)
        v._handle_zoom(event, 50.0, 50.0)  # img_rgb is None — must not raise


# ===========================================================================
# ImageViewer toolbar callbacks (no-Tk path)
# ===========================================================================


class TestToolbarCallbacks:
    def _viewer_with_image(self, mode: str = "fit") -> ImageViewer:
        v = ImageViewer(height=100, width=200, mode=mode)
        # 200×100 image in 100×200 canvas
        v._img_rgb = np.zeros((100, 200, 3), dtype=np.uint8)
        v._pan_xy = (5.0, 5.0)
        v._cumulative_pan_xy = (5.0, 5.0)
        v._zoom_factor = 2.0
        return v

    def test_onclick_fit_resets_pan_and_sets_fit_zoom(self):
        v = self._viewer_with_image()
        v._onclick_fit()
        assert v._pan_xy == (0.0, 0.0)
        assert v._cumulative_pan_xy == (0.0, 0.0)
        # 100×200 image in 100×200 canvas → fit zoom = min(100/100, 200/200) = 1.0
        assert v._zoom_factor == pytest.approx(1.0)

    def test_onclick_fill_resets_pan_and_sets_fill_zoom(self):
        v = self._viewer_with_image()
        v._onclick_fill()
        assert v._pan_xy == (0.0, 0.0)
        # 100×200 image in 100×200 canvas → fill zoom = max(1.0, 1.0) = 1.0
        assert v._zoom_factor == pytest.approx(1.0)

    def test_onclick_100_sets_zoom_to_one(self):
        v = self._viewer_with_image()
        v._onclick_100()
        assert v._zoom_factor == pytest.approx(1.0)
        assert v._pan_xy == (0.0, 0.0)

    def test_onclick_home_restores_mode_zoom(self):
        v = self._viewer_with_image(mode="100")
        v._zoom_factor = 5.0
        v._onclick_home()
        assert v._zoom_factor == pytest.approx(1.0)

    def test_onclick_fit_no_image_no_crash(self):
        v = ImageViewer()
        v._onclick_fit()

    def test_onclick_fill_no_image_no_crash(self):
        v = ImageViewer()
        v._onclick_fill()

    def test_onclick_100_no_image_no_crash(self):
        v = ImageViewer()
        v._onclick_100()


# ===========================================================================
# Package export
# ===========================================================================


class TestPackageExport:
    def test_image_viewer_importable_from_package(self):
        from guibbon.image_viewer import ImageViewer as IV  # noqa: F401

        assert IV is ImageViewer

    def test_image_viewer_importable_from_guibbon(self):
        import guibbon

        assert hasattr(guibbon, "ImageViewer")
        assert guibbon.ImageViewer is ImageViewer
