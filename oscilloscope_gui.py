#!/env/python python
import os
import time
import sys
import platform
from json import load as json_load, dump as json_dump

import visa
import pyvisa
from pyvisa.resources import MessageBasedResource

import tkinter as tk
from tkinter import ttk

from tkinter import filedialog as tkfiledialog
from tkinter import messagebox as tkmessagebox


""" TODO: Finish settings ini file read/write
========================================================
COMMON CLASS OBJECTS
========================================================
"""


class SettingsControl(ttk.Frame):
    def __init__(self, parent):
        self.frame = tk.Toplevel(parent)
        self.setvar = tk.StringVar()
        self.setvar.set(os.path.abspath('.') + "/settings.json")

        settings_list = ['start', 'stop', 'step']
        self.settings = {setting : None for setting in settings_list}

        self.init_save_path_form()

    def init_settings_form(self, fields):
        entries = dict()
        for field in fields:
            row = ttk.Frame(root)
            lab = ttk.Label(row, width=15, text=field, anchor='w')
            ent = ttk.Entry(row)
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            entries.update({field: ent})
        return entries

    def init_save_path_form(self):
        self.setdesc = ttk.Label(self)
        self.setdesc["justify"] = tk.LEFT
        self.setdesc["text"] = "Settings path"

        self.setentry = ttk.Entry(self)
        self.setentry["textvariable"] = self.setvar

        self.setpathbtn = ttk.Button(self)
        self.setpathbtn["text"] = "Select"
        self.setpathbtn["command"] = self.path_dialog

        self.setreadbtn = ttk.Button(self)
        self.setreadbtn["text"] = "Read"
        self.setreadbtn["command"] = self.read_config

        self.setreadbtn = ttk.Button(self)
        self.setreadbtn["text"] = "Save"
        self.setreadbtn["command"] = self.write_config

    def path_dialog(self):
        path = tkfiledialog.askdirectory()

        print(path)
        # file dialog returns a tuple for a path (?)
        if not path == () and not path == "":
            self.pathvar.set(path)

    def read_config(self):
        if  not os.path.isfile(self.filepath):
            print("ERROR: Not exists")
            raise ValueError
        with open(self.filepath, 'r') as file:
            for sett in self.settings_list:
                self.settings = json_load(file)[sett]

    def write_config(self):
        with open(self.filepath, 'w') as file:
            json_dump(self.settings, file)

    def show_window(self):
        pass
"""
========================================================
SHELL WINDOW + SHELL WINDOW WIDGETS
========================================================
"""


class ShellWindow(ttk.Frame):
    def __init__(self, parent=None):
        top = tk.Toplevel(parent)
        ttk.Frame.__init__(top, parent)
        self.initui()

        # self.title("NPSO Visa Shell")

    def initui(self):
        self.demo = ttk.Label(self)
        self.demo["text"] = "Demo label for testing"

        self.demo.grid(row=0, column=0, sticky=tk.W + tk.E + tk.S + tk.N)

        self.pack(side="top", fill="both", expand=True)


"""
========================================================
MAIN WINDOW WIDGETS
========================================================
"""


class FileOptions(ttk.Frame):
    def __init__(self, parent=None):
        ttk.Frame.__init__(self, parent)
        self.counter = 0

        # SAVEL PATH / DIRECTORY
        self.pathdesc = ttk.Label(self)
        self.pathdesc["justify"] = tk.LEFT
        self.pathdesc["text"] = "Save path"

        self.pathvar = tk.StringVar()

        if platform.system() == "Windows":
            self.pathvar.set("C:/")
        else:
            self.pathvar.set("/tmp")

        self.pathentry = ttk.Entry(self)
        self.pathentry["textvariable"] = self.pathvar

        self.pathbtn = ttk.Button(self)
        self.pathbtn["text"] = "Select"
        self.pathbtn["command"] = self.path_dialog

        # SAVE FILENAME
        self.filedesc = ttk.Label(self)
        self.filedesc["justify"] = tk.LEFT
        self.filedesc["text"] = "Filename"

        self.filevar = tk.StringVar()
        self.filevar.set("Oscil_gui_" + time.strftime("%d_%m_%Y_") + "0.csv")

        self.fileentry = ttk.Entry(self)
        self.fileentry["textvariable"] = self.filevar

        self.newnamebtn = ttk.Button(self)
        self.newnamebtn["text"] = "Next name"
        self.newnamebtn["command"] = self.updatefilename

        self.pathdesc.grid(row=0, column=0)
        self.pathentry.grid(row=0, column=1, sticky=tk.E + tk.W)
        self.pathbtn.grid(row=0, column=2)

        self.filedesc.grid(row=1, column=0)
        self.fileentry.grid(row=1, column=1, sticky=tk.E + tk.W)
        self.newnamebtn.grid(row=1, column=2)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)

    def path_dialog(self):
        path = tkfiledialog.askdirectory()

        print(path)
        # file dialog returns a tuple for a path (?)
        if not path == () and not path == "":
            self.pathvar.set(path)

    def get_filepath(self):
        return self.pathvar.get() + "/" + self.filevar.get()

    def updatefilename(self):
        self.counter += 1
        self.filevar.set(
            "Oscil_gui_" + time.strftime("%d_%m_%Y_") + str(self.counter) + ".csv")


