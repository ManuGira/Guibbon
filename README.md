# Tk4Cv2
![Tests](https://github.com/ManuGira/Tk4Cv2/actions/workflows/tests.yml/badge.svg)

The TkInter wrapper that mimics the HighGUI of OpenCV

## User Installation
This package is not hosted on PyPl, but you can still install this repo as a package with pip:
```
pip install git+https://github.com/ManuGira/Tk4Cv2.git@master
```
## Development
If you forked this repo, the following commands will be your new friends.  

### Dev Installation
Install development requirements:
```
$ pip install -r requirements_dev.txt
```
Install this package in editable mode:
```
$ pip install -e .
```
### Continuous Integration
#### Testing with pytest
Configured in `pyproject.toml`  
Run tests and generate coverage report:
```
$ pytest 
```
#### Type checking with mypy
Configured in `pyproject.toml`  
Run it with:
```
$ mypy .
```
#### Lintering with ruff
Configured in `pyproject.toml`  
Linter check:
```
$ ruff check .
```
Linter fix:
```
$ ruff check --fix .
```
#### CI Launched with tox
Configured in `tox.ini`
All of the above (except Linter fix):
```
$ tox
```

## TODO

* **Bug**: Closing the windows doesn't kill all threads

#### Image Viewer
* **Feature**: Handle double clicks
* **Feature**: Handle **param** field of mouse callback
* **Feature**: Scroll delta is missing
* **Feature**: Linux and Mac support

#### Demos
* **Feature**: Make sure that the failing demo also fails with cv2

#### Interactive Overlays
* **Feature**: Labels


## Documentation

#### Class hierarchy
* Tk4Cv2
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
* Tk4Cv2.root: *static Tk*
  * tk4cv2.window: *TopLevel*
    * tkcv2.frame: *Frame*
      * tkcv2.ctrl_frame: *Frame*
        * controller: *Frame*
        * controller: *Frame*
        * ...
      * tkcv2.image_viewer.canvas: *Canvas*
        * tkcv2.image_viewer.imgtk: *PIL.ImageTk*
