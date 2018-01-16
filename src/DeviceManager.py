import pyvisa
from pyvisa.errors import VisaIOError

class Device:
    def __init__(self, name, log):
        self.name = name         # Наименование устройства    
        self.addr = None         # Адресс по которому находится устройство(None если не открыто)
        self.is_open  = False    # Флаг показывающий открыто ли устройство
        self.dev_obj = None      # Объект открытого устройства

        self.log = log

    def open(self):
        if not self.is_open:
            if self.addr is not None:
                try:
                    self.dev_obj = self.rm.open_resource(self.addr)
                    self.log.log(self.name + " connected to " + self.addr)

                except OSError:
                    self.log.error("Can't do this")

                except VisaIOError:
                    self.log.error("Timeout or divice not connnected")

            else:
                self.log.error("Don't have adress to device")
        else:
            self.log.error("Already open")

    def close(self):
        if self.is_open:
                try:
                    self.dev_obj.close()                # Закрываем соединение
                    self.log.log(self.name + " closed")
                    self.dev_obj = None

                except OSError:
                    self.log.error("Can't do this")

                except VisaIOError:
                    self.log.error("Timeout or divice not connnected")
        else:
            self.log.error("Already closed")

    def query(self, command):
        try:
            response = self.dev_obj.query(command)
        except VisaIOError:
                    self.log.error("Timeout or divice not connnected")
        return response

    def write(self, command):
        return self.dev_obj.write(command)


class DeviceManager:
    def __init__(self, log):
        self.devices = dict()
        self.rm = pyvisa.ResourceManager()
        self.log = log

    def open(self, name):
        if name in self.devices.keys():

            device = self.devices[name]

            if not device.is_open:
                if device.addr is not None:
                    try:
                        device.dev_obj = self.rm.open_resource(device.addr)
                        device.is_open = True
                        self.log.log(device.name + " connected to " + device.addr)

                    except OSError:
                        self.log.error("Can't do this")

                    except VisaIOError:
                        self.log.error("Timeout or divice not connnected")

                else:
                    self.log.error("Don't have adress to device")
            else:
                self.log.error("Already open")
        else:
            self.log.error("Don't have device for it")

    def close(self, name):
        if name in self.devices.keys():
            self.devices[name].close()
        else:
            self.log.error("Don't have device for it")

    def add_device(self, name):
        if name not in self.devices.keys():
            self.devices[name] = Device(name, self.log)
        else:
            self.log.error("Device with this name already exists")

    def get_list(self):
        return self.rm.list_resources()

    def get_all_devices(self):
        return self.devices
