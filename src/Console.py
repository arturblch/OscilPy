from tkinter import ttk
from tkinter import *

import logging

class ConsoleView(ttk.Frame):
    def __init__(self, parent=None):
        ttk.Frame.__init__(self, parent)

        self.console_line = ttk.Entry(self)
        self.console = Text(self, width=30)
        self.console_scrol = ttk.Scrollbar(
            self, orient="vertical", command=self.console.yview)

        self.console_line.pack(side="top", fill="both")
        self.console.pack(side="left", fill="both", expand=True)
        self.console_scrol.pack(side="left", fill="both")

        # self.console_line.bind("<Return>", self.write)

        

    def write(self, text):
        self.console.insert(END, text + '\n')
        self.console.see(END)

class ConsoleHandler(logging.Handler):
    def __init__(self, view):
        logging.Handler.__init__(self)
        self.view = view

    def emit(self, record):
        self.view.write(self.format(record))