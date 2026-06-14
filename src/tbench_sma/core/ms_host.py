# ms_host.py

import struct
from  mqttms import MSProtocol
from tbench_sma.logger import get_app_logger

logger = get_app_logger(__name__)

class MShost:
    def __init__(self, ms_protocol: MSProtocol, config):
        self.ms_protocol = ms_protocol
        self.config = config

    def ms_simple_command(self, cmd: str):
        payload = f'{{"command":"{cmd}","data":""}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_command_send_uint16(self, cmd: str, value: int):
        format_string = '<H'
        pd = struct.pack(format_string,value).hex()
        payload = f'{{"command":"{cmd}","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_command_send_uint8(self, cmd: str, value: int):
        format_string = '<B'
        pd = struct.pack(format_string,value).hex()
        payload = f'{{"command":"{cmd}","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_command_send_string(self, cmd: str, value: str):
        value_bytes = value.encode('ascii')
        data = value_bytes.hex()
        payload = f'{{"command":"{cmd}","data":"{data}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_who_am_i(self):
        return self.ms_simple_command("WH")

    def ms_nop(self):
        return self.ms_simple_command("NP")

    def ms_sensors(self):
        return self.ms_simple_command("SR")

    def ms_wificred(self, ssid: str, password: str):
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

    def ms_set_mode(self, mode: int):
        format_string = 'B'
        pd = struct.pack(format_string,mode).hex()
        payload = f'{{"command":"MD","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

# etc
