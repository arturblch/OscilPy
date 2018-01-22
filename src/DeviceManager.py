import pyvisa
from pyvisa.errors import VisaIOError

class Device:
    def __init__(self, rm, name, log):
        self.rm = rm
        self.name = name         # Наименование устройства    
        self.addr = None         # Адресс по которому находится устройство(None если не открыто)
        self.is_open  = False    # Флаг показывающий открыто ли устройство
        self.dev_obj = None      # Объект открытого устройства

        self.log = log

    def set_addr(self, new_addr):
        if self.addr != new_addr:
            self.addr = new_addr
            self.log.info('Set "' + new_addr +'" address for ' + self.name)

    def open(self):
        if not self.is_open:
            if self.addr is not None:
                try:
                    self.dev_obj = self.rm.open_resource(self.addr)
                    self.is_open = True
                    self.log.info(self.name + " connected to " + self.addr)

                except OSError:
                    self.log.error("Can't do this")

                except VisaIOError:
                    self.log.error("Timeout or divice not connnected")

            else:
                self.log.error("Haven't adress to device")
                raise ValueError("Haven't have adress to device")
        else:
            self.log.info("Already open")

    def close(self):
        if self.is_open:
                try:
                    self.dev_obj.close()                # Закрываем соединение
                    self.log.info(self.name + " closed")
                    self.dev_obj = None
                    self.is_open = False

                except OSError:
                    self.log.error("Can't do this")

                except VisaIOError:
                    self.log.error("Timeout or divice not connnected")
        else:
            self.log.info("Already closed")

    def query(self, command):
        response = None
        try:
            response = self.dev_obj.query(command)
        except VisaIOError:
            self.log.error("Timeout or divice not connnected")
        return response

    def write(self, command):
        return self.dev_obj.write(command)

    def id_info(self):
        self.open()
        response = self.query("*IDN?")
        if response is not None:
            self.log.info("Device - " + response.split(',')[1])
        self.close()

''' DeviceManager хранит объект ResourceManager(pyvisa) и перечень устройств
'''
class DeviceManager:
    def __init__(self, log):
        self.devices = dict()
        self.rm = pyvisa.ResourceManager()
        self.log = log

    def open(self, name):
        if name in self.devices.keys():
            self.devices[name].open()
        else:
            self.log.error("Don't have device for it")

    def open_all(self):
        for dev in self.devices.values():
            dev.open()

    def close(self, name):
        if name in self.devices.keys():
            self.devices[name].close()
        else:
            self.log.error("Don't have device for it")

    def close_all(self):
        for dev in self.devices.values():
            if dev.is_open:
                dev.close()

    def add_device(self, name):
        if name not in self.devices.keys():
            self.devices[name] = Device(self.rm, name, self.log)
        else:
            self.log.error("Device with this name already exists")

    def get_list(self):
        return self.rm.list_resources()

    def get_device(self, dev_name):
        return self.devices.get(dev_name)

    def get_all_devices(self):
        return self.devices
