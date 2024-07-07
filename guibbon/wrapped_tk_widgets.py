import tkinter as tk


class Entry:
    def __init__(self, master, on_change=None, on_return=None):
        self.on_change = (lambda x: None) if on_change is None else on_change
        self.on_return = (lambda x: None) if on_return is None else on_return

        self.is_focus = False
        self.text_var = tk.StringVar()

        # Tcl doc about validatecommand: https://tcl-lang.org/man/tcl8.6/TkCmd/ttk_entry.htm#M34
        cnf = {
            "textvariable": self.text_var,
            "width": 8,
        }
        if on_change is not None:
            vcmd = master.register(self._on_change)
            cnf.update({
                "validate": "all",
                "validatecommand": (vcmd, "%P"),
            })

        self.entry = tk.Entry(master=master, cnf=cnf)
        self.entry.bind('<Return>', self._on_return)
        self.entry.bind("<FocusOut>", self._on_focus_out)


    def pack(self, cnf=None, **kw):
        if cnf is None:
            cnf = {}

        self.entry.pack(cnf, **kw)

    def set(self, text: str):
        self.text_var.set(text)

    def get(self):
        return self.text_var.get()

    def _on_change(self, text):
        self.on_change(text)
        self.is_focus = True
        return True

    def _on_return(self, event: tk.Event):
        # focus out by giving focus to the next item
        self.entry.tk_focusNext().focus()
        self.on_return(self.text_var.get())

    def _on_focus_out(self, event: tk.Event):
        # focus out by giving focus to the next item
        self.is_focus = False
