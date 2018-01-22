from tkinter import ttk
from tkinter import *


class DeviceView(Frame):
    def __init__(self, root, dev_manager, device, log):
        Frame.__init__(self, root)
        self.dev_manager = dev_manager
        self.device = device
        self.dev_name = device.name
        self.log = log

        self.optiondesc = ttk.Label(self)
        self.optiondesc["justify"] = LEFT
        self.optiondesc["text"] = "Select " + self.dev_name

        self.selected_option = StringVar()
        self.optionsui = ttk.Combobox(self)
        self.optionsui["textvariable"] = self.selected_option
        self.optionsui["values"] = tuple()
        self.optionsui.bind("<<ComboboxSelected>>", lambda _ : self.set_address())

        self.opbtn = ttk.Button(self)
        self.opbtn["text"] = "Open"
        self.opbtn["command"] = self.device.open

        self.idbtn = ttk.Button(self)
        self.idbtn["text"] = "Get ID"
        self.idbtn["command"] = self.device.id_info

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
        devices = self.dev_manager.get_list()
        self.optionsui["values"] = tuple(devices)
        self.log.info('Refresh devices for ' + self.dev_name +' view')

    def get_selection(self):
        return self.selected_option.get()

    def set_address(self):
        new_addr = self.get_selection()
        self.device.set_addr(new_addr)
