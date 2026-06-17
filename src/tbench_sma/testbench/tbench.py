# tbench.py

import time
import struct
import re
import logging
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError

from tbench_sma.definitions import Device, DeviceAction, DeviceMode, Led, LedOperation, ApiCmd, ParFlags, SensorState, OutputState, ConnectivityState
from tbench_sma.logger import get_app_logger
from tbench_sma.core.ms_host import MShost

logger = get_app_logger(__name__)

class UUIDv4Validator(Validator):
    # Precompiled regex for UUID v4 (case-insensitive)
    uuid4_regex = re.compile(
        r'^[0-9a-fA-F]{8}-'
        r'[0-9a-fA-F]{4}-'
        r'4[0-9a-fA-F]{3}-'
        r'[89abAB][0-9a-fA-F]{3}-'
        r'[0-9a-fA-F]{12}$'
    )

    def validate(self, document):
        text = document.text.strip()
        if not self.uuid4_regex.fullmatch(text):
            raise ValidationError(
                message='Invalid UUIDv4. Expected format: 8-4-4-4-12 hex characters (version 4 only).',
                cursor_position=len(document.text)
            )

class TestBench:
    def __init__(self, config: dict):
        self.config = config
        self.tests = [
                (self.t_who_am_i, "Who Am I" ),
                (self.t_version, "Version" ),
                (self.t_testmode, "Test Mode" ),
                (self.t_sensors, "Sensors" ),
                (self.t_leds, "LEDs" ),
                (self.t_heater, "Heater" ),
                (self.t_ionizer, "Ionizer" ),
                (self.t_ultra_reppeler, "Ultra Repeller" ),
                (self.t_serialn, "Serial N")
        ]
        self.snonly = [
                (self.t_serialn, "Serial N")
        ]
        self.monitor = [
                (self.t_monitor, "Monitor")
        ]

        self.resetwifi = [ ]

    def set_ms_host(self, ms_host:MShost):
        self.ms_host = ms_host

    def ble_binding(self) -> bool :
        # Connect to BLE server, send Wifi, receive MAC
        # store MAC in config
        # subscribe MQTT
        # API_MQTT_READY

        # Replacement of above until it is coded with proper hardware BLE/serial module
        # Prompt the user for a UUID input with validation
        uuid = self.config["mqttms"]["ms"]["server_uuid"]
        if self.config["options"]["interactive"]:
            uuid = prompt('Enter a UUID: ', default=uuid, validator=UUIDv4Validator())
        logger.info("Using UUID: %s", uuid)
        self.config["mqttms"]["ms"]["server_uuid"] = uuid

        return True

    def ms_subscribe(self):
        # subscribe to server topics
        try:
            res = self.ms_host.ms_protocol.subscribe_all()
            if not res:
                logger.error("Cannot subscribe to MQTT broker: %d",res)
                return
        except Exception as e:
            logger.error("Cannot subscribe to MQTT broker: %s", e)
            return
        self.ms_host.ms_protocol.set_unsolicited_message_processor(unsolicited_handler_a)

    def run_tests(self):
        # Run the tests in sequence
        logger.info("TestBench.tests")

        self.ms_subscribe()

        match self.config["options"]["mode"]:
            case "snonly":
                testarray = self.snonly
            case "monitor":
                testarray = self.monitor
            case "testbench":
                testarray = self.tests
            case "reset-wifi":
                testarray = self.resetwifi

        if self.config['options']['pairing']:
            # This is called after successful binding and this command must be first one
            # to be sent to the server before API_MQTT_READY while the window for it open.
            if self.config['options']['resetwifi']:
                if not self.reset_wifi_credentials():
                    return

            payload = self.ms_host.ms_mqtt_ready()
            resp = payload.get("response","")
            if resp != "OK":
                logger.error("API_MQTT_READY received answer: {resp}")
                return

        for test in testarray:
            logger.info("")
            logger.info("**** Test %s ****",test[1])
            res = test[0]()
            if res:
                logger.info("**** Test %s: PASS",test[1])
            else:
                logger.info("**** Test %s: FAIL",test[1])
            if self.config['options']['stop_if_failed'] and not res:
                break

    def reset_wifi_credentials(self) -> bool:
        payload = self.ms_host.ms_wificred("*","*")
        if payload.get("response","") == "OK":
            logger.info("WiFi credentials successfully cleared")
            return True
        logger.info("WiFi credentials were not cleared")
        return False

    # tests

    def t_who_am_i(self) -> bool:
        payload = self.ms_host.ms_who_am_i()
        if payload.get("response","") == "OK":
            jdata = payload.get('data', None)
            format_string = '<B'
            bdata = bytes.fromhex(jdata)
            unpacked_data = struct.unpack(format_string, bdata)
            logger.info("Device ID: %02x",unpacked_data[0])
            return True
        return False

    def t_version(self) -> bool:
        payload = self.ms_host.ms_version()
        if payload.get("response","") == "OK":
            jdata = payload.get('data', None)
            byte_array = bytes.fromhex(jdata)
            version_bytes, serial_bytes = byte_array.split(b'\0',1)
            versiondev = version_bytes.decode('ascii')
            serial = serial_bytes.decode('ascii').rstrip('\x00')
            logger.info(f"Version: %s",versiondev)
            logger.info("Serial Number: %s",serial)
            return True
        return False

    def t_testmode(self) -> bool:
        payload = self.ms_host.ms_set_mode(DeviceMode.TEST)
        if payload.get("response","") == "OK":
            logger.info("Test mode is set")
            return True
        logger.info("Test mode was not set")
        return False

    def t_sensors(self) -> bool:
        payload = self.ms_host.ms_sensors()
        return True

    def t_leds(self) -> bool:
        for _ in range(2):
            for led in Led:
                payload = self.ms_host.ms_leds(LedOperation.ON, led)
                rsp = payload.get("response","")
                if rsp != "OK":
                    logger.info(f"Cannot set LED {led.name} to ON: %s", rsp)
                time.sleep(0.5)
                self.ms_host.ms_leds(LedOperation.OFF, led)
        return True

    def t_heater(self) -> bool:
        payload = self.ms_host.ms_output(Device.HEATER, DeviceAction.ON)
        rsp = payload.get("response","")
        if rsp != "OK":
            logger.info(f"Cannot set HEATER to ON: %s", rsp)
        time.sleep(1)
        payload = self.ms_host.ms_output(Device.HEATER, DeviceAction.OFF)
        rsp = payload.get("response","")
        if rsp != "OK":
            logger.info(f"Cannot set HEATER to OFF: %s", rsp)
        return True

    def t_ionizer(self) -> bool:
        payload = self.ms_host.ms_output(Device.IONIZER, DeviceAction.ON)
        rsp = payload.get("response","")
        if rsp != "OK":
            logger.info(f"Cannot set IONIZER to ON: %s", rsp)
        time.sleep(1)
        payload = self.ms_host.ms_output(Device.IONIZER, DeviceAction.OFF)
        rsp = payload.get("response","")
        if rsp != "OK":
            logger.info(f"Cannot set IONIZER to OFF: %s", rsp)
        return True

    def t_ultra_reppeler(self) -> bool:
        payload = self.ms_host.ms_output(Device.ULTRA_REPELLER, DeviceAction.ON)
        rsp = payload.get("response","")
        if rsp != "OK":
            logger.info(f"Cannot set ULTRA_REPELLER to ON: %s", rsp)
        time.sleep(1)
        payload = self.ms_host.ms_output(Device.ULTRA_REPELLER, DeviceAction.OFF)
        rsp = payload.get("response","")
        if rsp != "OK":
            logger.info(f"Cannot set ULTRA_REPELLER to OFF: %s", rsp)
        return True

    def t_serialn(self) -> bool:
        idn = self.config.get("dut").get("ident")
        serial_date = self.config.get("dut").get("serial_date")
        serialn = self.config.get("dut").get("serialn")
        serial_separator =  self.config.get("dut").get("serial_separator")
        snstr = idn + serial_separator + serial_date + serial_separator + serialn

        if self.config["options"]["interactive"]:
            snstr = prompt("Serial number: ", default=snstr)

        logger.info(" S/N: %s",snstr)

        payload = self.ms_host.ms_serial(snstr)
        if payload.get("response","") == "OK":
            logger.info("Serial number is written")
            return True

        logger.info("Serial number was not set")
        return False

    def t_monitor(self):
        logger.info("Press Ctrl+C to stop monitoring")
        logger.setLevel(logging.WARNING)
        logging.getLogger("tbench_sma.core.ms_host").setLevel(logging.WARNING)
        logging.getLogger("mqttms").setLevel(logging.WARNING)
        print('\n')
        try:
            count = 0
            lines = 0
            monitor_loops = self.config["options"]["monitor_loops"]
            while True:
                print(f"Monitoring loop: {count + 1}")
                lines = 1
                sensor_data = self.read_sensors()
                if sensor_data:
                    lines += self.print_sensor_data(sensor_data)
                else:
                    print("No valid data received")
                    lines += 1

                count += 1
                if monitor_loops != 0 and count >= monitor_loops:
                    break

                time.sleep(self.config["options"]["monitor_delay"])
                print(f"\033[{lines}A", end="", flush=True)
        except KeyboardInterrupt as e   :
            raise e
        finally:
            logger.setLevel(logging.INFO)
            logging.getLogger("tbench_sma.core.ms_host").setLevel(logging.INFO)
            logging.getLogger("mqttms").setLevel(logging.INFO)
            print('')
            logger.info("Monitoring stopped")

        return True

def unsolicited_handler_a(payload:dict) -> None:
    logger.info(f"Received unsolicited message: {payload}")