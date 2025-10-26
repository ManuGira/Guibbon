import tkinter as tk
from typing import Callable

from guibbon.colors import COLORS

CallbackRadioButtons = Callable[[int, str], None]

class RadioButtonsWidget:

    def __init__(self, tk_frame, name, options, on_change: CallbackRadioButtons):
        self.name = name
        self.options = options + []  # copy
        self.on_change: CallbackRadioButtons = on_change
        self.frame = tk.Frame(tk_frame)
        tk.Label(self.frame, text=self.name).pack(padx=2, side=tk.TOP, anchor=tk.W)

        self.int_var = tk.IntVar()
        self.buttons_list: list[tk.Radiobutton] = []

        self.radioframeborder, self.buttons_list = RadioButtonsWidget._create_rb_list(self.frame, self.int_var, self.options, self.callback)

        self.frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)

    @staticmethod
    def _create_rb_list(frame: tk.Frame, int_var: tk.IntVar, options: list[str], callback: Callable[[], None]) -> tuple[tk.Frame, list[tk.Radiobutton]]:
        buttons_list = []
        radioframeborder = tk.Frame(frame, bg=COLORS.border)
        radioframe = tk.Frame(radioframeborder)
        for i, opt in enumerate(options):
            rb = tk.Radiobutton(radioframe, text=str(opt), variable=int_var, value=i, command=callback)
            rb.pack(side=tk.TOP, anchor=tk.W)
            buttons_list.append(rb)
        buttons_list[0].select()
        borderwidth = 1
        radioframe.pack(padx=borderwidth, pady=borderwidth, side=tk.TOP, fill=tk.X)
        radioframeborder.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X)
        return radioframeborder, buttons_list

    def callback(self):
        i, opt = self.get_current_selection()
        self.on_change(i, opt)

    def get_current_selection(self):
        i = self.int_var.get()
        opt = self.options[i]
        return i, opt

    def select(self, index, trigger_callback=False):
        if trigger_callback:
            self.buttons_list[index].invoke()
        else:
            self.buttons_list[index].select()

    def get_options_list(self):
        return self.options + []

    def set_options_list(self, new_options: list[str]):
        if len(new_options) == len(self.options):
            for rb, opt in zip(self.buttons_list, new_options):
                rb.config(text=opt)
        else:
            self.radioframeborder.destroy()
            self.radioframeborder, self.buttons_list = RadioButtonsWidget._create_rb_list(self.frame, self.int_var, new_options, self.callback)
        self.options = new_options + []
