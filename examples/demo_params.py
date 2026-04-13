"""
Demo: @guibbon.params decorator with GetPath support.

Run with:
    uv run python -m guibbon.examples.demo_params
"""

import guibbon
from dataclasses import field
from guibbon import GetPath, SliderDescriptor, RadioDescriptor


# ── Define nested params ──────────────────────────────────────────────────

@guibbon.params
class Resolution:
    width:  int = SliderDescriptor(values=list(range(1, 1025)), default=512)
    height: int = SliderDescriptor(values=list(range(1, 1025)), default=768)


@guibbon.params
class Params:
    sigma:      float = SliderDescriptor(values=[0.1, 0.5, 1.0, 2.0, 5.0], default=1.0)
    mode:       str   = RadioDescriptor(options=["blur", "sharpen"], default="blur")
    resolution: Resolution = field(default_factory=Resolution)


# ── Create an instance ────────────────────────────────────────────────────

params = Params()

# ── IDE autocompletion works — these are real typed fields ─────────────────

print("=== Field values (real types) ===")
print(f"  sigma  = {params.sigma}   isinstance(float)? {isinstance(params.sigma, float)}")
print(f"  mode   = {params.mode!r}  isinstance(str)?   {isinstance(params.mode, str)}")
print(f"  width  = {params.resolution.width}   isinstance(int)?   {isinstance(params.resolution.width, int)}")
print(f"  height = {params.resolution.height}   isinstance(int)?   {isinstance(params.resolution.height, int)}")

# ── GetPath — refactor-safe path reconstruction ───────────────────────────

print("\n=== GetPath (parent chain) ===")
print(f"  GetPath(params.sigma)             = {GetPath(params.sigma)!r}")
print(f"  GetPath(params.mode)              = {GetPath(params.mode)!r}")
print(f"  GetPath(params.resolution)        = {GetPath(params.resolution)!r}")
print(f"  GetPath(params.resolution.width)  = {GetPath(params.resolution.width)!r}")
print(f"  GetPath(params.resolution.height) = {GetPath(params.resolution.height)!r}")

# ── Descriptor metadata lives on the CLASS ────────────────────────────────

print("\n=== Descriptors (on class) ===")
print(f"  Params descriptors:      {list(Params.__guibbon_descriptors__.keys())}")
print(f"  Resolution descriptors:  {list(Resolution.__guibbon_descriptors__.keys())}")

slider = Resolution.__guibbon_descriptors__["width"]
print(f"  Width slider range: {slider.values[0]}..{slider.values[-1]}")

# ── Simulated callback with modified_descriptors ──────────────────────────

print("\n=== Simulated callback ===")
modified_descriptors = ["sigma.on_drag", "resolution.width.on_release"]

for md in modified_descriptors:
    print(f"  triggered: {md}")

if any("on_drag" in md for md in modified_descriptors):
    print("  → preview mode (something is being dragged)")
if "resolution.width.on_release" in modified_descriptors:
    print(f"  → width finalized at {params.resolution.width}")
