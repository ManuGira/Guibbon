from typing import Any
import tkinter as tk
import abc


class WidgetInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, master: tk.Frame, name: str, *params: tuple[Any]):
        pass
