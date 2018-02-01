import tkinter as tk
from tkinter import messagebox
from tkinter import Toplevel, Label, Entry, Frame, Button, E, W
import json
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

class Settings(Toplevel):
    def __init__(self, parent=None, old_set=None):
        super().__init__(parent)
        self.transient(parent)

        self.parent = parent

        self.title("Settings")
        self.resizable(False, False)

        self.cur_set = old_set

        self.initial_focus = self.body()
        self.init_set()

        self.grab_set()
        self.initial_focus.focus_set()

        self.wait_window()

    def body(self):
        
        Label(self, text='Start Freq:').grid(row=0, column=0)
        Label(self, text='Stop Freq').grid(row=1, column=0)
        Label(self, text='Step Freq').grid(row=2, column=0)
        Label(self, text='Time_offset').grid(row=3, column=0)
        Label(self, text='Power').grid(row=4, column=0)

        self.start_freq = Entry(self)
        self.stop_freq = Entry(self)
        self.steps_freq = Entry(self)
        self.time_offset = Entry(self)
        self.power = Entry(self)

        self.start_freq.grid(row=0, column=1, columnspan=3)
        self.stop_freq.grid(row=1, column=1, columnspan=3)
        self.step_freq.grid(row=2, column=1, columnspan=3)
        self.time_offset.grid(row=3, column=1, columnspan=3)
        self.power.grid(row=4, column=1, columnspan=3)

        self.save_btn = Button(self)
        self.save_btn["text"] = "Save"
        self.save_btn["command"] = self.save

        self.ok_btn = Button(self)
        self.ok_btn["text"] = "OK"
        self.ok_btn["command"] = self.ok

        self.cancel_btn = Button(self)
        self.cancel_btn["text"] = "Cancel"
        self.cancel_btn["command"] = self.cancel


        self.save_btn.grid(row=4, column=1, sticky=tk.E+tk.W)
        self.ok_btn.grid(row=4, column=2,sticky=tk.E+tk.W)
        self.cancel_btn.grid(row=4, column=3,sticky=tk.E+tk.W)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        return  self.start_freq

    def init_set(self):
        if self.cur_set is None:
            return
        for item in ['start_freq', 'stop_freq', 'steps_freq', 'time_offset', 'power']:
            if item in self.cur_set:
                e = getattr(self, item)
                e.delete(0,tk.END)
                e.insert(0,self.cur_set[item])

    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.cancel()

    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()

    def validate(self):

        try:
            cur_set = self.get_cur_set()
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                "Please try again",
                parent = self
            )
            return 0

        if not all(cur_set.values()):
            messagebox.showwarning(
                "Empty entry",
                "Please try again",
                parent = self
            )
            return 0

        self.cur_set = cur_set
        return 1

    def get_cur_set(self):
        cur_set = {
                    'start_freq' : self.start_freq.get(),
                    'stop_freq' : self.stop_freq.get(),
                    'steps_freq' : self.steps_freq.get(),
                    'time_offset' : int(self.time_offset .get()),
                    'power' : self.power.get()
                    }
        return cur_set

    def save(self):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        with open('settrings.json', 'w') as f:
                json.dump(self.cur_set, f)
        messagebox.showinfo(
                "Save",
                "settings.json save at {}".format(dir_path),
                parent = self
            )

def get_settings(parent=None, old_set=None):
    dialog = Settings(parent, old_set)
    return dialog.cur_set

if __name__ == '__main__':
    root = tk.Tk()
    setting = get_settings(root)
    print(setting)
    root.wait_window()