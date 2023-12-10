from typing import Any, Tuple
import tkinter as tk
import abc


class WidgetInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, master: tk.Frame, name: str, *params: Tuple[Any]):
        pass
