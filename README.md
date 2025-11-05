# ![icon](https://raw.githubusercontent.com/ManuGira/Guibbon/static/docs/images/icon32.png) Guibbon with U ![icon](https://raw.githubusercontent.com/ManuGira/Guibbon/static/docs/images/icon32.png) 
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

More info: 
  - [documentation](./docs/index.md)
  - [Release Notes](./docs/release_notes.md)
  - [Getting Started (user installation)](./docs/getting_started.md)

## Development 

The project is configured in `pyproject.toml`. It contains dependecies, and configs for continuous integration.

### Dev Installation
All development actions must be performed using uv. uv handles the project environment and there is no need to activate virtual environments manually — run tools and scripts with `uv run <command>`. The project includes uv.lock and pyproject.toml to define dependencies and the development environment. 
Use `uv run` for all development tasks described below.

#### Install uv
Follow the official installation instructions:
https://docs.astral.sh/uv/getting-started/installation/

Once installed, use `uv run <command>` for all project commands.

### Continuous Integration
All CI and local developer commands are executed through uv.
#### Testing with pytest
Run tests and generate the coverage report via uv:
```
$ uv run pytest
```
#### Type checking with mypy
Run type checks:
```
$ uv run mypy .
```
#### Lintering with ruff
Linter check:
```
$ uv run ruff check .
```
Linter fix:
```
$ uv run ruff check --fix .
```

### Publishing to PyPI
Update the version number in `pyproject.toml` and then build and publish using uv's native commands.

Build source and wheel distributions:
```
$ uv build
```

Publish to PyPI using a token:
```
$ uv publish --token <your-pypi-token>
```

Publish to PyPI test repository:
```
$ uv publish --publish-url https://test.pypi.org/legacy/ --token <your-test-pypi-token>
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
