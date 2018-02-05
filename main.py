#!/env/python python
import os
import time
import sys
import platform
import json

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


# class OpenCommand:
#     __slots__ = 'device'

#     def __init__(self, device):
#         self.device = device

#     def execute(self):
#         self.device.open()


# class WriteCommand:
#     __slots__ = 'device', 'command', 'attr'

#     def __init__(self, device, command, attr=None):
#         self.device = device
#         self.command = command
#         self.attr = attr

#     def execute(self):
#         self.device.write("{} {}".format(self.command, self.attr))


# class QueryCommand:
#     __slots__ = 'device', 'command'

#     def __init__(self, device, command, attr):
#         self.device = device
#         self.command = command

#     def execute(device):
#         self.device.query(self.command)


# class Task_2:
#     def __init__(self, settings, devices):
#         self.is_stop = False
#         self.is_pause = False
#         self.settings = settings
#         self.device = devices
#         self.command_list = [
#             OpenCommand(self.device['oscil']),
#             OpenCommand(self.device['generator']),
#             WriteCommand(self.device['oscil'], 'factory'),
#             WriteCommand(self.device['generator'], '*RST'),
#         ]


class Task_1:
    def __init__(self, settings, log):
        self.is_stop = False
        self.is_pause = False
        self.settings = settings
        self.log = log

    def start(self, oscil, generator, save_loc):
        self.log.error('Start task')
        try:
            oscil.open()                    # Открываем устройства
            generator.open()

        except ValueError:
            self.log.error('Stop task')
            return


        oscil.write("factory")          # Сброс настроек
        generator.write("*RST")

        generator.write("FREQ:STEP:MODE USER")
        generator.write("FREQ:STEP {}MHz".format(self.settings['step_freq']))
        generator.write("FREQ {}MHz".format(self.settings['start_freq']))
        generator.write("SOUR:POW:POW {}dBm".format(self.settings['power']))

        # Источник сигнала
        oscil.write("MEASU:MEAS1:SOUrce CH1")
        oscil.write("MEASU:MEAS2:SOUrce CH2")
        # Тип измерения (Пиковое)
        oscil.write("MEASU:MEAS1:TYPe PK2PK")
        oscil.write("MEASU:MEAS2:TYPe PK2PK")
        # Включить
        oscil.write("MEASU:MEAS1:State ON")
        oscil.write("MEASU:MEAS2:State ON")

        try:
            with open(save_loc, "w") as file:
                file.write(";".join(["Gen_freq MHz", "Ch_1 V", "Ch_2 V"]) + '\n')
                # generator.write("OUTP ON")
                time.sleep(self.settings['time_offset'])
                value_ch1 = float(oscil.query("MEASU:MEAS1:VALue?").split()[1])                 # Возврат значения
                value_ch2 = float(oscil.query("MEASU:MEAS2:VALue?").split()[1])

                file.write(
                    ";".join([self.settings['start_freq'], value_ch1, value_ch2]) + '\n')

                for gen_freq in self.gen_freq():
                    if self.is_stop:
                        break
                    while self.is_pause:
                        time.sleep(0.2)
                    generator.write("FREQ UP")
                    time.sleep(self.settings['time_offset'])
                    value_ch1 = oscil.query("MEASU:MEAS1:VALue?").split()[1]                   # Возврат значения
                    value_ch2 = oscil.query("MEASU:MEAS2:VALue?").split()[1]

                    file.write(
                        ";".join([str(gen_freq), str(value_ch1), str(value_ch2)]) + '\n')
        except Exception as e:
            raise e
        finally:
            generator.write("OUTP OFF")

    def gen_freq(self):
        return range(int(self.settings['start_freq']) + int(self.settings['stop_freq']),
                                      int(self.settings['stop_freq']) +
                                      int(self.settings['stop_freq']),
                                      int(self.settings['stop_freq']))

    def stop(self):
        self.is_stop = True

    def pause(self):
        self.is_pause = not self.is_pause


class FileOptions(Frame):
    def __init__(self, parent=None):
        ttk.Frame.__init__(self, parent)
        self.counter = 0

        # SAVEL PATH / DIRECTORY
        self.pathdesc = ttk.Label(self)
        self.pathdesc["justify"] = LEFT
        self.pathdesc["text"] = "Save path"

        self.pathvar = StringVar()

        self.pathvar.set("C:/")

        self.pathentry = ttk.Entry(self, textvariable=self.pathvar)

        self.pathbtn = ttk.Button(self, text="Select")
        self.pathbtn["command"] = self.path_dialog

        # SAVE FILENAME
        self.filedesc = ttk.Label(self, text="Filename")
        self.filedesc["justify"] = LEFT

        self.filevar = StringVar()
        self.filevar.set("Oscil_gui_" + time.strftime("%d_%m_%Y_") + "0.csv")

        self.fileentry = ttk.Entry(self, textvariable=self.filevar)

        self.newnamebtn = ttk.Button(self, text="Next name")
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
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent.root)
        self.root = parent.root
        self.parent = parent
        self.log = parent.log
        self.settings = None

        self.settingbtn = ttk.Button(self)
        self.settingbtn["text"] = "Settings"
        self.settingbtn["command"] = self.get_settings

        self.startbtn = ttk.Button(self)
        self.startbtn["text"] = "Start Mesurement"
        self.startbtn["command"] = self.start_cur_task

        self.settingbtn.grid(row=0, column=0)
        self.startbtn.grid(row=0, column=1)

    def load_settings(self):
        if os.path.isfile('settings.json'):
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)
                self.log.info('Settings load sucsesfully')
        else:
            self.log.info('Settings missing')

    def get_settings(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.settings = SettingsGetter.get_settings(
            self.root, self.settings, save_dir=dir_path)

    def start_cur_task(self):
        if self.settings
            task = Task_1(self.settings, self.log)
            oscil = self.parent.dm.get_device("oscil")
            generator = self.parent.dm.get_device("generator")
            save_loc = self.parent.fileoptions.get_filepath()
            task.start(oscil, generator, save_loc)
        else:
            self.log.info('Settings missing')


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

        self.task_ctrl.load_settings()
        for dev_view in self.dev_views.values():  # Обновляем список устройств
            dev_view.refresh_devices()            # для каждого вида

    def init_gui(self):
        self.fileoptions = FileOptions(self.root)
        for dev_name in DEV_LIST:
            device = self.dm.devices[dev_name]
            if device is not None:
                self.dev_views[dev_name] = DeviceView(
                    self.root, self.dm, device, self.log)

        self.task_ctrl = TaskControl(self)

        self.console = ConsoleView(self.root)
        wh = ConsoleHandler(self.console)   # Подписываем консоль к логеру
        self.log.addHandler(wh)

        self.fileoptions.pack(side="top", fill="both")
        for dev in self.dev_views.values():
            dev.pack(side="top", fill="both")
        self.task_ctrl.pack(side="top", fill="both")
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
