"""Guibbon controller component: parameter controls (sliders, radio buttons, …).

Public API:
    SliderDescriptor — descriptor backed by a slider widget
    RadioDescriptor  — descriptor backed by radio buttons / dropdown
"""

from .radio import RadioDescriptor
from .slider import SliderDescriptor

__all__ = [
    "SliderDescriptor",
    "RadioDescriptor",
]
