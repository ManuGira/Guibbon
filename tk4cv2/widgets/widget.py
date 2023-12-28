import tkinter as tk
import abc


class WidgetInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, parent_frame: tk.Frame, *params):
        pass
