# ms_host.py

import struct
from  mqttms import MSProtocol
from tbench_sma.logger import get_app_logger

logger = get_app_logger(__name__)

class MShost:
    def __init__(self, ms_protocol: MSProtocol, config):
        self.ms_protocol = ms_protocol
        self.config = config

    def ms_simple_command(self, cmd: str) -> dict | None:
        payload = f'{{"command":"{cmd}","data":""}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_command_send_uint16(self, cmd: str, value: int) -> dict | None:
        format_string = '<H'
        pd = struct.pack(format_string,value).hex()
        payload = f'{{"command":"{cmd}","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_command_send_uint8(self, cmd: str, value: int) -> dict | None:
        format_string = '<B'
        pd = struct.pack(format_string,value).hex()
        payload = f'{{"command":"{cmd}","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_command_send_string(self, cmd: str, value: str) -> dict | None:
        value_bytes = value.encode('ascii')
        data = value_bytes.hex()
        payload = f'{{"command":"{cmd}","data":"{data}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_who_am_i(self) -> dict | None:
        return self.ms_simple_command("WH")

    def ms_nop(self) -> dict | None:
        return self.ms_simple_command("NP")

    def ms_sensors(self) -> dict | None:
        return self.ms_simple_command("SR")

    def ms_wificred(self, ssid: str, password: str) -> dict | None:
        ssid_bytes = ssid.encode('ascii')
        password_bytes = password.encode('ascii')
        data = bytearray(ssid_bytes) + b'\0' + bytearray(password_bytes)
        data = data.hex()
        payload = f'{{"command":"WF","data":"{data}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_set_mode(self, mode: int) -> dict | None:
        format_string = 'B'
        pd = struct.pack(format_string,mode).hex()
        payload = f'{{"command":"MD","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_getsmac(self) -> dict | None:
        return self.ms_simple_command("GM")

    def ms_set_amb_thr(self, value: int) -> dict | None:
        return self.ms_command_send_uint16("AH", value)

    def ms_set_co_thr(self, value: int) -> dict | None:
        return self.ms_command_send_uint16("CH", value)

    def ms_set_hum_thr(self, value: int) -> dict | None:
        return self.ms_command_send_uint16("HH", value)

    def ms_set_gas_thr(self, value: int) -> dict | None:
        return self.ms_command_send_uint16("GH", value)

    def ms_set_temp_thr(self, value: int) -> dict | None:
        return self.ms_command_send_uint16("TH", value)

    def ms_sensors_enable(self, sensor:int, operation:int) -> dict | None:
        pd = bytes([sensor, operation])
        payload = f'{{"command":"SE","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_outputs_enable(self, output:int, operation:int) -> dict | None:
        pd = bytes([output, operation])
        payload = f'{{"command":"OE","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_postventtime(self, value: int) -> dict | None:
        return self.ms_command_send_uint16("PT", value)

    def ms_postlighttime(self, value: int) -> dict | None:
        return self.ms_command_send_uint16("PL", value)

    def ms_co_interval(self, value: int) -> dict | None:
        return self.ms_command_send_uint16("CI", value)

    def ms_auto_times(self, vent_toggle_time: int, vent_pause_time: int) -> dict | None:
        pd = struct.pack('<HH', vent_toggle_time, vent_pause_time).hex()
        payload = f'{{"command":"AT","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_set_phases(self, phase1: int, phase2: int, phase3: int, phase4: int, phase5: int) -> dict | None:
        pd = struct.pack('<HHHHH', phase1, phase2, phase3, phase4, phase5).hex()
        payload = f'{{"command":"FX","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_set_speed(self, speed: int) -> dict | None:
        return self.ms_command_send_uint8("SX", speed)

    def ms_led_duties(self, duty0: int, duty1: int, duty2: int, duty3: int, duty4: int, operation: int) -> dict | None:
        # duty0-4: 0-1023
        # duty0 = blue
        # duty1 = green
        # duty2 = red
        # duty3 = yellow
        # duty4 = white
        # operation:
        # LED_DUTY_SET = set in RAM only,
        # LED_DUTY_DEFAULT = set in RAM and save to flash
        # LED_DUTY_STORE = save to flash and update RAM
        pd = struct.pack('<HHHHHB', duty0, duty1, duty2, duty3, duty4, operation).hex()
        payload = f'{{"command":"LD","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_get_params(self) -> dict | None:
        return self.ms_simple_command("PG")

    def ms_logs(self, log_level: int, log_module: int) -> dict | None:
        pd = struct.pack('<BB', log_level, log_module).hex()
        payload = f'{{"command":"LG","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_mqtt_ready(self) -> dict | None:
        return self.ms_simple_command("MQ")

    def ms_set_mqtt(self, broker: str) -> dict | None:
        broker_bytes = broker.encode('ascii')
        data = bytearray(broker_bytes)
        data = data.hex()
        payload = f'{{"command":"SQ","data":"{data}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_restart(self) -> dict | None:
        return self.ms_simple_command("RS")

    def ms_version(self) -> dict | None:
        return self.ms_simple_command("VS")

    def ms_serial(self, sn: str) -> dict | None:
        sn_bytes = sn.encode('ascii')
        data = sn_bytes.hex()
        payload = f'{{"command":"SN","data":"{data}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_output(self, output: int, operation: int) -> dict | None:
        pd = struct.pack('<BB', output, operation).hex()
        payload = f'{{"command":"OU","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_fan(self, fan: int, operation: int) -> dict | None:
        pd = struct.pack('<BB', fan, operation).hex()
        payload = f'{{"command":"FA","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_set_fan_phase(self, fan: int, phase: int) -> dict | None:
        pd = struct.pack('<BH', fan, phase).hex()
        payload = f'{{"command":"FF","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_fan_process(self, fan: int, operation: int, phase: int) -> dict | None:
        pd = struct.pack('<BBH', fan, operation, phase).hex()
        payload = f'{{"command":"FP","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_leds(self, operation: int, leds: int) -> dict | None:
        pd = struct.pack('<BB', operation, leds).hex()
        payload = f'{{"command":"LE","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_reset(self) -> dict | None:
        return self.ms_simple_command("RE")

    def ms_ota_update(self, url: str) -> dict | None:
        url_bytes = url.encode('ascii')
        data = bytearray(url_bytes)
        data = data.hex()
        payload = f'{{"command":"OT","data":"{data}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_ota_update_version_only(self, version: str) -> dict | None:
        version_bytes = version.encode('ascii')
        data = bytearray(version_bytes)
        data = data.hex()
        payload = f'{{"command":"OV","data":"{data}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_setbaseurl(self, url: str) -> dict | None:
        url_bytes = url.encode('ascii')
        data = bytearray(url_bytes)
        data = data.hex()
        payload = f'{{"command":"SB","data":"{data}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_timezone(self, tz:str) -> dict | None:
        return self.ms_command_send_string("TZ", tz)
