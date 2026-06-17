# definitions/devices.py

from enum import IntEnum

class Device(IntEnum):
    FAN_IN = 1
    FAN_OUT = 2
    HEATER = 3
    IONIZER = 4
    ULTRA_REPELLER = 5
    SENSOR_HUMIDITY = 6
    SENSOR_AIRQUALITY = 7
    SENSOR_AMBIENT = 8
    SENSOR_CO = 9
