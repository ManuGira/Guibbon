import tkinter as tk
from typing import Callable, Optional

CallbackCheckButtonList = Callable[[list[bool]], None]


class CheckButtonListWidget:
    def __init__(self, tk_frame, name: str, options: list[str], on_change: CallbackCheckButtonList, initial_values: Optional[list[bool]] = None):
        self.name = name
        self.on_change: CallbackCheckButtonList = on_change
        if initial_values is None:
            initial_values = [False] * len(options)
        self.frame = tk.Frame(tk_frame)
        tk.Label(self.frame, text=name).pack(padx=2, side=tk.TOP, anchor=tk.W)
        checkframeborder = tk.Frame(self.frame, bg="grey")
        borderwidth = 1
        checkframe = tk.Frame(checkframeborder)

        self.vars = [tk.BooleanVar() for _ in options]

        for i, opt in enumerate(options):
            checkvar = self.vars[i]
            cb = tk.Checkbutton(checkframe, text=str(opt), variable=checkvar, onvalue=True, offvalue=False, command=self.callback)
            if initial_values[i]:
                cb.select()
            cb.pack(side=tk.TOP, anchor=tk.W)

        checkframe.pack(padx=borderwidth, pady=borderwidth, side=tk.TOP, fill=tk.X)
        checkframeborder.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X)
        self.frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)

    def callback(self):
        res = [var.get() for var in self.vars]
        self.on_change(res)

    def get_current_value(self) -> list[bool]:
        return [var.get() for var in self.vars]
