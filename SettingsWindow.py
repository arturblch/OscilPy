import tkinter as tk
from tkinter import Toplevel, Label, Entry, Frame

class Settings(Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.body()
        self.master.geometry('{}x{}'.format(300, 200))

    def body(self):
        self.master.title("Settings")

        Label(self.master, text='Start Freq:').grid(row=0)
        Label(self.master, text='Stop Freq').grid(row=1)
        Label(self.master, text='Steps').grid(row=2)

        self.start_freq = Entry(self.master)
        self.stop_freq = Entry(self.master)
        self.steps_freq = Entry(self.master)

        self.start_freq.grid(row=0, column=1)
        self.stop_freq.grid(row=1, column=1)
        self.steps_freq.grid(row=2, column=1)



if __name__ == '__main__':
    top = Settings()
    top.mainloop()