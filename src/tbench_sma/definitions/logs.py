# definitions/logs.py

from enum import IntEnum

class LogLevel(IntEnum):
    NONE = 0       # No log output
    ERROR = 1      # Critical errors
    WARN = 2       # Recoverable errors
    INFO = 3       # Normal flow information
    DEBUG = 4      # Extra debugging information
    VERBOSE = 5    # Very detailed / frequent logging

    @classmethod
    def from_value(cls, value: int) -> "LogLevel | None":
        try:
            return cls(value)
        except ValueError:
            return None

class LogModule(IntEnum):
    ALL = 0
    LOG = 1
    AMBIENT = 2
    CO = 3
    LEDS = 4
    ANVS = 5
    API = 6
    BME688 = 7
    APP = 8
    MQTT = 9
    UTIL = 10
    WIFI = 11
    BLE = 12
    SM = 13
    PROCESS = 14
    SNTP = 15
    OTA = 16

    MOT = 17
    RC5 = 18
    REPELLER = 19
    PAIR = 20
    EVENT = 21
