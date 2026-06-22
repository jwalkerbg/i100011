# definitions/leds.py

from enum import IntEnum, IntFlag

class LedOperation(IntEnum):
    OFF = 0
    ON = 1
    BLINK = 2

class Led(IntFlag):
    GREEN = 0x01
    RED = 0x02
    YELLOW = 0x04
    BLUE = 0x08
    WHITE = 0x10
    ALL = GREEN | RED | YELLOW | BLUE | WHITE
