"""Guibbon core infrastructure.

Main exports:
  - params: Decorator for parameter classes (@guibbon.params)
  - GetPath: Reconstruct dotted paths from tracked values
  - Descriptor, BuildableDescriptor: Descriptor base classes (framework contracts)
  - _BaseDescriptor: Backward-compatible alias for Descriptor
  - BuildableWidget: Framework-agnostic widget protocol
  - App: App orchestrator (params, components, need_update, modified_descriptors)
  - HasNeedUpdate: Protocol for components with need_update property

Note: Concrete descriptors (SliderDescriptor, RadioDescriptor, …) live in their
respective component packages (e.g. guibbon.controller), not here.
"""

from .app import (
    App,
    HasNeedUpdate,
)
from .buildable import BuildableWidget
from .descriptor import (
    BuildableDescriptor,
    Descriptor,
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
    "BuildableWidget",
    "App",
    "HasNeedUpdate",
    "Descriptor",
    "BuildableDescriptor",
    "_BaseDescriptor",
    "_params_decorator",
    "_make_tracked_type",
    "_track_fields",
    "_wrap_value",
]
