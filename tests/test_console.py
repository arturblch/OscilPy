import pytest
from tkinter import ttk
from tkinter import *

from src.Console import ConsoleView, ConsoleHandler
from utils import LogGetter

SIZE = (650, 500)
PROGRAM_NAME = "Oscil GUI"

def test_init():
    log = LogGetter.get_logger()

    root = Tk()
    root.geometry('{}x{}'.format(*SIZE))
    root.title(PROGRAM_NAME)

    console = ConsoleView(root)
    test_btn= ttk.Button(root)
    test_btn["text"] = "TEST"
    test_btn["command"] = lambda : loging(log)
    console.pack(side="top", fill="both")
    test_btn.pack(side="top", fill="both")

    vh = ConsoleHandler(console)
    log.addHandler(vh)

    root.mainloop()

def loging(log):
    log.info("hi world")



if __name__ == '__main__':
    test_init()