#!/env/python python
import os
import time
import sys
import platform
from json import load as json_load, dump as json_dump

import visa
from pyvisa.errors import VisaIOError
import pyvisa
from pyvisa.resources import MessageBasedResource

from tkinter import *
from tkinter import ttk

from tkinter import filedialog
from tkinter import messagebox
from src.DeviceManager import DeviceManager
from src.DeviceView import DeviceView
from src.Console import ConsoleView, ConsoleHandler

from utils import LogGetter

SIZE = (650, 500)
PROGRAM_NAME = "Oscil GUI"





""" TODO: Finish settings ini file read/write
"""
class MesureControl(ttk.Frame):
    def __init__(self):
        self.root = tk.Tk()
        self.setvar = tk.StringVar()
        self.root.title("Mesurement")

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

    def init_path_form(self):
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
        path = filedialog.askdirectory()

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

class FileOptions(Frame):
    def __init__(self, parent=None):
        ttk.Frame.__init__(self, parent)
        self.counter = 0

        # SAVEL PATH / DIRECTORY
        self.pathdesc = ttk.Label(self)
        self.pathdesc["justify"] = LEFT
        self.pathdesc["text"] = "Save path"

        self.pathvar = StringVar()

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
        self.filedesc["justify"] = LEFT
        self.filedesc["text"] = "Filename"

        self.filevar = StringVar()
        self.filevar.set("Oscil_gui_" + time.strftime("%d_%m_%Y_") + "0.csv")

        self.fileentry = ttk.Entry(self)
        self.fileentry["textvariable"] = self.filevar

        self.newnamebtn = ttk.Button(self)
        self.newnamebtn["text"] = "Next name"
        self.newnamebtn["command"] = self.updatefilename

        self.pathdesc.grid(row=0, column=0)
        self.pathentry.grid(row=0, column=1, sticky=E + W)
        self.pathbtn.grid(row=0, column=2, sticky=E + W)

        self.filedesc.grid(row=1, column=0)
        self.fileentry.grid(row=1, column=1, sticky=E + W)
        self.newnamebtn.grid(row=1, column=2, sticky=E + W)

        self.columnconfigure(1, weight=2)

    def path_dialog(self):
        path = filedialog.askdirectory()

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

        self.settingbtn.grid(row=0, column=0)

        self.columnconfigure(0, weight=1)

    def open_settings(self):
        settingwin = SettingsControl(self)


    def open_shell(self):
        shellwin = ShellWindow()
        self.shells.append(shellwin)


class Oscil_GUI:
    def __init__(self, root, args=None):
        self.root = root

        self.need_devices = ['oscil', 'generator']
        self.devices = {dev : None for dev in self.need_devices}
        self.devices_ctrls = dict()

        self.argparse(args)

        self.log = LogGetter.get_logger()
        
        self.init_gui()
        wh = ConsoleHandler(self.console)
        self.log.addHandler(wh)
        
        self.dm = DeviceManager(self.log)
        for dev_name in self.need_devices:
            self.dm.add_device(dev_name)

        for dev_ctrl in self.devices_ctrls.values():
            dev_ctrl.refresh_devices()

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

    def init_gui(self):
        self.fileoptions = FileOptions(self.root)
        for dev_name in self.need_devices:
            self.devices_ctrls[dev_name] = DeviceView(self, dev_name, get_id=self.get_id(), _open=self.open())

        self.toolbar = Toolbar(self.root, dlfunc=self.dl_picture)
        self.console = ConsoleView(self.root)

        self.fileoptions.pack(side="top", fill="both")
        for dev in self.devices_ctrls.values():
            dev.pack(side="top", fill="both")
        self.toolbar.pack(side="top", fill="both")
        self.console.pack(side="top", fill="both")

    def get_id(self):
        def wraper(device, name):
            dev_instance = self.rm.open_resource(name)
            response = dev_instance.query("*IDN?")
            self.log.info("Device - " + response.split(',')[1])
        return wraper

    def open(self):
        def wraper(name):
            self.dm.open(name)
        return wraper



    def dl_picture(self):
        filepath = self.fileoptions.get_filepath()
        overwrite = None

        if os.path.isfile(filepath):
            # returns boolean value
            overwrite = messagebox.askyesno(
                type="yesno",
                message="A file with the same name already exists in \n" +
                filepath + "\nThis operation will overwrite it. Continue?",
                icon="question",
                title="File already exists")

        if overwrite or overwrite == None:
            try:
                self.dev_instance = self.rm.open_resource(
                    self.instancectl.get_selection())
                self.log.info("Connected to " +
                                 self.instancectl.get_selection())

                self.dev_instance.chunk_size = 5000000
                self.dev_instance.timeout = None

                self.log.info("Sending image download command")
                self.dev_instance.write("HARDCOPY:PORT RS232")
                self.dev_instance.write("HARDCOPY:filename \"TEK.PNG\"")
                self.dev_instance.write("HARDCOPY START")
                time.sleep(1)

                self.log.info("Starting image download")
                prtscr_bin = self.dev_instance.read_raw()
                self.log.info("Image download complete, writing file")

                with open(filepath, "wb") as f:
                    f.write(prtscr_bin)
                self.log.info("Image file written")

                self.dev_instance.close()
                self.log.info("Download Completed")

            except pyvisa.errors.VisaIOError:
                self.log.error(
                    "Visa IOError w/ [" + self.instancectl.get_selection() + "]" +
                    "\tPS: Did you choose the device on the combobox?")


if __name__ == "__main__":

    root = Tk()
    root.geometry('{}x{}'.format(*SIZE))
    root.title(PROGRAM_NAME)

    Oscil_GUI(root)

    root.mainloop()
