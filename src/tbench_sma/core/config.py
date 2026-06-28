# core/config.py

import os
import sys
from typing import Dict, Any, Mapping, TypedDict
import argparse
from jsonschema import validate, ValidationError

from tbench_sma.logger import get_app_logger

logger = get_app_logger(__name__)

# Check Python version at runtime
if sys.version_info >= (3, 11):
    import tomllib as toml # Use the built-in tomllib for Python 3.11+
else:
    import tomli as toml # Use the external tomli for Python 3.7 to 3.10

class TemplateConfig(TypedDict, total=False):
    template_name: str
    template_version: str
    template_description: Dict[str, Any]

class LoggingConfig(TypedDict, total=False):
    verbose: int
    log_prefix: bool
    use_color: bool
    use_string_handler: bool
    version_option: bool
    exc_full_stack: bool

class MqttmsConfig(TypedDict, total=False):
    mqtt: Dict[str, Any]
    ms: Dict[str, Any]

class DutConfig(TypedDict, total=False):
    ident: str
    name: str
    serial_date: str
    serialn: str
    serial_separator: str

class TestsConfig(TypedDict, total=False):
    motoron: float
    motoroff: float
    heateron: float
    ionizeron: float
    repelleron: float
    buttontime: float
    amb_thr: float
    amb_low: float
    amb_high: float
    co_thr: float
    co_low: float
    co_max: float
    temp_thr: float
    temp_low: float
    temp_high: float
    press_thr: float
    press_low: float
    press_high: float
    hum_thr: float
    hum_low: float
    hum_high: float
    air_thr: float
    air_low : float
    air_high: float

class OptionsConfig(TypedDict, total=False):
    mode: str
    monitor_delay: float
    monitor_loops: float
    dutdelay: float
    interactive: bool
    pairing: bool
    resetwifi: bool
    stop_if_failed: bool

class ReportConfig(TypedDict, total=False):
    save_report: bool
    report_format: str
    report_dest: str
    report_path: str

class ConfigDict(TypedDict):
    template: TemplateConfig
    logging: LoggingConfig
    mqttms: MqttmsConfig
    dut: DutConfig
    tests: TestsConfig
    options: OptionsConfig
    report: ReportConfig

