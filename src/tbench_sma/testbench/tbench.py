# tbench.py

import threading
import time
from datetime import datetime, UTC
import struct
import queue
import re
import json
import yaml
from pathlib import Path
import logging
from dataclasses import dataclass, field, asdict
from typing import Any
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError

from tbench_sma.definitions import Device, DeviceAction, DeviceMode, Led, LedOperation
from tbench_sma.core.config import Config, ConfigDict
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

    def validate(self, document) -> None:
        text = document.text.strip()
        if not self.uuid4_regex.fullmatch(text):
            raise ValidationError(
                message='Invalid UUIDv4. Expected format: 8-4-4-4-12 hex characters (version 4 only).',
                cursor_position=len(document.text)
            )

class TestBench:

    # class variables because they will be used in static method unsolicited_handler
    button_event = threading.Event()
    ir_event = threading.Event()
    dev_state_event = threading.Event()
    kbd_q: queue.Queue = queue.Queue()
    ir_q: queue.Queue = queue.Queue()
    devstate_q: queue.Queue = queue.Queue()

    def __init__(self, config: ConfigDict):
        self.config = config
        self.tests = [
                (self.t_who_am_i, "Who Am I" ),
                (self.t_version, "Version" ),
                (self.t_testmode, "Test Mode" ),
                (self.t_sensors, "Sensors" ),
                (self.t_kbd_ir, "Keyboard & IR"),
                (self.t_leds, "LEDs" ),
                (self.t_heater, "Heater" ),
                (self.t_ionizer, "Ionizer" ),
                (self.t_ultra_reppeler, "Ultra Repeller" ),
                (self.t_fan_in, "Fan In" ),
                (self.t_fan_out, "Fan Out" ),
                (self.t_serialn, "Serial N")
        ]
        self.snonly = [
                (self.t_serialn, "Serial N")
        ]
        self.monitor = [
                (self.t_monitor, "Monitor")
        ]

        self.resetwifi = [ ]

        #self.ms_host: MShost = None

    def set_ms_host(self, ms_host:MShost) -> None:
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

    def ms_subscribe(self) -> None:
        # subscribe to server topics
        try:
            res = self.ms_host.ms_protocol.subscribe_all()
            if not res:
                logger.error("Cannot subscribe to MQTT broker: %d",res)
                return
        except Exception as e:
            logger.error("Cannot subscribe to MQTT broker: %s", str(e), exc_info=self.config.config['logging']['exc_full_stack'])
            return
        self.ms_host.ms_protocol.set_unsolicited_message_processor(TestBench.unsolicited_handler)

    def run_tests(self) -> None:
        # Run the tests in sequence
        logger.info("TestBench.tests")

        self.ms_subscribe()

        self.report = TestReport(uuid=self.config["mqttms"]["ms"]["server_uuid"],
                                 reppath=self.config["report"]["report_path"])

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
                logger.error("API_MQTT_READY received answer: %s", resp)
                return

        self.report.create_prolog()

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

        self.report.add_epilog()
        self.report.dump_data()
        self.report.save_report(self.config)

    def reset_wifi_credentials(self) -> bool:
        payload = self.ms_host.ms_wificred("*","*")
        if payload.get("response","") == "OK":
            logger.info("WiFi credentials successfully cleared")
            return True
        logger.info("WiFi credentials were not cleared")
        return False

    # tests

    def t_who_am_i(self) -> bool:
        tc = TestCase("t_who_am_i")

        payload = self.ms_host.ms_who_am_i()
        if payload.get("response","") == "OK":
            jdata = payload.get('data', None)
            format_string = '<B'
            bdata = bytes.fromhex(jdata)
            unpacked_data = struct.unpack(format_string, bdata)
            logger.info("Device ID: %02x",unpacked_data[0])
            tc.result = True
            tc.data['Device code'] = unpacked_data[0]
            self.report.add_test_data(tc)
            return True

        tc.result = False
        tc.data['code'] = 0
        self.report.add_test_data(tc)
        return False

    def t_version(self) -> bool:
        tc = TestCase("t_version")
        payload = self.ms_host.ms_version()
        if payload.get("response","") == "OK":
            jdata = payload.get('data', None)
            byte_array = bytes.fromhex(jdata)
            version_bytes, serial_bytes = byte_array.split(b'\0',1)
            versiondev = version_bytes.decode('ascii')
            serial = serial_bytes.decode('ascii').rstrip('\x00')
            logger.info("Version: %s",versiondev)
            logger.info("Serial Number: %s",serial)

            tc.result = True
            tc.data['version'] = versiondev
            tc.data['serialn'] = serial
            self.report.add_test_data(tc)
            return True

        tc.result = False
        self.report.add_test_data(tc)
        return False

    def t_testmode(self) -> bool:
        tc = TestCase("t_testmode")
        payload = self.ms_host.ms_set_mode(DeviceMode.TEST)
        if payload.get("response","") == "OK":
            logger.info("Test mode is set")
            tc.result = True
            tc.data['action'] = "Test mode was set"
            self.report.add_test_data(tc)
            return True
        logger.info("Test mode was not set")
        tc.result = False
        tc.data['action'] = "Test mode was not set"
        self.report.add_test_data(tc)
        return False

    def t_sensors(self) -> bool:
        tc = TestCase("t_sensors")
        TestBench.dev_state_event.clear()

        payload = self.ms_host.ms_sensors()
        if payload.get("response","") == "OK":
            logger.info("Sensors command was sent")

            deadline = time.monotonic() + 5.0
            while time.monotonic() < deadline:
                if TestBench.dev_state_event.is_set():
                    uslp = TestBench.devstate_q.get()

                    raw = (
                        uslp.get("data", {})
                            .get("sensors", {})
                            .get("raw", {})
                    )
                    tc.data.update(raw)

                    tc.result = True
                    self.report.add_test_data(tc)
                    return True

        tc.result = False
        self.report.add_test_data(tc)
        return False

    def t_leds(self) -> bool:
        tc = TestCase("t_leds")
        res = True
        for _ in range(1):
            for led in Led:
                payload = self.ms_host.ms_leds(LedOperation.ON, led)
                rsp = payload.get("response","")
                if rsp == "OK":
                    tc.data[led.name + " set"] = "PASS"
                else:
                    logger.info(f"Cannot set LED {led.name} to ON: %s", rsp)
                    tc.data[led.name + " set"] = "FAIL"
                    res = False

                time.sleep(0.5)

                self.ms_host.ms_leds(LedOperation.OFF, led)
                if rsp == "OK":
                    tc.data[led.name + " clear"] = "PASS"
                else:
                    logger.info(f"Cannot clear LED {led.name} to ON: %s", rsp)
                    tc.data[led.name + " clear"] = "FAIL"
                    res = False

        tc.result = res
        self.report.add_test_data(tc)
        return res

    def t_heater(self) -> bool:
        tc = TestCase("t_heater")
        res = True
        heateron = self.config.get("tests").get("heateron", 3.0)
        payload = self.ms_host.ms_output(Device.HEATER, DeviceAction.ON)
        rsp = payload.get("response","")
        if rsp == "OK":
            logger.info("HEATER was to set to ON: %s", rsp)
            tc.data['heater on:'] = "PASS"
        else:
            logger.info("HEATER was not set to ON: %s", rsp)
            tc.data['heater on:'] = "FAIL"
            res = False

        time.sleep(heateron)

        payload = self.ms_host.ms_output(Device.HEATER, DeviceAction.OFF)
        rsp = payload.get("response","")
        if rsp == "OK":
            logger.info("HEATER was to set to OFF: %s", rsp)
            tc.data['heater off:'] = "PASS"
        else:
            logger.info("HEATER was not set to OFF: %s", rsp)
            tc.data['heater off:'] = "FAIL"
            res = False

        tc.result = res
        self.report.add_test_data(tc)
        return True

    def t_ionizer(self) -> bool:
        tc = TestCase("t_ionizer")
        res = True
        ionizeron = self.config.get("tests").get("ionizeron", 3.0)
        payload = self.ms_host.ms_output(Device.IONIZER, DeviceAction.ON)
        rsp = payload.get("response","")
        if rsp == "OK":
            logger.info("IONIZER was set to ON: %s", rsp)
            tc.data['ionizer on:'] = "PASS"
        else:
            logger.info("IONIZER was not set to ON: %s", rsp)
            tc.data['ionizer on:'] = "FAIL"
            res = False

        time.sleep(ionizeron)

        payload = self.ms_host.ms_output(Device.IONIZER, DeviceAction.OFF)
        rsp = payload.get("response","")
        if rsp == "OK":
            logger.info("IONIZER was set to OFF: %s", rsp)
            tc.data['ionizer on:'] = "PASS"
        else:
            logger.info("IONIZER was not set to OFF: %s", rsp)
            tc.data['ionizer on:'] = "FAIL"
            res = False

        tc.result = res
        self.report.add_test_data(tc)
        return True

    def t_ultra_reppeler(self) -> bool:
        tc = TestCase("t_ultra_reppeler")
        res = True
        repelleron = self.config.get("tests").get("repelleron", 3.0)
        payload = self.ms_host.ms_output(Device.ULTRA_REPELLER, DeviceAction.ON)
        rsp = payload.get("response","")
        if rsp == "OK":
            logger.info("ULTRA_REPELLER was set to ON: %s", rsp)
            tc.data['repeller on:'] = "PASS"
        else:
            logger.info("ULTRA_REPELLER was set to ON: %s", rsp)
            tc.data['repeller on:'] = "FAIL"
            res = False

        time.sleep(repelleron)

        payload = self.ms_host.ms_output(Device.ULTRA_REPELLER, DeviceAction.OFF)
        rsp = payload.get("response","")
        if rsp == "OK":
            logger.info("ULTRA_REPELLER was set to OFF: %s", rsp)
            tc.data['repeller off:'] = "PASS"
        else:
            logger.info("ULTRA_REPELLER was set to OFF: %s", rsp)
            tc.data['repeller off:'] = "FAIL"
            res = False

        tc.result = res
        self.report.add_test_data(tc)
        return True

    def t_kbd_ir(self) -> bool:
        tc = TestCase("t_kbd_ir")
        res = True
        TestBench.button_event.clear()
        TestBench.ir_event.clear()

        print("Press shortly local button and any IR RC button in 10 seconds\n")
        buttontime = self.config.get("tests").get("buttontime", 10.0)
        deadline = time.monotonic() + buttontime
        while time.monotonic() < deadline:
            if TestBench.button_event.is_set() and TestBench.ir_event.is_set():
                break
            time.sleep(0.1)

        btnres = TestBench.button_event.is_set()
        irres = TestBench.ir_event.is_set()
        if btnres:
            logger.info("Button event has been received. Button test passed.")
            kbdp = TestBench.kbd_q.get()
            tc.data['kbd_event'] = kbdp.get("data", {}).get("event","")
            tc.data['button'] = "PASS"
        else:
            logger.info("Button event has not been received. Button test failed.")
            tc.data['Button'] = "FAIL"
            res = False
        if irres:
            logger.info("IR event has been received. IR test passed.")
            irp = TestBench.ir_q.get()
            tc.data['ir_event'] = irp.get("data", {}).get("event","")
            tc.data['ir'] = "PASS"
        else:
            logger.info("IR event has not been received. IR test failed.")
            tc.data['ir'] = "FAIL"
            res = False

        tc.result = res
        self.report.add_test_data(tc)
        return btnres and irres

    def t_fan_in(self) -> bool:
        tc = TestCase("t_fan_in")
        res = True
        motoron = self.config.get("tests").get("motoron", 3.0)
        motoroff = self.config.get("tests").get("motoroff", 1.0)
        payload = self.ms_host.ms_fan_process(Device.FAN_IN, DeviceAction.ON,5000)
        rsp = payload.get("response","")
        if rsp == "OK":
            logger.info("FAN IN was set to ON: %s", rsp)
            tc.data['fan in on:'] = "PASS"
        else:
            logger.info("FAN IN was not set to ON: %s", rsp)
            tc.data['fan in on:'] = "FAIL"
            res = False

        time.sleep(motoron)

        payload = self.ms_host.ms_fan_process(Device.FAN_IN, DeviceAction.OFF,5000)
        rsp = payload.get("response","")
        if rsp == "OK":
            logger.info("FAN IN was set to OFF: %s", rsp)
            tc.data['fan in off:'] = "PASS"
        else:
            logger.info("FAN IN was not set to OFF: %s", rsp)
            tc.data['fan in off:'] = "FAIL"
            res = False

        time.sleep(motoroff)

        tc.result = res
        self.report.add_test_data(tc)
        return res

    def t_fan_out(self) -> bool:
        tc = TestCase("t_fan_out")
        res = True
        motoron = self.config.get("tests").get("motoron", 3.0)
        motoroff = self.config.get("tests").get("motoroff", 1.0)
        payload = self.ms_host.ms_fan_process(Device.FAN_OUT, DeviceAction.ON,5000)
        rsp = payload.get("response","")
        if rsp == "OK":
            logger.info("FAN OUT was set to ON: %s", rsp)
            tc.data['fan out on:'] = "PASS"
        else:
            logger.info("FAN OUT was not set to ON: %s", rsp)
            tc.data['fan out on:'] = "FAIL"
            res = False

        time.sleep(motoron)

        payload = self.ms_host.ms_fan_process(Device.FAN_OUT, DeviceAction.OFF,5000)
        rsp = payload.get("response","")
        if rsp == "OK":
            logger.info("FAN OUT was set to OFF: %s", rsp)
            tc.data['fan out off:'] = "PASS"
        else:
            logger.info("FAN OUT was not set to OFF: %s", rsp)
            tc.data['fan out off:'] = "FAIL"
            res = False

        time.sleep(motoroff)

        tc.result = res
        self.report.add_test_data(tc)
        return res

    def t_serialn(self) -> bool:
        tc = TestCase("t_serialn")
        res = True
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
            logger.info("Serial number \'%s\'is written",snstr)
            tc.data['serialn'] = snstr
            self.report.serialn = snstr
        else:
            logger.info("Serial number was not set")
            tc.data['serialn'] = "not set"
            res = False

        tc.result = res
        self.report.add_test_data(tc)
        return res

    def t_monitor(self) -> bool:
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
        except KeyboardInterrupt as e:
            raise e
        finally:
            logger.setLevel(logging.INFO)
            logging.getLogger("tbench_sma.core.ms_host").setLevel(logging.INFO)
            logging.getLogger("mqttms").setLevel(logging.INFO)
            print('')
            logger.info("Monitoring stopped")

        return True

    @staticmethod
    def unsolicited_handler(payload:dict) -> None:
        logger.info("Received unsolicited message %s", json.dumps(payload, separators=(",", ":")))

        if isinstance(payload, dict):
            if payload.get("src") == "keyboard":
                logger.info("Received keyboard event: %s",payload.get("data",{}).get("event",""))
                TestBench.kbd_q.put(payload)
                TestBench.button_event.set()
            if payload.get("src") == "ir":
                logger.info("Received IR event: %s",payload.get("data",{}).get("event",""))
                TestBench.ir_q.put(payload)
                TestBench.ir_event.set()
            if payload.get("src") == "system" and payload.get("type") == "devstate":
                TestBench.devstate_q.put(payload)
                TestBench.dev_state_event.set()

