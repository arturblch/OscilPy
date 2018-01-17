from tkinter import ttk
from tkinter import *


class DeviceView(Frame):
    def __init__(self, parent, dev_name, get_id=None, _open=None):
        Frame.__init__(self, parent.root)
        self.root = parent
        self.dev_name = dev_name

        # check function args
        if get_id is None:
            print("ERROR: Unimplemented method `get_id`")
            raise NotImplementedError
        else:
            self.get_id_func = get_id

        if _open is None:
            print("ERROR: Unimplemented method `_open`")
            raise NotImplementedError
        else:
            self.open_func = _open

        self.optiondesc = ttk.Label(self)
        self.optiondesc["justify"] = LEFT
        self.optiondesc["text"] = "Select " + self.dev_name

        self.selected_option = StringVar()
        self.optionsui = ttk.Combobox(self)
        self.optionsui["textvariable"] = self.selected_option
        self.optionsui["values"] = tuple()

        self.opbtn = ttk.Button(self)
        self.opbtn["text"] = "Open"
        self.opbtn["command"] = lambda: self.open_func(self.dev_name)

        self.idbtn = ttk.Button(self)
        self.idbtn["text"] = "Get ID"
        self.idbtn["command"] = lambda: self.get_id_func(self.dev_name)

        self.refreshbtn = ttk.Button(self)
        self.refreshbtn["text"] = "Refresh"
        self.refreshbtn["command"] = self.refresh_devices

        self.optiondesc.grid(row=0, column=0)
        self.optionsui.grid(row=0, column=1, sticky=EW)
        self.opbtn.grid(row=0, column=2, sticky=EW)
        self.idbtn.grid(row=0, column=3, sticky=EW)
        self.refreshbtn.grid(row=0, column=4, sticky=EW)

        self.columnconfigure(1, weight=2)

    def refresh_devices(self):
        devices = self.root.dm.get_list()
        self.optionsui["values"] = tuple(devices)
        self.root.log.info('Refresh devices')

    def get_selection(self):
        return self.selected_option.get()