class Config:
    def __init__(self) -> None:
        self.config: ConfigDict = self.DEFAULT_CONFIG

    DEFAULT_CONFIG: ConfigDict = {
        'template': {
            'template_name': "tbench_sma",
            'template_version': "4.2.0",
            'template_description': { 'text': """Template with CLI interface, configuration options in a file, logger and unit tests""", 'content-type': "text/plain" }
        },
        'logging': {
            'verbose': 3,
            'log_prefix': True,
            'use_color': True,
            'use_string_handler': False,
            'version_option': False,
            'exc_full_stack': False
        },
        'mqttms': {
            'mqtt': {
                'host': 'localhost',
                'port': 1883,
                'username': 'guest',
                'password': 'guest',
                'client_id': 'mqttx_93919c20',
                'timeout': 15.0,
                'long_payload': 25
            },
            'ms': {
                'client_uuid': 'e6f87d77-4216-4be1-ab83-b5fa6792b747',
                'server_uuid': '4fdc0d1f-2421-4b5b-975b-9b4d0a08d712',
                'cmd_topic': '@/server_uuid/CMD/format',
                'subs_topics': [
                    {
                        'topic': '@/server_uuid/RSP/format',
                        'format': 'ASCIIHEX'
                    },
                    {
                        'topic': '@/server_uuid/USL/format',
                        'format': 'JSON'
                    }
                ],
                'timeout': 5.0
            }
        },
        "dut": {
            "ident": "999999",
            "name": "device",
            "serial_date": "2501",
            "serialn": "0000001",
            "serial_separator": "-"
        },
        "tests": {
            "motoron": 3.0,
            "motoroff": 1.0,
            "heateron": 3.0,
            "ionizeron": 3.0,
            "repelleron": 3.0,
            "buttontime": 10.0,
            "amb_thr": 750.0,
            "amb_low": 0.0,
            "amb_high": 2000.0,
            "co_thr": 9,
            "co_low": 0,
            "co_max": 1200,
            "temp_thr": 2300,
            "temp_low": 0,
            "temp_high": 4500,
            "press_thr": 99000,
            "press_low": 60000,
            "press_high": 110000,
            "hum_thr": 75000,
            "hum_low": 0,
            "hum_high": 100000,
            "air_thr": 16000,
            "air_low": 500,
            "air_high": 100000
        },
        "options": {
            "mode": "testbench",
            "monitor_delay": 2.0,
            "monitor_loops": 10,
            "dutdelay": 2.0,
            "interactive": True,
            "pairing": False,
            "resetwifi": True,
            "stop_if_failed": False
        },
        "report": {
            "save_report": False,
            "report_format": "json",
            "report_dest": "file",
            "report_path": "reports"
        }
    }

    # When adding / removing changing configuration parameters, change following validation appropriately
    CONFIG_SCHEMA = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "logging": {
                "type": "object",
                "properties": {
                    "verbose": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 6
                    },
                    "log_prefix": {
                        "type": "boolean"
                    },
                    "use_color": {
                        "type": "boolean"
                    },
                    "use_string_handler": {
                        "type": "boolean"
                    },
                    "version_option": {
                        "type": "boolean"
                    },
                    "exc_full_stack": {
                        "type": "boolean"
                    }
                },
                "additionalProperties": False
            },
            "mqttms": {
                "type": "object",
                "properties": {
                    "mqtt": {
                        "type": "object",
                        "properties": {
                            "host": {"type": "string"},
                            "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                            "username": {"type": "string"},
                            "password": {"type": "string"},
                            "client_id": {"type": "string"},
                            "timeout": {"type": "number"},
                            "long_payload": {"type": "integer", "minimum": 10, "maximum": 32768}
                        },
                        "required": ["host", "port"]
                    },
                    "ms": {
                        "type": "object",
                        "properties": {
                            "client_uuid": {"type": "string"},
                            "server_uuid": {"type": "string"},
                            "cmd_topic": {"type": "string"},
                            "subs_topics": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "topic": {
                                            "type": "string"
                                        },
                                        "format": {
                                            "type": "string",
                                            "enum": ["BINARY", "ASCIIHEX", "ASCII", "JSON" ]
                                        }
                                    },
                                    "required": ["topic", "format"],
                                    "additionalProperties": False
                                },
                                "minItems": 1,
                                "uniqueItems": True
                            }
                        },
                        "timeout": {"type": "number", "minimum": 0.1, "maximum": 60.0},
                        "required": ["client_uuid", "server_uuid", "cmd_topic", "subs_topics", "timeout"]
                    }
                },
                "required": ["mqtt", "ms"],
                "additionalProperties": False
            },
            "dut" :{
                "type": "object",
                "properties": {
                    "ident": { "type": "string"},
                    "name": { "type": "string" },
                    "serial_date": { "type": "string"},
                    "serialn": { "type": "string"},
                    "serial_separator": { "type": "string" }
                }
            },
            "tests": {
                "type": "object",
                "properties": {
                    "motoron": {"type": "number"},
                    "motoroff": {"type": "number"},
                    "heateron": {"type": "number"},
                    "ionizeron": {"type": "number"},
                    "repelleron": {"type": "number"},
                    "buttontime": {"type": "number"},
                    "amb_thr": {"type": "number"},
                    "amb_low": {"type": "number"},
                    "amb_high": {"type": "number"},
                    "co_thr": {"type": "number"},
                    "co_low": {"type": "number"},
                    "co_max": {"type": "number"},
                    "temp_thr": {"type": "number"},
                    "temp_low": {"type": "number"},
                    "temp_high": {"type": "number"},
                    "press_thr": {"type": "number"},
                    "press_low": {"type": "number"},
                    "press_high": {"type": "number"},
                    "hum_thr": {"type": "number"},
                    "hum_low": {"type": "number"},
                    "hum_high": {"type": "number"},
                    "air_thr": {"type": "number"},
                    "air_low": {"type": "number"},
                    "air_high": {"type": "number"}
                }
            },
            "options": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string"},
                    "monitor_delay": {"type": "number"},
                    "monitor_loops": {"type": "integer"},
                    "dutdelay": {"type": "number"},
                    "interactive": {"type": "boolean"},
                    "pairing": {"type": "boolean"},
                    "resetwifi": {"type": "boolean"},
                    "stop_if_failed": {"type": "boolean"}
                }
            },
            "report": {
                "type": "object",
                "properties": {
                    "save_report": {"type": "boolean"},
                    "report_format": {
                        "type": "string",
                        "enum": ["json", "yaml"]
                    },
                    "report_dest": {
                        "type": "string",
                        "enum": ["file", "db"]
                    },
                    "report_path": {
                        "type": "string"
                    }
                }
            }
        },
        "additionalProperties": False
    }

    def load_toml(self,file_path:str) -> Dict[str, Any]:
        """
        Load a TOML file with exception handling.

        :param file_path: Path to the TOML file
        :return: Parsed TOML data as a dictionary
        :raises FileNotFoundError: If the file does not exist
        :raises tomli.TOMLDecodeError / tomllib.TOMLDecodeError: If there is a parsing error
        """
        try:
            # Open the file in binary mode (required by both tomli and tomllib)
            with open(file_path, 'rb') as f:
                return toml.load(f)

        except FileNotFoundError as e:
            raise e  # Optionally re-raise the exception if you want to propagate it
        except toml.TOMLDecodeError as e:
            raise e  # Re-raise the exception for further handling
        except Exception as e:
            raise e  # Catch-all for any other unexpected exceptions

    def load_config_file(self, file_path: str="config.toml") -> Dict[str, Any]:
        # skip the configuration file if an empty name is given
        if file_path == '':
            return {}
        # Convert None to default value of 'config.json'
        if file_path == "config.toml":
            logger.warning("CFG: Using default '%s'",file_path)
            file_path = 'config.toml'
        try:
            config_file = self.load_toml(file_path=file_path)
            validate(instance=config_file, schema=self.CONFIG_SCHEMA)
        except ValidationError as e:
            raise ValidationError(f"Configuration file validation error: {e}") from e
        except Exception as e:
            raise e

        self.deep_update(config=self.config, config_file=config_file)

        return config_file

    def deep_update(self,config:Mapping[str, Any], config_file: Dict[str, Any]) -> None:
        """
        Recursively updates a dictionary (`config`) with the contents of another dictionary (`config_file`).
        It performs a deep merge, meaning that if a key contains a nested dictionary in both `config`
        and `config_file`, the nested dictionaries are merged instead of replaced.

        Parameters:
        - config (Dict[str, Any]): The original dictionary to be updated.
        - config_file (Dict[str, Any]): The dictionary containing updated values.

        Returns:
        - None: The update is done in place, so the `config` dictionary is modified directly.
        """
        for key, value in config_file.items():
            if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                # If both values are dictionaries, recurse to merge deeply
                self.deep_update(config[key], value)
            else:
                # Otherwise, update the key with the new value from config_file if it is present there
                if value is not None:
                    config[key] = value

    def load_config_env(self) -> ConfigDict:
        """
        Load configuration from environment variables.

        :return: Updated configuration dictionary
        """
        env_overrides = {
            "report": {
                "report_path": os.getenv("SMA_REPORT_PATH")
            }
        }
        self.deep_update(config=self.config, config_file=env_overrides)

        return self.config

    def merge_cli_options(self, config_cli: argparse.Namespace | None = None) -> ConfigDict:    # pylint: disable=too-many-branches
        # handle CLI options if started from CLI interface
        # replace param1 and param2 with actual parameters, defined in app:parse_args()
        if config_cli:

            if config_cli.version_option is not None:
                self.config['logging']['version_option'] = config_cli.version_option

            # Handle general options
            if config_cli.verbose is not None:
                self.config['logging']['verbose'] = config_cli.verbose
            if config_cli.log_prefix is not None:
                self.config['logging']['log_prefix'] = config_cli.log_prefix
            if config_cli.use_color is not None:
                self.config['logging']['use_color'] = config_cli.use_color
            if config_cli.use_string_handler is not None:
                self.config['logging']['use_string_handler'] = config_cli.use_string_handler
            if config_cli.exc_full_stack is not None:
                self.config['logging']['exc_full_stack'] = config_cli.exc_full_stack

        # Handle MQTT CLI overrides
            if config_cli.mqtt_host is not None:
                self.config['mqttms']['mqtt']['host'] = config_cli.mqtt_host
            if config_cli.mqtt_port is not None:
                self.config['mqttms']['mqtt']['port'] = config_cli.mqtt_port
            if config_cli.mqtt_username is not None:
                self.config['mqttms']['mqtt']['username'] = config_cli.mqtt_username
            if config_cli.mqtt_password is not None:
                self.config['mqttms']['mqtt']['password'] = config_cli.mqtt_password
            if config_cli.mqtt_client_id is not None:
                self.config['mqttms']['mqtt']['client_id'] = config_cli.mqtt_client_id
            if config_cli.mqtt_timeout is not None:
                self.config['mqttms']['mqtt']['timeout'] = config_cli.mqtt_timeout
            if config_cli.long_payload is not None:
                self.config['mqttms']['mqtt']['long_payload'] = config_cli.long_payload

            # handle ms protocol overrides
            if config_cli.ms_client_uuid is not None:
                self.config['mqttms']['ms']['client_uuid'] = config_cli.ms_client_uuid
            if config_cli.ms_server_uuid is not None:
                self.config['mqttms']['ms']['server_uuid'] = config_cli.ms_server_uuid
            if config_cli.ms_cmd_topic is not None:
                self.config['mqttms']['ms']['cmd_topic'] = config_cli.ms_cmd_topic
            if config_cli.ms_rsp_topic is not None:
                self.config['mqttms']['ms']['rsp_topic'] = config_cli.ms_rsp_topic
            if config_cli.ms_timeout is not None:
                self.config['mqttms']['ms']['timeout'] = config_cli.ms_timeout

            # dut options
            if config_cli.dut_ident is not None:
                self.config['dut']['ident'] = config_cli.dut_ident
            if config_cli.dut_name is not None:
                self.config['dut']['name'] = config_cli.dut_name
            if config_cli.dut_serial_date is not None:
                self.config['dut']['serial_date'] = config_cli.dut_serial_date
            if config_cli.dut_serialn is not None:
                self.config['dut']['serialn'] = config_cli.dut_serialn
            if config_cli.serial_separator is not None:
                self.config['dut']['serial_separator'] = config_cli.serial_separator

            # test options
            if config_cli.motoron is not None:
                self.config['tests']['motoron'] = config_cli.motoron
            if config_cli.motoroff is not None:
                self.config['tests']['motoroff'] = config_cli.motoroff
            if config_cli.heateron is not None:
                self.config['tests']['heateron'] = config_cli.heateron
            if config_cli.ionizeron is not None:
                self.config['tests']['ionizeron'] = config_cli.ionizeron
            if config_cli.repelleron is not None:
                self.config['tests']['repelleron'] = config_cli.repelleron
            if config_cli.buttontime is not None:
                self.config['tests']['buttontime'] = config_cli.buttontime
            if config_cli.amb_thr is not None:
                self.config['tests']['amb_thr'] = config_cli.amb_thr
            if config_cli.amb_low is not None:
                self.config['tests']['amb_low'] = config_cli.amb_low
            if config_cli.amb_high is not None:
                self.config['tests']['amb_high'] = config_cli.amb_high
            if config_cli.co_thr is not None:
                self.config['tests']['co_thr'] = config_cli.co_thr
            if config_cli.co_low is not None:
                self.config['tests']['co_low'] = config_cli.co_low
            if config_cli.co_max is not None:
                self.config['tests']['co_max'] = config_cli.co_max
            if config_cli.temp_thr is not None:
                self.config['tests']['temp_thr'] = config_cli.temp_thr
            if config_cli.temp_low is not None:
                self.config['tests']['temp_low'] = config_cli.temp_low
            if config_cli.temp_high is not None:
                self.config['tests']['temp_high'] = config_cli.temp_high
            if config_cli.press_thr is not None:
                self.config['tests']['press_thr'] = config_cli.press_thr
            if config_cli.press_low is not None:
                self.config['tests']['press_low'] = config_cli.press_low
            if config_cli.press_high is not None:
                self.config['tests']['press_high'] = config_cli.press_high
            if config_cli.hum_thr is not None:
                self.config['tests']['hum_thr'] = config_cli.hum_thr
            if config_cli.hum_low is not None:
                self.config['tests']['hum_low'] = config_cli.hum_low
            if config_cli.hum_high is not None:
                self.config['tests']['hum_high'] = config_cli.hum_high
            if config_cli.air_thr is not None:
                self.config['tests']['air_thr'] = config_cli.air_thr
            if config_cli.air_low is not None:
                self.config['tests']['air_low'] = config_cli.air_low
            if config_cli.air_high is not None:
                self.config['tests']['air_high'] = config_cli.air_high

            # operatione options
            if config_cli.mode is not None:
                self.config['options']['mode'] = config_cli.mode
            if config_cli.monitor_delay is not None:
                self.config['options']['monitor_delay'] = config_cli.monitor_delay
            if config_cli.monitor_loops is not None:
                self.config['options']['monitor_loops'] = config_cli.monitor_loops
            if config_cli.dutdelay is not None:
                self.config['options']['dutdelay'] = config_cli.dutdelay
            if config_cli.interactive is not None:
                self.config['options']['interactive'] = config_cli.interactive
            if config_cli.pairing is not None:
                self.config['options']['pairing'] = config_cli.pairing
            if config_cli.resetwifi is not None:
                self.config['options']['resetwifi'] = config_cli.resetwifi
            if config_cli.stop_if_failed is not None:
                self.config['options']['stop_if_failed'] = config_cli.stop_if_failed

            if config_cli.save_report is not None:
                self.config['report']['save_report'] = config_cli.save_report
            if config_cli.report_format is not None:
                self.config['report']['report_format'] = config_cli.report_format
            if config_cli.report_dest is not None:
                self.config['report']['report_dest'] = config_cli.report_dest
            if config_cli.report_path is not None:
                self.config['report']['report_path'] = config_cli.report_path

        return self.config

