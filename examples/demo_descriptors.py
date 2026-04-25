"""
Demo: descriptor system — built-in and custom descriptors.

Shows:
  - SliderDescriptor and RadioDescriptor with on_widget_change / get_triggered_descriptors
  - Writing a custom descriptor by subclassing BuildableDescriptor
  - Simulated app cycle: fire events → collect modified_descriptors → clear

Run with:
    uv run python -m examples.demo_descriptors
"""

import guibbon
from dataclasses import field
from guibbon import BuildableDescriptor, GetPath, RadioDescriptor, SliderDescriptor


# ── 1. Built-in descriptors ───────────────────────────────────────────────

print("=== Built-in descriptors ===")

size_desc = SliderDescriptor(values=range(1, 11), default=5, on_drag=True, on_release=True)
mode_desc = RadioDescriptor(options=["blur", "sharpen"], default="blur")

# Simulate a drag + release on the slider, and a mode change
size_desc.on_widget_change("drag")
size_desc.on_widget_change("drag")
size_desc.on_widget_change("release")
mode_desc.on_widget_change("change")

# Collect what fired (field paths come from @guibbon.params at runtime)
modified = (
    size_desc.get_triggered_descriptors("size")
    + mode_desc.get_triggered_descriptors("mode")
)
print(f"  modified_descriptors = {modified}")

# Pattern matching — the idiom used inside on_change callbacks
if "size.on_release" in modified:
    print("  → size finalized, run full computation")
if any("on_drag" in md for md in modified):
    print("  → something is being dragged, run preview")
if "mode.on_change" in modified:
    print("  → mode changed")

# App clears state between cycles
size_desc.triggered_callbacks.clear()
mode_desc.triggered_callbacks.clear()
print(f"  after clear: {size_desc.triggered_callbacks}")


# ── 2. Custom descriptor ──────────────────────────────────────────────────

print("\n=== Custom descriptor ===")


class ThresholdDescriptor(BuildableDescriptor):
    """Example custom descriptor: a threshold value with a single 'on_set' callback."""

    def __init__(self, low: float, high: float, default: float) -> None:
        if not (low <= default <= high):
            raise ValueError(f"default {default} must be in [{low}, {high}]")
        self.low = low
        self.high = high
        self.fire_on_set = True
        super().__init__(default)

    def on_widget_change(self, trigger_type: str) -> None:
        if trigger_type == "set" and self.fire_on_set:
            self.triggered_callbacks.append("on_set")


threshold_desc = ThresholdDescriptor(low=0.0, high=1.0, default=0.5)
threshold_desc.on_widget_change("set")
print(f"  triggered: {threshold_desc.get_triggered_descriptors('threshold')}")


# ── 3. Integration with @guibbon.params ──────────────────────────────────

print("\n=== @guibbon.params integration ===")


@guibbon.params
class Params:
    size:      int   = SliderDescriptor(values=range(1, 11), default=5, on_drag=True, on_release=True)
    mode:      str   = RadioDescriptor(options=["blur", "sharpen"], default="blur")
    threshold: float = field(default=0.5)  # plain field, no descriptor


params = Params()

print(f"  params.size      = {params.size}  (is int: {isinstance(params.size, int)})")
print(f"  params.mode      = {params.mode!r}  (is str: {isinstance(params.mode, str)})")
print(f"  params.threshold = {params.threshold}")
print(f"  GetPath(params.size) = {GetPath(params.size)!r}")
print(f"  GetPath(params.mode) = {GetPath(params.mode)!r}")

# Simulate an app cycle using descriptors from the class
size_d = Params.__guibbon_descriptors__["size"]
mode_d = Params.__guibbon_descriptors__["mode"]

size_d.on_widget_change("drag")
mode_d.on_widget_change("change")

modified = (
    size_d.get_triggered_descriptors(GetPath(params.size))
    + mode_d.get_triggered_descriptors(GetPath(params.mode))
)
print(f"\n  modified_descriptors = {modified}")

# Dynamic visibility: hide size slider when mode is "sharpen"
if "mode.on_change" in modified:
    Params.__guibbon_descriptors__["size"].is_visible = (params.mode != "sharpen")
    print(f"  size visible: {Params.__guibbon_descriptors__['size'].is_visible}")
