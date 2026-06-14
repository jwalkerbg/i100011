# tbench.py

import time
import struct
import re
import logging
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError

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

    def set_ms_host(self, ms_host:MShost):
        self.ms_host = ms_host

    def ms_subscribe(self):
        # subscribe to server topics
        try:
            res = self.ms_host.ms_protocol.subscribe()
            if not res:
                logger.error("Cannot subscribe to MQTT broker: %d",res)
                return
        except Exception as e:
            logger.error(f"Cannot subscribe to MQTT broker: {e}")
            return