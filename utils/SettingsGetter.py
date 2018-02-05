import tkinter as tk
from tkinter import messagebox
from tkinter import Toplevel, Label, Entry, Frame, Button, E, W
import json
import os
import re



class Settings(Toplevel):
    def __init__(self, parent=None, old_set=None, save_dir=None):
        super().__init__(parent)
        self.transient(parent)

        self.parent = parent
        self.cur_set = old_set
        if save_dir:
            self.save_dir = save_dir
        else:
            self.save_dir = os.path.dirname(os.path.realpath(__file__))

        self.title("Settings")
        self.resizable(False, False)


        self.initial_focus = self.body()
        self.init_set()

        self.grab_set()
        self.initial_focus.focus_set()

        self.wait_window()

    def body(self):
        
        Label(self, text='Start Freq, MHz:').grid(row=0, column=0)
        Label(self, text='Stop Freq, MHz').grid(row=1, column=0)
        Label(self, text='Step Freq, MHz').grid(row=2, column=0)
        Label(self, text='Time_offset, s').grid(row=3, column=0)
        Label(self, text='Power, dBm').grid(row=4, column=0)

        self.start_freq = Entry(self)
        self.stop_freq = Entry(self)
        self.step_freq = Entry(self)
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


        self.save_btn.grid(row=5, column=1, sticky=tk.E+tk.W)
        self.ok_btn.grid(row=5, column=2,sticky=tk.E+tk.W)
        self.cancel_btn.grid(row=5, column=3,sticky=tk.E+tk.W)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        return  self.start_freq

    def init_set(self):
        if self.cur_set is None:
            return
        for item in ['start_freq', 'stop_freq', 'step_freq', 'time_offset', 'power']:
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
                    'start_freq' :  float(self.start_freq.get()),
                    'stop_freq' :   float(self.stop_freq.get()),
                    'step_freq' :   float(self.step_freq.get()),
                    'time_offset' : int(self.time_offset .get()),
                    'power' :       float(self.power.get())
                    }
        return cur_set

    def save(self):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        save_path = os.path.join(self.save_dir, 'settrings.json')
        with open(save_path, 'w') as f:
                json.dump(self.cur_set, f)
        messagebox.showinfo(
                "Save done",
                "settings.json save at {}".format(self.save_dir),
                parent = self
            )

def get_settings(parent=None, old_set=None, save_dir=None):
    dialog = Settings(parent, old_set, save_dir)
    return dialog.cur_set

if __name__ == '__main__':
    root = tk.Tk()
    setting = get_settings(root)
    print(setting)
    root.wait_window()