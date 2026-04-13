"""Guibbon core infrastructure.

Main exports:
  - params: Decorator for parameter classes (@guibbon.params)
  - GetPath: Reconstruct dotted paths from tracked values
  - SliderDescriptor, RadioDescriptor: Concrete descriptor types
  - _BaseDescriptor: Base class for custom descriptors
"""

from .params import (
    GetPath,
    RadioDescriptor,
    SliderDescriptor,
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
    "SliderDescriptor",
    "RadioDescriptor",
    "_BaseDescriptor",
    "_params_decorator",
    "_make_tracked_type",
    "_track_fields",
    "_wrap_value",
]
