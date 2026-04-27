"""Pattern 1: simple blocking image display.

This pattern is implemented directly on :class:`guibbon.ImageViewer`::

    import guibbon
    viewer = guibbon.ImageViewer()
    viewer.set_image(bgr_array)
    viewer.wait(0)  # 0 = block indefinitely until window is closed

No extra class is needed.  ``wait()`` creates its own Tk root window and
runs ``mainloop()``.
"""
