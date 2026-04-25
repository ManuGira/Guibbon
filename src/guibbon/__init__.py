"""Guibbon: GUI framework for scientific image parameter exploration.

Guibbon provides:
  - Parameter binding via @guibbon.params decorator
  - Descriptor-based widgets (sliders, radio buttons, overlays)
  - Interactive image viewer with custom overlays
  - Controller components for parameter manipulation
  - Preview mode support for interactive exploration
  - 100% testable non-GUI code

Usage:
    import guibbon
    from guibbon import SliderDescriptor, RadioDescriptor, GetPath

    @guibbon.params
    class Params:
        size: int = SliderDescriptor(values=range(1, 11), default=5)
"""

from .controller import RadioDescriptor, SliderDescriptor
from .core.descriptor import (
    BuildableDescriptor,
    Descriptor,
)
from .core.params import (
    GetPath,
    params,
)

__version__ = "2.0.0-dev"
__all__ = [
    "params",
    "GetPath",
    "Descriptor",
    "BuildableDescriptor",
    "SliderDescriptor",
    "RadioDescriptor",
]