@dataclass
class TestCase:
    name: str
    result: bool = False

    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )

    data: dict[str, Any] = field(default_factory=dict)

@dataclass
class TestReport:
    uuid: str = ""
    reppath: str = ""
    serialn: str = ""
    timestamp: str = ""
    test_results: list = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    total: int = 0
    result: bool = True

    def create_prolog(self) -> None:
        self.timestamp = datetime.now(UTC).isoformat()

    def add_test_data(self, tc: TestCase) -> None:
        if tc is not None:
            self.test_results.append(asdict(tc))

    def add_epilog(self) -> None:
        tests = self.test_results
        passed = sum(
            1 for t in tests
            if t.get("result") is True
        )
        failed = sum(
            1 for t in tests
            if t.get("result") is False
        )
        self.passed = passed
        self.failed = failed
        self.total = len(tests)
        self.skipped = len(tests) - passed - failed

    def dump_data(self) -> None:
        print("\n=== TEST REPORT ===")
        print(f"Passed : {self.passed}")
        print(f"Failed : {self.failed}")
        print(f"Total  : {self.total}")

        print("\n=== DETAILS ===")
        for test in self.test_results:
            status = "PASS" if test.get("result") else "FAIL"
            print(f"{status:4} {test.get('name')}")

        print("\n=== JSON ===")
        print(json.dumps(asdict(self), indent=2))

    def to_dict(self):
        return asdict(self)

    def build_report_path(self, fmt: str) -> Path:
        ext = "json" if fmt == "json" else "yaml"
        return Path(self.reppath) / f"{self.uuid}.{ext}"

    def to_json(self):
        path = self.build_report_path("json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)
        return path

    def to_yaml(self):
        path = self.build_report_path("yaml")
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.to_dict(), f, sort_keys=False)
        return path

    def save_report(self, config: dict):
        if config['report']['save_report'] == False:
            return

        if config['report']['report_dest'] == "db":
            logger.verbose("Save report to database is not implemented")

        if config['report']['report_dest'] == "file":
            if config['report']['report_format'] == 'json':
                self.to_json()
            if config['report']['report_format'] == 'yaml':
                self.to_yaml()
