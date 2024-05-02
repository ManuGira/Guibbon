
# ![icon](guibbon/icons/icon32.png) Guibbon with U ![icon](guibbon/icons/icon32.png) 
![Tests](https://github.com/ManuGira/Guibbon/actions/workflows/tests.yml/badge.svg)

High-level GUI with an API similar to the HighGUI of OpenCV. It allows to display an image and add GUI controllers such as
 - Sliders (trackbar)
 - Buttons
 - Radio buttons
 - Check boxes
 - Color picker
 - Draggable points and polygons on the displayed image
 - Any custom widget that you write in Tkinter

If you know how to use the GUI of OpenCV, then you already know how to use Guibbon. So if you just need to display an image and add a few controllers to play with parameters, this package is for you. 

Other reasons why you want to use Guibbon:
 - It's using Tkinter which is natively installed in most python distributions
 - Beside Tkinter, it only has 3 dependencies: numpy, opencv-python and pillow
 - It's less than 200 KB

More info in the [documentation](https://manugira.github.io/Guibbon/)

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

## User Installation
The [Guibbon package](https://pypi.org/project/guibbon) is hosted on PyPI, you can install the **latest stable release** with pip:
```
pip install guibbon
```
If stability is not for you, install the **rolling version** from github. You will get early access to new mkdocs**features**, **bugfixes** and **bugs**:
```
pip install git+https://github.com/ManuGira/Guibbon.git@master
```
## Development 

The project is configured in `pyproject.toml`. It contains dependecies, and configs for continuous integration.

### Dev Installation
Install development requirements with poetry:
```
$ poetry install
```
This will create a new venv for this project and install dependencies according to poetry.lock. If you prefer to manage your venv yourself, you can install with pip:
```
$ pip install -r requirements_dev.txt
$ pip install -e .  # Install this package in editable mode
``` 
All requirements files and poetry.lock have been generated with the `prepare_python.sh` script.
```
./prepare_python.sh
```

### Continuous Integration
#### Testing with pytest 
Run tests and generate coverage report:
```
$ pytest 
```
#### Type checking with mypy
Run it with:
```
$ mypy .
```
#### Lintering with ruff
Linter check:
```
$ ruff check .
```
Linter fix:
```
$ ruff check --fix .
```

### Publishing to PyPI with poetry
First, update the version number in the `pyproject.toml`  
Then build tarball and wheel:
```
$ poetry build
```
Publish to PyPI:
```
$ poetry publish -r pypi -u __token__ -p <paste the secret token here (very long string starting with "pypi-")>
```

### Publishing Documentation
The documentation is written with [mkdocs](https://www.mkdocs.org/). Documentation files are placed in folder `./build/docs/site`.  
Build documentation site for all version tag and current develop:
```
$ ./scripts/build_docs.sh
```
Once built, the documentation can be deployed on github on the page of the Guibbon's project.  
```
$ ./scripts/deploy_docs.sh
```

## TODO

#### Image Viewer
* **Feature**: Handle double clicks
* **Feature**: Handle **param** field of mouse callback
* **Feature**: Scroll delta is missing
* **Feature**: Mac support

#### Demos
* **Feature**: Make sure that the failing demo also fails with cv2

#### Interactive Overlays
* **Feature**: Make sure that the failing demo also fails with cv2

#### Class hierarchy
* Guibbon
  * keyboard_event_hander: *static KeyboardEventHandler*
  * root: *static tk.Tk*
  * self.window: *tk.Frame*
  * frame: *tk.Frame*
  * ctrl_frame: *tk.Frame*
  * image_viewer: *ImageViewer*
    * canvas: *tk.Canvas*
    * imgtk: *PIL.ImageTk*
    * interactive_overlays: *List(InteractiveOverlay)*
      * canvas*
        * circle_id: *id of canvas oval*
        * 

#### Tkinter hierarchy
* Guibbon.root: *static Tk*
  * guibbon.window: *TopLevel*
    * tkcv2.frame: *Frame*
      * tkcv2.ctrl_frame: *Frame*
        * controller: *Frame*
        * controller: *Frame*
        * ...
      * tkcv2.image_viewer.canvas: *Canvas*
        * tkcv2.image_viewer.imgtk: *PIL.ImageTk*
