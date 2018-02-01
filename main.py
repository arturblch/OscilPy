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

from utils import LogGetter, SettingsGetter

SIZE = (650, 500)
PROGRAM_NAME = "Oscil GUI"
DEV_LIST = ['oscil', 'generator']



class Task_1:
    def __init__(self, settings):
        self.is_stop = False
        self.pause = False
        self.settings = settings

    def start(self, oscil, generator, save_loc):
        oscil.open()                    # Открываем устройства
        generator.open()

        oscil.write("factory")          # Сброс настроек
        generator.write("*RST")

        generator.write("FREQ:STEP:MODE USER")
        generator.write("FREQ:STEP {}".format(self.settings['freq_step']))
        generator.write("FREQ {}".format(self.settings['start_freq']))
        generator.write("SOUR:POW:POW {}".format(self.settings['power']))

        oscil.write("MEASU:MEAS1:SOUrce CH1")                          # Источник сигнала
        oscil.write("MEASU:MEAS2:SOUrce CH2")
        oscil.write("MEASU:MEAS1:TYPe PK2PK")                          # Тип измерения (Пиковое)
        oscil.write("MEASU:MEAS2:TYPe PK2PK")
        oscil.write("MEASU:MEAS1:State ON")                            # Включить
        oscil.write("MEASU:MEAS2:State ON")

        try:
            with open(save_loc, "w") as file:
                file.write(";".join(["Gen_freq", "Ch_1", "Ch_2"]) + '\n')
                # generator.write("OUTP ON")
                chanel1 = oscil.query("MEASU:MEAS1:VALue?").split()[1]                    # Возврат значения
                chanel2 = oscil.query("MEASU:MEAS2:VALue?").split()[1]

                file.write(";".join([self.settings['start_freq'], chanel1, chanel2])+ '\n')

                for gen_freq in range(int(self.settings['start_freq'][:-3]) + int(self.settings['freq_step'][:-3]),
                                    int(self.settings['stop_freq'][:-3]) + int(self.settings['freq_step'][:-3]),
                                    int(self.settings['freq_step'][:-3])):

                    generator.write("FREQ UP")
                    time.sleep(0.1)
                    chanel1 = oscil.query("MEASU:MEAS1:VALue?").split()[1]                   # Возврат значения
                    chanel2 = oscil.query("MEASU:MEAS2:VALue?").split()[1]

                    file.write(";".join([str(gen_freq), str(chanel1), str(chanel2)])+'\n')
        except Exception as e:
            raise e
        finally:
            generator.write("OUTP OFF")

    def stop(self):
        self.is_stop = True

    def pause(self):
        self.pause = not self.pause



""" TODO: Finish settings ini file read/write
"""
class TaskSettings(ttk.Frame):
    def __init__(self):
        self.root = tk.Tk()
        self.setvar = tk.StringVar()
        self.root.title("Task Settings")

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

class TaskControl(ttk.Frame):
    def __init__(self, parent, gui):
        ttk.Frame.__init__(self, parent)
        self.gui = gui
        settings = {
            'start_freq' : '100 MHz',
            'stop_freq' : '200 MHz',
            'freq_step' : '1 MHz',
            'power' : '-20 dBm'
        }

        self.task = Task_1(settings)

        self.settingbtn = ttk.Button(self)
        self.settingbtn["text"] = "Settings"
        self.settingbtn["command"] = self.set_settings

        self.startbtn = ttk.Button(self)
        self.startbtn["text"] = "Start Mesurement"
        self.startbtn["command"] = self.start_cur_task

        self.settingbtn.grid(row=0, column=0)
        self.startbtn.grid(row=0, column=1)

    def get_settings(self):
        settings = SettingsGetter.get_settings(self.parent, self.parent.settings)
        self.parent.settings = settings

    def start_cur_task(self):
        oscil = self.gui.dm.get_device("oscil")
        generator = self.gui.dm.get_device("generator")
        save_loc = self.gui.fileoptions.get_filepath()
        self.task.start(oscil, generator, save_loc)

class Oscil_GUI:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.exit)

        self.dev_views = dict()             # Кортеж видов для устройств

        self.log = LogGetter.get_logger()   # Создаем логер
        self.settings = None                # Создаем настройки
        self.dm = DeviceManager(self.log)   # Создаем менеджер устройств
        for dev_name in DEV_LIST:           # Добовляем устройства к менеджеру
            self.dm.add_device(dev_name)

        self.init_gui()                     # Создаем форму

        for dev_view in self.dev_views.values():  # Обновляем список устройств  
            dev_view.refresh_devices()            # для каждого вида

    def init_gui(self):
        self.fileoptions = FileOptions(self.root)
        for dev_name in DEV_LIST:
            device = self.dm.devices[dev_name]
            if device is not None:
                self.dev_views[dev_name] = DeviceView(self.root, self.dm, device, self.log)
        
        self.toolbar = TaskControl(self.root, self)

        self.console = ConsoleView(self.root)
        wh = ConsoleHandler(self.console)   # Подписываем консоль к логеру
        self.log.addHandler(wh)

        self.fileoptions.pack(side="top", fill="both")
        for dev in self.dev_views.values():
            dev.pack(side="top", fill="both")
        self.toolbar.pack(side="top", fill="both")
        self.console.pack(side="top", fill="both")

    def exit(self):
        self.dm.close_all()
        self.root.destroy()

if __name__ == "__main__":

    root = Tk()
    root.geometry('{}x{}'.format(*SIZE))
    root.title(PROGRAM_NAME)

    gui = Oscil_GUI(root)
    root.mainloop()