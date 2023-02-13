# Tk4Cv2
![Tests](https://github.com/ManuGira/Tk4Cv2/actions/workflows/tests.yml/badge.svg)
The TkInter wrapper that mimics the HighGUI of OpenCV

## Installation
This package is not hosted on PyPl, but you can still install this repo as a package with pip:
```
pip install git+https://github.com/ManuGira/Tk4Cv2.git@master
```

## Development
If you forked this repo, the following commands will be your new friends.

Install development requirements:
```
$ pip install -r requiremens_dev.txt
```
Install this package in editable mode:
```
$ pip install -e .
```
Run tests:
```
$ pytest tests 
```
Type check:
```
$ mypy .
```
Linter check:
```
$ ruff check .
```
Linter fix:
```
$ ruff check --fix .
```
All of the above (except Linter fix):
```
$ tox
```


## TODO
#### Image Viewer
* handle double clicks
* Scroll delta is missing
* Linux and Mac support
