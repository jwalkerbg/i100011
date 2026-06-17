# app_runner.py

from importlib.metadata import version as pkg_version
#from time import time
import time
from typing import Dict, Tuple
from mqttms import MQTTDispatcher
from mqttms.core import MQTTms

import tbench_sma
from tbench_sma.core.config import Config
from tbench_sma.logger import get_app_logger
from tbench_sma.core.ms_host import MShost
from tbench_sma.testbench.tbench import TestBench

logger = get_app_logger(__name__)

class AppMQTTDispatcher(MQTTDispatcher):
    def __init__(self, config: Dict):
        super().__init__(config)

    def handle_message(self, message: Tuple[str, str]) -> bool:
        if not super().handle_message(message):
            logger.info("handle_message: -t '%s' -m '%s'", message[0], message[1])
            return True
        return False

# CLI application main function with collected options & configuration
def run_app(cfg:Config) -> None:
    try:
        # Add real application code here.
        logger.info("Running run_app")
        logger.info("config = %s",str(cfg.config))

        # Create testBench object
        tb = TestBench(cfg.config)

        # Step 1) BLE binding, exchange WIFi credentials / MAC address
        if cfg.config['options']['pairing']:
            if not tb.ble_binding():
                logger.error("Cannot bind with server via BLE")
                return

        # At this point:
        # Тhe server knows WiFi credentials and connects to MQTT broker
        # the client (this app) knows MAC address of the server

        # create MQTTms mqttms object to work with
        try:
            appdispatcher = AppMQTTDispatcher(cfg.config)
            mqttms = MQTTms(cfg.config['mqttms'],cfg.config['logging'],appdispatcher)
        except Exception as e:
            logger.error(f"Cannot create MQTTMS object. Giving up: {e}")
            return

        # connect broker
        try:
            res = mqttms.connect_mqtt_broker()
            if not res:
                mqttms.graceful_exit()
                return
        except Exception as e:
            mqttms.graceful_exit()
            logger.error(f"Cannot connect to MQTT broker: {e}.")
            return

        # create ms_host object if all above went well
        ms_host = MShost(ms_protocol=mqttms.ms_protocol,config=cfg.config)

        tb.set_ms_host(ms_host=ms_host)

        # Wait for a while to give the server chance to connect to WiFi and MQTT broker
        time.sleep(cfg.config['options']['dutdelay'])

        tb.run_tests()

    except KeyboardInterrupt:
        logger.warning("Application stopped by user (Ctrl-C). Exiting...")

    except ValueError as e:
        raise e
    except Exception as e:
        raise e
    finally:
        # Graceful exit on Ctrl-C
        if 'mqttms' in locals():
            mqttms.graceful_exit()
        logger.info("Exiting run_app")