valid_modes = ['testbench', 'monitor', 'snonly', 'reset-wifi']

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments, including nested options for mqtt and MS Protocol."""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='My CLI App with Config File and Overrides',
                                     epilog='Priority: (lowest) defaults -> config file -> environment variables -> CLI options (highest)')

    # -------------------
    # General options
    # -------------------
    general_group = parser.add_argument_group("General Options")
    general_group.add_argument(
        '--config',
        type=str,
        dest='config',
        default='config.toml',
        help="Name of the configuration file, default is 'config.toml'"
    )
    general_group.add_argument(
        '--no-config',
        action='store_const',
        const='',
        dest='config',
        help="Do not use a configuration file (only defaults & options)"
    )
    general_group.add_argument(
        '-v',
        dest='version_option',
        action='store_true',
        default=False,
        help='Show version information of the module'
    )

    # -------------------
    # Logging options
    # -------------------
    logging_group = parser.add_argument_group("Logging Options")
    logging_group.add_argument(
        '--verbose',
        type=int,
        choices=[0, 1, 2, 3, 4, 5, 6],
        dest='verbose',
        help="Verbosity level: 0=CRITICAL, 1=ERROR, 2=WARNING, 3=QUIET, 4=INFO, 5=VERBOSE, 6=DEBUG. Default hardcoded is 3 or taken from config file/environment variable."
    )
    prefix_group = logging_group.add_mutually_exclusive_group()
    prefix_group.add_argument(
        "--log-prefix",
        action="store_const",
        const=True,
        dest="log_prefix",
        help="Enable log prefixes (timestamp, module, level)"
    )
    prefix_group.add_argument(
        "--no-log-prefix",
        action="store_const",
        const=False,
        dest="log_prefix",
        help="Disable log prefixes (print only the message)"
    )
    color_group = logging_group.add_mutually_exclusive_group()
    color_group.add_argument(
        "--use-color",
        action="store_const",
        const=True,
        dest="use_color",
        help="Enable colored log output"
    )
    color_group.add_argument(
        "--no-use-color",
        action="store_const",
        const=False,
        dest="use_color",
        help="Disable colored log output"
    )
    string_handler_group = logging_group.add_mutually_exclusive_group()
    string_handler_group.add_argument(
        "--use-string-handler",
        action="store_const",
        const=True,
        dest="use_string_handler",
        help="Enable string handler to store logs in an internal buffer"
    )
    string_handler_group.add_argument(
        "--no-use-string-handler",
        action="store_const",
        const=False,
        dest="use_string_handler",
        help="Disable string handler to store logs in an internal buffer"
    )
    exception_group = logging_group.add_mutually_exclusive_group()
    exception_group.add_argument(
        "--exc-full-stack",
        action="store_const",
        const=True,
        dest='exc_full_stack',
        help="Enable full stack logging for exceptions (useful for development and debugging)"
    )
    exception_group.add_argument(
        "--no-exc-full-stack",
        action="store_const",
        const=False,
        dest='exc_full_stack',
        help="Disable full stack logging for exceptions (useful for production)"
    )

    # application options & parameters
    # MQTT options
    mqtt_group = parser.add_argument_group('MQTT Options')
    mqtt_group.add_argument('--mqtt-host', type=str, help='MQTT host to connect to')
    mqtt_group.add_argument('--mqtt-port', type=int, help='MQTT port')
    mqtt_group.add_argument('--mqtt-username', type=str, help='MQTT username')
    mqtt_group.add_argument('--mqtt-password', type=str, help='MQTT password')
    mqtt_group.add_argument('--mqtt-client-id', type=str, help="MQTT Client ID, used by the broker")
    mqtt_group.add_argument("--mqtt-timeout", type=float, help="Timeout to wait connection or other activity in MQTT handler.")
    mqtt_group.add_argument("--mqtt-lp", type=int, dest='long_payload',
                            help="Determines threshold of long payloads. When they are longer that this value, a short string is logged instead of real payloads. --verbose makes real payloads to be logged always.")

    # ms protocol
    ms_group = parser.add_argument_group('MS Protocol Options')
    ms_group.add_argument("--ms-client_uuid", type=str, dest='ms_client_uuid', help="UUID of the client (master side).")
    ms_group.add_argument("--ms-server_uuid", type=str, dest='ms_server_uuid', help="UUID of the server (slave side).")
    ms_group.add_argument("--ms-cmd-topic", type=str, dest='ms_cmd_topic', help="Template of command topic.")
    ms_group.add_argument("--ms-rsp-topic", type=str, dest='ms_rsp_topic', help="Template of response topic.")
    ms_group.add_argument("--ms-timeout", type=float, dest='ms_timeout', help="Timeout used in protocol to wait for response.")

    # dut
    dut_group = parser.add_argument_group('DUT Data')
    dut_group.add_argument("--dut-ident", type=str, dest='dut_ident', help="ID Number of Device Under Test")
    dut_group.add_argument("--dut-name", type=str, dest='dut_name', help="Device name")
    dut_group.add_argument("--dut-serial-date", type=str, dest='dut_serial_date', help="Date as part of serial number")
    dut_group.add_argument("--dut-serialn", type=str, dest='dut_serialn', help="Serial number of the Device Under Test")
    dut_group.add_argument("--dut-sn-separator", type=str, dest='serial_separator', help="Separator string or symbol used to separate parts of the serial number")

    # tests
    tests_group = parser.add_argument_group('Tests Options')
    tests_group.add_argument("--motoron", type=float, dest='motoron', help="Time to maintain motor enabled in tests")
    tests_group.add_argument("--motoroff", type=float, dest='motoroff', help="Time to maintain motor disabled in tests")
    tests_group.add_argument("--heateron", type=float, dest='heateron', help="Time to maintain heater enabled in tests")
    tests_group.add_argument("--ionizeron", type=float, dest='ionizeron', help="Time to maintain ionizer enabled in tests")
    tests_group.add_argument("--repelleron", type=float, dest='repelleron', help="Time to maintain repeller enabled in tests")
    tests_group.add_argument("--buttontime", type=float, dest='buttontime', help="Time to wait for button and IR events in tests")

    tests_group.add_argument("--amb-thr", type=float, dest="amb_thr", help="Ambient light threshold (the lesser the darker)")
    tests_group.add_argument("--amb-low", type=float, dest="amb_low", help="Ambient light reasonable lowest value")
    tests_group.add_argument("--amb-high", type=float, dest="amb_high", help="Ambient light reasonable highest value")
    tests_group.add_argument("--co-thr", type=float, dest='co_thr', help="threshold")
    tests_group.add_argument("--co-low", type=float, dest='co_low', help="reasonable lowest value")
    tests_group.add_argument("--co-max", type=float, dest='co_high', help="reasonable highest value")
    tests_group.add_argument("--temp-thr", type=float, dest='temp_thr', help="threshold")
    tests_group.add_argument("--temp-low", type=float, dest='temp_low', help="reasonable lowest value")
    tests_group.add_argument("--temp-high", type=float, dest='temp_high', help="reasonable highest value")
    tests_group.add_argument("--press-thr", type=float, dest='press_thr', help="threshold")
    tests_group.add_argument("--press-low", type=float, dest='press_low', help="reasonable lowest value")
    tests_group.add_argument("--press-high", type=float, dest='press_high', help="reasonable highest value")
    tests_group.add_argument("--hum-thr", type=float, dest='hum_thr', help="threshold")
    tests_group.add_argument("--hum-low", type=float, dest='hum_low', help="reasonable lowest value")
    tests_group.add_argument("--hum-high", type=float, dest='hum_high', help="reasonable highest value")
    tests_group.add_argument("--air-thr", type=float, dest='air_thr', help="threshold")
    tests_group.add_argument("--air-low", type=float, dest='air_low', help="reasonable lowest value")
    tests_group.add_argument("--air-high", type=float, dest='air_high', help="reasonable highest value")

    # operative options
    operative_group = parser.add_argument_group('Operative Options')
    operative_group.add_argument('--mode', type=str, dest='mode', choices=valid_modes, help='Select mode of operation') # testbench, monitor, sn-only
    operative_group.add_argument("--monitor-delay", type=float, dest='monitor_delay', help="Interval of refreshing data in monitor mode")
    operative_group.add_argument("--monitor-loops", type=int, dest='monitor_loops', help="Number of loops in monitor mode")
    operative_group.add_argument("--dut-delay", type=float, dest='dutdelay',
                                 help="Delay after BLE pairing and connecting to MQTT before start of tests driven by MS protocol over MQTT. This time allows DUT to setup WiFi/MQTT connection.")
    interactive_group = operative_group.add_mutually_exclusive_group()
    interactive_group.add_argument('--interactive', dest='interactive', action='store_const', const=True, help='Enable interactive mode (default)')
    interactive_group.add_argument('--no-interactive', dest='interactive', action='store_const', const=False, help='Disable interactive mode')

    paring_group = operative_group.add_mutually_exclusive_group()
    paring_group.add_argument("--pairing", dest='pairing', action='store_const', const=True, help="Execute pairing procedure. Assumes DUT has no valid WiFi credentials.")
    paring_group.add_argument("--no-pairing", dest='pairing', action='store_const', const=False, help="Do not execute pairing procedure. Assumes DUT already has valid WiFi credentials.")

    reset_wifi_group = operative_group.add_mutually_exclusive_group()
    reset_wifi_group.add_argument("--reset-wifi", dest='resetwifi', action='store_const', const=True, help="Reset WiFi credentials on the DUT")
    reset_wifi_group.add_argument("--no-reset-wifi", dest='resetwifi', action='store_const', const=False, help="Do not reset WiFi credentials on the DUT")

    stop_if_failed_grop = operative_group.add_mutually_exclusive_group()
    stop_if_failed_grop.add_argument("--stop-if-failed", dest='stop_if_failed', action='store_const', const=True, help="Stop execution of tests if current test failed")
    stop_if_failed_grop.add_argument("--no-stop-if-failed", dest='stop_if_failed', action='store_const', const=False, help="Continue execution of tests even if current test failed")

    report_group = parser.add_argument_group('Report Options')
    report_save_group = report_group.add_mutually_exclusive_group()
    report_save_group.add_argument("--save-report", dest='save_report', action='store_const', const=True, help="Save test report into a file or a database")
    report_save_group.add_argument("--no-save-report", dest='save_report', action='store_const', const=False, help="Do not save test report")
    report_group.add_argument("--report-format", dest='report_format', choices=["json", "yaml"], help="Select output format for test report")
    report_group.add_argument("--report-dest", dest='report_dest', choices=["file", "db"], help="Select output destination for test report")
    report_group.add_argument("--report-path", dest='report_path', help="Select output path (directory) where reports are saved")

    return parser.parse_args()

def get_app_configuration() -> Config:
    """Get the application configuration.

    This function initializes the Config class, loads the configuration file,
    applies environment variable overrides, and returns the final configuration.

    Returns:
        ConfigDict: The final application configuration.
    """

    # Step 1: Create config object with default configuration
    config_instance = Config()

    # Step 2: Parse command-line arguments
    args = parse_args()
    if args.version_option:
        # If version option is requested, skip loading other configurations
        config_instance.config['logging']['version_option'] = True
        return config_instance

    # Step 3: Try to load configuration from configuration file
    config_file = args.config
    try:
        config_instance.load_config_file(config_file)
    except Exception as e:
        raise e

    # Step 4: Load config from environment variables (if set)
    try:
        config_instance.load_config_env()
    except Exception as e:
        raise e

    # Step 5: Merge default config, config.json, and command-line arguments
    config_instance.merge_cli_options(args)

    return config_instance
