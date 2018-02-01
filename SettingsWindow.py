import tkinter as tk
from tkinter import Toplevel, Label, Entry, Frame, Button, E, W

class Settings(Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.body()

    def body(self):
        self.master.title("Settings")

        Label(self.master, text='Start Freq:').grid(row=0, sticky= W)
        Label(self.master, text='Stop Freq').grid(row=1,  sticky= W)
        Label(self.master, text='Steps').grid(row=2, sticky= W)
        Label(self.master, text='Time_offset').grid(row=3, sticky= W)

        self.start_freq = Entry(self.master)
        self.stop_freq = Entry(self.master)
        self.steps_freq = Entry(self.master)
        self.time_offset = Entry(self.master)


        self.save_btn = Button(self.master)
        self.save_btn["text"] = "Save"
        self.save_btn["command"] = self.save


        self.start_freq.grid(row=0, column=1,)
        self.stop_freq.grid(row=1, column=1,)
        self.steps_freq.grid(row=2, column=1,)
        self.time_offset.grid(row=3, column=1,)
        self.save_btn.grid(row=4, column=1, sticky=E)

    def save(self):
        pass

    def show(self):
        self.deiconify()
        self.wait_window()
        value = self.start_freq.get()
        return value

if __name__ == '__main__':
    top = Settings()
    print(top.show())