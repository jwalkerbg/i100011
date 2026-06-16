# definitions/flags.py

from enum import IntEnum, IntFlag

class ParFlags(IntFlag):
    HAS_WIFI_CRED = 0x0001  # device has valid WiFi SSID/password
    CO_EN = 0x0002          # CO sensor enabled for ventilation
    HUMIDITY_EN = 0x0004    # humidity sensor enabled
    AIRQUALITY_EN = 0x0008  # air quality sensor enabled
    AMBIENT_EN = 0x0010     # ambient light sensor enabled
    HEATER_EN = 0x0020      # heater enabled
    IONIZER_EN = 0x0040     # ionizer enabled
    ULTRA_REPELLER_EN = 0x0080  # ultrasonic repeller enabled

class SensorState(IntFlag):
    HUMIDITY = 0b00000001
    AIR = 0b00000010
    AMBIENT = 0b00000100
    CO = 0b00001000
    TEMP = 0b00010000

class OutputState(IntFlag):
    FAN_IN = 0x01
    FAN_OUT = 0x02
    HEATER = 0x04
    IONIZER = 0x08
    ULTRA_REPELLER = 0x10

class ConnectivityState(IntFlag):
    WIFI_CONNECTED = 0x10
    MQTT_SUBSCRIBED = 0x20
    OTA_IN_PROGRESS = 0x40
