"""Guibbon controller component: parameter controls (sliders, radio buttons, …).

Public API:
    Controller       — component that assembles control widgets from params
    SliderDescriptor — descriptor backed by a slider widget
    RadioDescriptor  — descriptor backed by radio buttons / dropdown
"""

from .controller import Controller
from .radio import RadioDescriptor
from .slider import SliderDescriptor

__all__ = [
    "Controller",
    "SliderDescriptor",
    "RadioDescriptor",
]
