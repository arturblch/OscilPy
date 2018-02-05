import pyvisa
from  time import sleep
dm = pyvisa.ResourceManager()

oscil = dm.open_resource("USB0::0x0699::0x036A::C044437::INSTR")
try:

    # Источник сигнала
    print(oscil.write("MEASU:MEAS1:SOUrce CH1"))
    print(oscil.write("SELECT:CH1 ON"))
    print(oscil.query("*esr?"))
    print(oscil.query("allev?"))
    # Тип измерения (Пиковое)
    print(oscil.write("MEASU:MEAS1:TYPe PK2PK"))
    sleep(1)
    print(float(oscil.query("MEASU:MEAS1:VALue?").split()[1]))
    print(float(oscil.query("MEASU:MEAS1:VALue?").split()[1]))
    print(oscil.query("*esr?"))
    print(oscil.query("allev?"))
    # Включить
finally:
    oscil.close()