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

* **Bug**: Process is not stopped when windows is closed 

#### Image Viewer
* **Feature**: handle double clicks
* **Feature**: Scroll delta is missing
* **Feature**: Linux and Mac support
