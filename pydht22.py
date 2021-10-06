import ctypes
import sys
import subprocess
import json


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


def read_sensors_subproc(pins, num_retries=2):
    cmd = ["./dht22", "--json", "-n", str(num_retries)] + [f"{x}" for x in pins]

    # Set timeout to 5 seconds plus max retry time
    timeout = 2 * (len(pins) * num_retries) + 5
    try:
        # Start subprocess and wait for it to terminate
        out = subprocess.check_output(cmd, timeout=timeout)
        # Decode JSON output
        resp = json.loads(out.decode())
        readings = dict()
        for s in resp:
            if s["status"] == "OK":
                readings[int(s["pin"])] = (float(s["temp"]), float(s["humidity"]))
    except subprocess.CalledProcessError as e:
        print(e)
        readings = dict()
    except subprocess.TimeoutExpired as e:
        print(e)
        readings = dict()

    return readings


def read_sensors(pins):
    sensors = list()
    for pin in pins:
        sensor = Sensor()
        sensor.pin = pin
        sensors.append(sensor)

    # Convert to ctypes array
    sensors = (Sensor * len(sensors))(*sensors)

    dht22.process_sensors(len(sensors), ctypes.byref(sensors), 3)

    readings = dict()
    for s in sensors:
        readings[s.pin] = (s.temp, s.humidity)

    return readings
