# Guibbon with U
![Tests](https://github.com/ManuGira/Guibbon/actions/workflows/tests.yml/badge.svg)

The TkInter wrapper that mimics the HighGUI of OpenCV

## User Installation
This package is not hosted on PyPl, but you can still install this repo as a package with pip:
```
pip install git+https://github.com/ManuGira/Guibbon.git@master
```
## Development 

The project is configureed in `pyproject.toml`. It contains dependecies, and configs for continuous integration.

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

## TODO

#### Image Viewer
* **Feature**: Handle double clicks
* **Feature**: Handle **param** field of mouse callback
* **Feature**: Scroll delta is missing
* **Feature**: Linux and Mac support

#### Demos
* **Feature**: Make sure that the failing demo also fails with cv2

#### Interactive Overlays
* **Feature**: Make sure that the failing demo also fails with cv2


## Documentation

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

#### TkInter hierarchy
* Guibbon.root: *static Tk*
  * guibbon.window: *TopLevel*
    * tkcv2.frame: *Frame*
      * tkcv2.ctrl_frame: *Frame*
        * controller: *Frame*
        * controller: *Frame*
        * ...
      * tkcv2.image_viewer.canvas: *Canvas*
        * tkcv2.image_viewer.imgtk: *PIL.ImageTk*
