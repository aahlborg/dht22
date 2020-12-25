import ctypes
import sys


# Load the C library
try:
    dht22 = ctypes.CDLL("./dht22.so")
except OSError as e:
    print(f"Error: {e}")
    sys.exit()


class Sensor(ctypes.Structure):
    _fields_ = [('pin', ctypes.c_int),
                ('status', ctypes.c_int),
                ('temp', ctypes.c_float),
                ('humidity', ctypes.c_float)]

    def __init__(self):
        self.status = -1

    def __repr__(self):
        return f"pin {self.pin}, status {self.status}, temp {self.temp:.1f}, humidity {self.humidity:.1f}"


def read_sensors(pins):
    sensors = list()
    for pin in pins:
        sensor = Sensor()
        sensor.pin = pin
        sensors.append(sensor)

    # Convert to ctypes array
    sensors = (Sensor * len(sensors))(*sensors)

#    for s in sensors:
#        print(s)

    dht22.process_sensors(len(sensors), ctypes.byref(sensors), 3)

#    for s in sensors:
#        print(s)

    readings = dict()
    for s in sensors:
        readings[s.pin] = (s.temp, s.humidity)

    return readings
