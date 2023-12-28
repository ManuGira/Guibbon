import tkinter as tk
from tk4cv2.colors import COLORS

class RadioButtonWidget:
    def __init__(self, tk_frame, name, options, on_change):
        self.name = name
        self.options = options + []  # copy
        self.on_change = on_change
        self.frame = tk.Frame(tk_frame)
        tk.Label(self.frame, text=self.name).pack(padx=2, side=tk.TOP, anchor=tk.W)
        radioframeborder = tk.Frame(self.frame, bg=COLORS.border)
        borderwidth = 1
        radioframe = tk.Frame(radioframeborder)

        self.var = tk.IntVar()
        self.buttons_list: List[tk.Radiobutton] = []
        for i, opt in enumerate(self.options):
            rb = tk.Radiobutton(radioframe, text=str(opt), variable=self.var, value=i, command=self.callback)
            rb.pack(side=tk.TOP, anchor=tk.W)
            self.buttons_list.append(rb)
        self.buttons_list[0].select()

        radioframe.pack(padx=borderwidth, pady=borderwidth, side=tk.TOP, fill=tk.X)
        radioframeborder.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X)
        self.frame.pack(padx=4, pady=4, side=tk.TOP, fill=tk.X, expand=1)

    def get_current_selection(self):
        i = self.var.get()
        opt = self.options[i]
        return i, opt

    def select(self, index, trigger_callback=False):
        if trigger_callback:
            self.buttons_list[index].invoke()
        else:
            self.buttons_list[index].select()


    def callback(self):
        i, opt = self.get_current_selection()
        self.on_change(i, opt)