class InstanceControl(ttk.Frame):
    def __init__(self, parent, dev_name, devices=None, refreshfunc=None, get_id=None, dlfunc=None):
        ttk.Frame.__init__(self, parent)
        self.dev_name = dev_name
        # check devices arg
        if not devices == None:
            self.devices = list(devices)
        else:
            self.devices = []

        # check function args
        if refreshfunc == None:
            print("ERROR: Unimplemented method `refreshfunc`")
            raise NotImplementedError
        else:
            self.refreshfunc = refreshfunc
        if get_id == None:
            print("ERROR: Unimplemented method `get_id`")
            raise NotImplementedError
        else:
            self.get_id_func = get_id

        self.optiondesc = ttk.Label(self)
        self.optiondesc["justify"] = tk.LEFT
        self.optiondesc["text"] = "Select " + self.dev_name

        self.selected_option = tk.StringVar()
        self.optionsui = ttk.Combobox(self)
        # self.optionsui["width"] = 30
        self.optionsui["textvariable"] = self.selected_option
        self.optionsui["values"] = tuple(self.devices)

        self.idbtn = ttk.Button(self)
        self.idbtn["text"] = "Get ID"
        self.idbtn["command"] = self.get_id

        self.refreshbtn = ttk.Button(self)
        self.refreshbtn["text"] = "Refresh"
        self.refreshbtn["command"] = self.refreshfunc

        self.optiondesc.grid(row=0, column=0)
        self.optionsui.grid(row=0, column=1, sticky=tk.E + tk.W)
        self.idbtn.grid(row=0, column=2)
        self.refreshbtn.grid(row=0, column=3)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    def set_devices(self, devices):
        self.devices = devices
        self.optionsui["values"] = tuple(self.devices)

    def get_selection(self):
        return self.selected_option.get()

    def get_id(self):
        self.get_id_func(self)


class Toolbar(ttk.Frame):
    def __init__(self, parent=None, dlfunc=None):
        ttk.Frame.__init__(self, parent)

        self.shells = []

        if dlfunc == None:
            print("ERROR: Unimplemented method `dlfunc`")
            raise NotImplementedError
        else:
            self.dlfunc = dlfunc

        self.settingbtn = ttk.Button(self)
        self.settingbtn["text"] = "Settings"
        self.settingbtn["command"] = self.open_settings

        self.shellbtn = ttk.Button(self)
        self.shellbtn["text"] = "Open Shell"
        self.shellbtn["command"] = self.open_shell
        # self.shellbtn["state"] = tk.DISABLED

        self.settingbtn.grid(row=0, column=0)
        self.shellbtn.grid(row=0, column=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        # self.columnconfigure(2, weight=1)

    def open_settings(self):
        settingwin = SettingsControl(self)


    def open_shell(self):
        shellwin = ShellWindow()
        self.shells.append(shellwin)


class Console(ttk.Frame):
    def __init__(self, parent=None, stdout=False):
        ttk.Frame.__init__(self, parent)

        self.stdout = stdout

        self.consoleui = tk.Text(self, width=50)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.consoleui.yview)

        self.consoleui.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="left", fill="both")

    def txt(self, text):
        if self.stdout:
            print(text)

        self.consoleui.insert(tk.END, text + '\n')

    def log(self, text):
        self.txt("LOG: " + text)

    def error(self, text):
        self.txt("ERROR: " + text)


