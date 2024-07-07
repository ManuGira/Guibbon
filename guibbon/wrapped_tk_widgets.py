import tkinter as tk


class Entry(tk.Widget, tk.XView):
    def __init__(self, master, on_change_callback=None, on_return_callback=None):
        # super().__init__(master=master, widgetName="entry")
        self.on_change_callback = (lambda x: None) if on_change_callback is None else on_change_callback
        self.on_return_callback = (lambda x: None) if on_return_callback is None else on_return_callback

        # Tcl doc about validatecommand: https://tcl-lang.org/man/tcl8.6/TkCmd/ttk_entry.htm#M34
        # self.zoom_text = tk.StringVar()
        self.text_var = tk.StringVar()

        cnf = {"textvariable": self.text_var}
        if on_change_callback is not None:
            vcmd = master.register(self._on_change_callback)
            cnf["validate"] = "all"
            cnf["validatecommand"] = (vcmd, "%P")

        self.entry = tk.Entry(master=master, cnf=cnf)
        self.entry.bind('<Return>', self._on_return_callback)

    def pack(self, cnf=None, **kw):
        if cnf is None:
            cnf = {}

        self.entry.pack(cnf, **kw)

    def set(self, text: str):
        self.text_var.set(text)

    def get(self):
        return self.text_var.get()

    def _on_change_callback(self, text):
        self.on_change_callback(text)
        return True

    def _on_return_callback(self, event: tk.Event):
        # focus out by giving focus to the next item
        self.entry.tk_focusNext().focus()
        self.on_return_callback(self.text_var.get())
