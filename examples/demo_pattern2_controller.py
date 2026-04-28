"""Pattern 2 demo: ControllerAppBase — parameter panel only, no image.

Subclasses ControllerAppBase, defines a Params dataclass, and prints the
result of a small calculation every time a widget changes.

Run with:
    uv run python examples/demo_pattern2_controller.py
"""

import guibbon
from guibbon import SliderDescriptor, RadioDescriptor
from guibbon.apps import ControllerAppBase


@guibbon.params
class Params:
    value: int = SliderDescriptor(values=list(range(0, 101, 5)), default=50)
    operation: str = RadioDescriptor(
        options=["square", "double", "negate", "identity"],
        default="square",
    )


class CalculatorApp(ControllerAppBase):
    """Interactive calculator: pick a value and an operation, see the result."""

    @guibbon.params
    class Params:
        value: int = SliderDescriptor(values=list(range(0, 101, 5)), default=50)
        operation: str = RadioDescriptor(
            options=["square", "double", "negate", "identity"],
            default="square",
        )

    def on_change(self, params, modified_descriptors):
        v = int(params.value)
        op = str(params.operation)
        if op == "square":
            result = v * v
        elif op == "double":
            result = v * 2
        elif op == "negate":
            result = -v
        else:
            result = v
        trigger = f"  (triggered by: {modified_descriptors})" if modified_descriptors else ""
        print(f"  {op}({v}) = {result}{trigger}")


if __name__ == "__main__":
    print("Pattern 2: ControllerAppBase — adjust sliders and radio buttons.")
    print("Results are printed to the console. Close the window to exit.\n")
    CalculatorApp(refresh_rate=30, title="Guibbon — Pattern 2 calculator").run()
