# definitions/modes.py

from enum import IntEnum

class DeviceMode(IntEnum):
    STANDBY = 0
    AUTO = 1
    MANUAL = 2
    OFF = 3
    FORCED_CLEANING = 4
    NIGHT = 5
    TEST = 6