"""
========================================================
MAIN WINDOW
========================================================
"""


class Oscil_GUI(ttk.Frame):
    def __init__(self, root, args=None):
        ttk.Frame.__init__(self, root)

        root.wm_title("Oscil GUI")
        # root.resizable(width=False, height=False)

        self.rm = None
        self.stdout = False

        self.argparse(args)
        self.initui()
        self.initserial()

    def argparse(self, args):
        if not args == None:
            for i in range(len(args)):
                if args[i] in ("--help", "-h"):
                    helptext = "Oscil_GUI.py [args]"
                    print(helptext)

                elif args[i] == "--stdout":
                    if args[i + 1].lower() == "true":
                        self.stdout = True
                    elif args[i + 1].lower() == "false":
                        self.stout = False

    def initui(self):
        self.fileoptions = FileOptions(self)
        self.oscil = InstanceControl(
            self, 'oscil', refreshfunc=self.initserial, get_id=self.get_id())
        self.generator = InstanceControl(
            self, 'generator', refreshfunc=self.initserial, get_id=self.get_id())
        self.toolbar = Toolbar(self, dlfunc=self.dl_picture)
        self.console = Console(self, stdout=True)

        self.fileoptions.pack(side="top", fill="both", expand=True)
        self.oscil.pack(side="top", fill="both", expand=True)
        self.generator.pack(side="top", fill="both", expand=True)
        self.toolbar.pack(side="top", fill="both", expand=True)
        self.console.pack(side="top", fill="both", expand=True)

        self.pack(side="top", fill="both", expand=True)
        self.console.log("GUI initialization finished")

    def initserial(self):
        try:
            if self.rm == None:
                self.rm = visa.ResourceManager()

            self.devices = self.rm.list_resources()

            self.console.log("Found Devices:\n\t" + '\n\t'.join(self.devices))
            self.oscil.set_devices(self.devices)
            self.generator.set_devices(self.devices)

        except OSError:
            self.console.error("Cannot initialize serial")

        finally:
            self.console.log("Serial initialization finished")

    def get_id(self):
        def wraper(child):
            if child.get_selection():
                try:
                    if self.rm == None:
                        self.rm = visa.ResourceManager()

                    child.dev_instance = self.rm.open_resource(
                        child.get_selection())
                    self.console.log("Connected to " + child.get_selection())

                    response = child.dev_instance.query("*IDN?")
                    self.console.log("Device - "+ response.split(',')[1])

                except OSError:
                    self.console.error("Can't do this")

                finally:
                    child.dev_instance.close()
                    self.console.log("Close device")
        return wraper

    def dl_picture(self):
        filepath = self.fileoptions.get_filepath()
        overwrite = None

        if os.path.isfile(filepath):
            # returns boolean value
            overwrite = tkmessagebox.askyesno(
                type="yesno",
                message="A file with the same name already exists in \n" +
                filepath + "\nThis operation will overwrite it. Continue?",
                icon="question",
                title="File already exists")

        if overwrite or overwrite == None:
            try:
                self.dev_instance = self.rm.open_resource(
                    self.instancectl.get_selection())
                self.console.log("Connected to " +
                                 self.instancectl.get_selection())

                self.dev_instance.chunk_size = 5000000
                self.dev_instance.timeout = None

                self.console.log("Sending image download command")
                self.dev_instance.write("HARDCOPY:PORT RS232")
                self.dev_instance.write("HARDCOPY:filename \"TEK.PNG\"")
                self.dev_instance.write("HARDCOPY START")
                time.sleep(1)

                self.console.log("Starting image download")
                prtscr_bin = self.dev_instance.read_raw()
                self.console.log("Image download complete, writing file")

                with open(filepath, "wb") as f:
                    f.write(prtscr_bin)
                self.console.log("Image file written")

                self.dev_instance.close()
                self.console.log("Download Completed")

            except pyvisa.errors.VisaIOError:
                self.console.error(
                    "Visa IOError w/ [" + self.instancectl.get_selection() + "]")
                self.console.txt(
                    "\tPS: Did you choose the device on the combobox?")


if __name__ == "__main__":

    root = tk.Tk()
    root.geometry('{}x{}'.format(650, 300))

    view = Oscil_GUI(root, sys.argv)
    root.mainloop()
