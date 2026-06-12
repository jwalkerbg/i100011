# core/config.py

import os
import sys
from typing import Dict, Any, Mapping, TypedDict
import argparse
from jsonschema import validate, ValidationError

from pymodule.logger import get_app_logger

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

class ParametersConfig(TypedDict, total=False):
    param1: int
    param2: int

class PositionalsConfig(TypedDict, total=False):
    input_file: str
    output_file: str

class ConfigDict(TypedDict):
    template: TemplateConfig
    logging: LoggingConfig
    parameters: ParametersConfig
    positionals: PositionalsConfig

class Config:
    def __init__(self) -> None:
        self.config: ConfigDict = self.DEFAULT_CONFIG

    DEFAULT_CONFIG: ConfigDict = {
        'template': {
            'template_name': "pymodule",
            'template_version': "4.1.0",
            'template_description': { 'text': """Template with CLI interface, configuration options in a file, logger and unit tests""", 'content-type': "text/plain" }
        },
        'logging': {
            'verbose': 3,
            'log_prefix': True,
            'use_color': True,
            'use_string_handler': False,
            'version_option': False
        },
        'parameters': {
            'param1': 1,
            'param2': 2
        },
        'positionals': {
            'input_file': '',
            'output_file': ''
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
                    }
                },
                "additionalProperties": False
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "number"
                    },
                    "param2": {
                        "type": "number"
                    }
                },
                "additionalProperties": False
            },
            "positionals": {
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string"
                    },
                    "output_file": {
                        "type": "string"
                    }
                },
                "additionalProperties": False
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
            raise ValidationError(f"Configuration file validation error: {e}")
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
            "parameters": {
                "param1": os.getenv("PYMODULE_PARAM1"),
                "param2": os.getenv("PYMODULE_PARAM2")
            },
            "positionals": {
                "input_file": os.getenv("PYMODULE_INPUT_FILE"),
                "output_file": os.getenv("PYMODULE_OUTPUT_FILE")
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

            # sample parameters that should be changed in real applications
            if config_cli.param1 is not None:
                self.config['parameters']['param1'] = config_cli.param1
            if config_cli.param2 is not None:
                self.config['parameters']['param2'] = config_cli.param2

            # positional parameters
            if hasattr(config_cli, 'input_file') and config_cli.input_file is not None:
                self.config['positionals']['input_file'] = config_cli.input_file
            if hasattr(config_cli, 'output_file') and config_cli.output_file is not None:
                self.config['positionals']['output_file'] = config_cli.output_file

        return self.config

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments, including nested options for mqtt and MS Protocol."""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='My CLI App with Config File and Overrides', epilog='Priority: (lowest) defaults -> config file -> environment variables -> CLI options (highest)')

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


    # application options & parameters
    param_group = parser.add_argument_group("Parameters")
    param_group.add_argument('--param1', dest='param1', type=int, help="Parameter1")
    param_group.add_argument('--param2', dest='param2', type=int, help="Parameter2")

    positional_group = parser.add_argument_group("Parameters")
    positional_group.add_argument('input_file', type=str, nargs="?", help="Input file")
    positional_group.add_argument('output_file', type=str, nargs="?", help="Output file")

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
