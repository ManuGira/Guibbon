"""Guibbon core infrastructure.

Main exports:
  - params: Decorator for parameter classes (@guibbon.params)
  - GetPath: Reconstruct dotted paths from tracked values
  - Descriptor, BuildableDescriptor: Descriptor base classes
  - SliderDescriptor, RadioDescriptor: Concrete descriptor types
  - _BaseDescriptor: Backward-compatible alias for Descriptor
"""

from .descriptor import (
    BuildableDescriptor,
    Descriptor,
    RadioDescriptor,
    SliderDescriptor,
)
from .params import (
    GetPath,
    _BaseDescriptor,
    _make_tracked_type,
    _params_decorator,
    _track_fields,
    _wrap_value,
    params,
)

__all__ = [
    "params",
    "GetPath",
    "Descriptor",
    "BuildableDescriptor",
    "SliderDescriptor",
    "RadioDescriptor",
    "_BaseDescriptor",
    "_params_decorator",
    "_make_tracked_type",
    "_track_fields",
    "_wrap_value",
]
