
# ![icon](images/icon32.png) Guibbon with U ![icon](images/icon32.png) 
![Tests](https://github.com/ManuGira/Guibbon/actions/workflows/tests.yml/badge.svg)

### High-level GUI with an API similar to the HighGUI of OpenCV. 
**If you know how to use the GUI of OpenCV, then you already know how to use Guibbon.**

It allows to display an image and add GUI controllers such as:

 - Sliders (trackbar)
 - Buttons
 - Radio buttons
 - Check boxes
 - Color picker
 - Draggable points and polygons on the displayed image
 - Any custom widget that you write in Tkinter

### Reasons why you want to use Guibbon:

 - It's fast to learn and fast to code.
 - It's using Tkinter which is natively installed in most python distributions
 - Beside Tkinter, it only has 3 dependencies: numpy, opencv-python and pillow
 - It's less than 200 KB
 - You can create your own custom widget.
 
## Release Notes
#### v0.1.6* (rolling version)
###### Features
* **Custom Icon**: The window has an icon of a smiling guibbon now
* **Set Slider Name**: Allows to change the name of a Slider Widget after its instantiation
* **Improve Color Picker UX**: Add an "Edit" button to the Color Picker Widget for better UX

###### Bug fixes
* **Float image support**: Before this fix, it was not possible to use `guibbon.imshow(...)` on an image with dtype=float 

#### v0.1.5
###### Features
 * **Monkey Patching**: Inject Guibbon's function in cv2 package (not permanantly) with `guibbon.inject(cv2)`
 * **Image Viewer**: shows image with `guibbon.imshow(...)` similarly to `cv2.imshow(...)` (can be monkey patched)
 * **WaitKeyEx**: Similar to `cv2.WaitKeyEx(...)`, it supports most of the keyboard events (can be monkey patched)
 * **Trackbar**: create and edit trackbar similarly to `cv2.createTrackbar` (can be monkey patched)
 * **Slider Widget**: Same as `cv2.trackbar` but with a more flexible signature
 * **Button Widget**: A button to trigger a callback
 * **Check Button Widget**: Single check box to get control over a boolean
 * **Check Button List Widget**: List of check boxes
 * **Radio Buttons Widget**: Set of radio buttons (also called option buttons) to get control over an enum value
 * **Color Picker Widget**: Let the user choose a color from a color palette
 * **Custom Widget**: Exposing the `guibbon.WidgetInterface` allowing you to create and add your custom widget to the right panel
 * **Interactive Point Overlay**: A draggable point on the image. The point act as a 2D slider returning you its position on the image
 * **Interactive Polygon Overlays**: A set of draggable point on the image
 * **Interactive Rectangle Overlays**: A couple of interactive points representing top-left and bottom-right corners of a rectangle
 * **Magnets for Interactive Overlays**: A point cloud that can be injected to an interactive overlay. The overlay will snap to the magnets when dragged by the user.

